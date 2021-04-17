import json
import typing
from urllib.parse import parse_qs

from .headers import Headers
from .utils import get_encoding_from_headers


class Request:
    def __init__(self, app, scope, receive):
        self.app = app
        self._scope = scope
        self._receive = receive

        self.http_version: str = scope["http_version"]
        self.asgi_version: str = scope["asgi"]["version"]

        self.headers: Headers = Headers(*scope["headers"])
        self.encoding: str = get_encoding_from_headers(self.headers) or "utf-8"
        self.method: str = scope["method"]
        self.scheme: str = scope["scheme"]
        self.root_path: str = scope["root_path"]
        self.path: str = scope["path"].rstrip("/") or "/"
        self.querystring: typing.Dict[str, typing.List[str]] = parse_qs(
            scope["query_string"].decode("ascii")
        )

        self.server: typing.Tuple[str, int] = scope["server"]
        self.client: typing.Tuple[str, int] = scope["client"]

    async def body(self):
        # caching
        if hasattr(self, "_body"):
            return self._body

        body = b""
        more_body = True

        while more_body:
            message = await self._receive()
            body += message.get("body", b"")
            more_body = message.get("more_body", False)

        self._body = body.decode(self.encoding)
        return self._body

    async def json(self):
        # caching
        if hasattr(self, "_json"):
            return self._json

        body = await self.body()
        try:
            self._json = json.loads(body)
        except json.JSONDecodeError:
            raise ValueError("Can't decode body as JSON")
        return self._json
