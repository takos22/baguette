import asyncio
import traceback
import typing
from urllib.parse import parse_qs

from .headers import Headers, make_headers
from .json import dumps
from .types import HeadersType, Receive, Scope, Send, StrOrBytes
from .utils import to_str
from .websocketexceptions import CloseServerError, WebsocketClose

if typing.TYPE_CHECKING:
    from .app import Baguette


class Websocket:
    """Base websocket class.

    You usually only need to overwrite the :meth:`on_connect`,
    :meth:`on_message`, :meth:`on_disconnect` and :meth:`on_close` when
    subclassing.
    """

    def __init__(
        self, app: "Baguette", scope: Scope, receive: Receive, send: Send
    ):
        self.app: "Baguette" = app
        self._scope: Scope = scope
        self._receive: Receive = receive
        self._send: Send = send
        self._message_queue: asyncio.Queue = asyncio.Queue()
        self.accepted: asyncio.Event = asyncio.Event()
        self.closed: asyncio.Event = asyncio.Event()

        self.asgi_version: str = scope["asgi"]["version"]

        self.headers: Headers = Headers(*scope["headers"])
        self.scheme: str = scope["scheme"]
        self.root_path: str = scope["root_path"]
        self.path: str = scope["path"].rstrip("/") or "/"
        self.querystring: typing.Dict[str, typing.List[str]] = parse_qs(
            scope["query_string"].decode("ascii")
        )

        self.server: typing.Tuple[str, int] = scope["server"]
        self.client: typing.Tuple[str, int] = scope["client"]
        self.subprotocols: typing.List[str] = scope["subprotocols"]

    # --------------------------------------------------------------------------
    # Websocket methods

    async def connect(self) -> bool:
        """Connects to the websocket.

        .. warning:: This method must be called before :meth:`handle_messages`.

        Returns
        -------
            :class:`bool`
                Whether the websocket is connected.

        Raises
        ------
            :exc:`RuntimeError`
                Websocket is already connected
        """

        message = await self._receive()
        if message["type"] != "websocket.connect":
            raise RuntimeError("Websocket already connected.")

        try:
            await self.on_connect()

        except WebsocketClose as close:
            await self.close(403, str(close))
            return False

        except Exception as error:
            await self.on_error("on_connect", error)

            reason = "Error in connection."
            if self.app.debug:
                reason = (
                    reason[:-1]
                    + ": "
                    + str(error)
                    + "\nTraceback (most recent call last):\n"
                    + "".join(traceback.format_tb(error.__traceback__))
                )
            await self.close(403, reason)
            return False

        else:
            await self.accept()

        finally:
            if self.accepted.is_set():
                # run the main loop
                async def wrapped_main():
                    while not self.closed.is_set():
                        await self.main()
                        await asyncio.sleep(0)  # release pool

                self._schedule_coro(wrapped_main, "main")
                return True
            return False

    async def accept(
        self, headers: HeadersType = None, subprotocol: str = None
    ):
        """Accepts the websocket connection.

        If you want to accept with your own headers or subprotocol, call this in
        :meth:`on_connect`. If you don't, it will be called in :meth:`connect`
        if :meth:`on_connect` doesn't error.

        Parameters
        ----------
            headers : :class:`list` of ``(str, str)`` tuples, \
            :class:`dict` or :class:`Headers`
                The headers to include in the accept message.
                Default: No headers.
            subprotocol : Optional :class:`str`
                The subprotocol to use in the websocket.
                Default: ``None``
        """

        if not self.accepted.is_set():
            headers: Headers = make_headers(headers)
            await self._send(
                {
                    "type": "websocket.accept",
                    "headers": headers.raw(),
                    "subprotocol": subprotocol,
                }
            )
            self.accepted.set()

    async def receive(self) -> str:
        """Receives a message from the websocket.

        .. note:: You don't need to call this method in :meth:`on_message`.

        Returns
        -------
            :class:`str`
                The received message
        """

        return to_str(await self._message_queue.get())

    async def send(self, message: StrOrBytes):
        """Sends a message to the websocket.

        Parameters
        ----------
            message : :class:`str` or :class:`bytes`
                The message to send to the websocket.

        Raises
        ------
            TypeError
                The message isn't of type :class:`str` or :class:`bytes`.
        """

        if isinstance(message, str):
            message = dict(text=message)

        elif isinstance(message, bytes):
            message = dict(bytes=message)

        else:
            raise TypeError(
                "message must be of type str or bytes. Got: "
                + message.__class__.__name__
            )

        message["type"] = "websocket.send"
        await self._send(message)

    async def send_json(self, data):
        await self.send(dumps(data))

    async def close(self, code: int = 1000, reason: str = ""):
        """Closes the websocket connection.

        Parameters
        ----------
            code : Optional :class:`int`
                The status code to close the websocket connection with.
                Default: ``1000``.
            reason : Optional :class:`str`
                The reason to close the websocket connection with.
                Default: ``""``.

        Raises
        ------
            :exc:`RuntimeError`
                The connection is already closed.
        """

        if not self.closed.is_set():
            await self._send(
                {"type": "websocket.close", "code": code, "reason": reason}
            )
            self.closed.set()
            self.dispatch("close", code, reason)
        else:
            raise RuntimeError("Websocket already closed.")

    async def handle_messages(self):
        """Handles the received messages, calls :meth:`on_message` and puts them
        in queue.

        Raises
        ------
            :exc:`RuntimeError`
                The websocket isn't connected.
        """

        while not self.closed.is_set():
            if not self.accepted.is_set():
                raise RuntimeError("Websocket not connected.")

            message = await self._receive()

            if message["type"] == "websocket.receive":
                message = message.get("bytes") or message.get("text")
                await self._message_queue.put(message)
                self.dispatch("message", message)

            elif message["type"] == "websocket.disconnect":
                self.closed.set()
                self.dispatch("disconnect", message["code"])

    async def _run_coro(
        self, coro: typing.Coroutine, event_name: str, *args, **kwargs
    ):
        """Runs a coroutine and catches errors."""

        try:
            await coro(*args, **kwargs)
        except WebsocketClose as close:
            await self.close(close.close_code, str(close))
        except Exception as error:
            await self.on_error(event_name, error, *args, **kwargs)

    def _schedule_coro(
        self, coro: typing.Coroutine, event_name: str, *args, **kwargs
    ) -> asyncio.Task:
        """Schedules a coroutine in an :class:`asyncio task <asyncio.Task>`."""

        wrapped = self._run_coro(coro, event_name, *args, **kwargs)
        return asyncio.create_task(wrapped)

    def dispatch(self, event: str, *args, **kwargs):
        """Dispatches an event to the correct handler."""

        method = "on_" + event

        try:
            coro = getattr(self, method)
        except AttributeError:
            pass
        else:
            self._schedule_coro(coro, method, *args, **kwargs)

    # --------------------------------------------------------------------------
    # Websocket events

    async def main(self):
        """Runs in a loop until the websocket is closed."""

    async def on_connect(self):
        """Called on websocket connection.

        If this function raises an exception, the websocket connection wont be
        accepted.
        """

    async def on_message(self, message: str):
        """Called on every websocket message.

        Parameters
        ----------
            message : :class:`str`
                The websocket message
        """

    async def on_disconnect(self, code: int):
        """Called on websocket disconnection.

        If the server closed the connection, this is called before
        :meth:`on_close`.

        Parameters
        ----------
            code : :class:`int`
                The websocket close status code.
        """

    async def on_close(self, code: int, reason: str):
        """Called when the websocket is closed by the server.

        Parameters
        ----------
            code : :class:`int`
                The websocket close status code.

            reason : :class:`str`
                The reason why the websocket is closed.
        """

    async def on_error(
        self, event_name: str, error: Exception, *args, **kwargs
    ):
        """Called when an event errors.

        Parameters
        ----------
            event_name : :class:`str`
                The event that raised the error.

            error : :class:`str`
                The error that was raised.

            *args : :class:`tuple`
                The arguments of the event.

            **kwargs : :class:`dict`
                The keyword arguments of the event.
        """

        if event_name not in ["on_connect", "on_disconnect", "on_close"]:
            close = CloseServerError(
                description=(
                    (f"Exception in {event_name}: " + str(error))
                    if self.app.debug
                    else "Internal server error while operating."
                )
            )
            await self.close(close.close_code, str(close))

        traceback.print_exc()
