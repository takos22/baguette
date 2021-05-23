import typing
from .headers import Headers, make_headers
from .types import HeadersType, Scope, Receive, Send


class Message:
    def __init__(self, text: str = None, bytes_: bytes = None):
        if text is None and bytes_ is None:
            raise ValueError("Both text and bytes_ can't be None.")

        self.text = text
        self.bytes = bytes_

    def to_dict(self) -> dict:
        return dict(text=self.text, bytes=self.bytes)


class Websocket:
    def __init__(self, scope: Scope, receive: Receive, send: Send):
        self._scope = scope
        self._receive = receive
        self._send = send

        self.connected = False

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

    async def close(self, code: int = 1000):
        await self._send({"type": "websocket.close", "code": code})
        self.connected = False

    async def receive(self) -> Message:
        message = await self._receive()

        type_ = message.pop("type")
        if type_ == "websocket.connect":
            raise RuntimeError("Call connect() method before receive()")
        elif type_ == "websocket.disconnect":
            return await self.on_disconnect(message["code"])

        message = Message(**message)
        await self.on_message(message)
        return message

    async def send(self, message: typing.Union[dict, Message]):
        if isinstance(message, Message):
            message = message.to_dict()

        if not isinstance(message, dict):
            raise TypeError(
                "message must be of type Message. Got: "
                + message.__class__.__name__
            )

        message["type"] = "websocket.send"
        await self._send(message)

    async def on_connect(self):
        pass

    async def on_message(self, message: Message):
        pass

    async def on_disconnect(self, code: int):
        pass
