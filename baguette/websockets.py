import typing
from urllib.parse import parse_qs

from .headers import Headers, make_headers
from .types import HeadersType, Receive, Scope, Send, StrOrBytes


class Websocket:
    def __init__(self, scope: Scope, receive: Receive, send: Send):
        self._scope = scope
        self._receive = receive
        self._send = send

        self.connected = False

        self.http_version: str = scope["http_version"]
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

    async def connect(self):
        message = await self._receive()
        try:
            assert message["type"] == "websocket.connect"
            await self.on_connect()
        except Exception:
            await self.close(403)
        else:
            await self.accept()

    async def accept(
        self, headers: HeadersType = None, subprotocol: str = None
    ):
        headers: Headers = make_headers(headers)
        await self._send(
            {
                "type": "websocket.accept",
                "headers": headers.raw(),
                "subprotocol": subprotocol,
            }
        )
        self.connected = True

    async def receive(self) -> StrOrBytes:
        message = await self._receive()

        type_ = message.pop("type")
        if type_ == "websocket.connect":
            raise RuntimeError("Call connect() method before receive()")
        elif type_ == "websocket.disconnect":
            return await self.on_disconnect(message["code"])

        message = message.get("bytes") or message["text"]
        await self.on_message(message)
        return message

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

    async def close(self, code: int = 1000):
        await self._send({"type": "websocket.close", "code": code})
        self.connected = False

    # --------------------------------------------------------------------------
    # Websocket events

    async def on_connect(self):
        pass

    async def on_message(self, message: StrOrBytes):
        pass

    async def on_disconnect(self, code: int):
        pass
