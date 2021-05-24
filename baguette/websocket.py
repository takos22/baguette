import asyncio
import typing
from urllib.parse import parse_qs

from .headers import Headers, make_headers
from .types import HeadersType, Receive, Scope, Send, StrOrBytes

if typing.TYPE_CHECKING:
    from .app import Baguette


class Websocket:
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
        message = await self._receive()
        if message["type"] != "websocket.connect":
            raise RuntimeError("Websocket already connected.")

        try:
            await self.on_connect()
        except Exception:
            await self.close(403, "Error in connection")
        else:
            await self.accept()
        finally:
            return self.accepted.is_set()

    async def accept(
        self, headers: HeadersType = None, subprotocol: str = None
    ):
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

    async def receive(self) -> StrOrBytes:
        return await self._message_queue.get()

    async def send(self, message: StrOrBytes):
        if isinstance(message, str):
            message = dict(text=message)

        elif isinstance(message, bytes):
            message = dict(bytes=message)

        else:
            raise TypeError(
                "message must be of type str, bytes or dict. Got: "
                + message.__class__.__name__
            )

        message["type"] = "websocket.send"
        await self._send(message)

    async def close(self, code: int = 1000, reason: str = ""):
        if not self.closed.is_set():
            await self._send(
                {"type": "websocket.close", "code": code, "reason": reason}
            )
            self.closed.set()
        else:
            raise RuntimeError("Websocket already closed.")

    async def handle_messages(self):
        while True:
            message = await self._receive()
            if message["type"] == "websocket.receive":
                message = message.get("bytes") or message.get("text")
                await self._message_queue.put(message)
                await self.on_message(message)
            elif message["type"] == "websocket.disconnect":
                self.closed.set()
                return await self.on_disconnect(message["code"])

    # --------------------------------------------------------------------------
    # Websocket events

    async def on_connect(self):
        pass

    async def on_message(self, message: StrOrBytes):
        pass

    async def on_disconnect(self, code: int):
        pass
