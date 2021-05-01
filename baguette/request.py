import json
import typing
from cgi import parse_header
from urllib.parse import parse_qs

from .forms import Field, Form, MultipartForm, URLEncodedForm
from .headers import Headers
from .httpexceptions import BadRequest
from .types import ASGIApp, JSONType, Receive, Scope
from .utils import get_encoding_from_headers

FORM_CONTENT_TYPE = ["application/x-www-form-urlencoded", "multipart/form-data"]


class Request:
    def __init__(self, app: ASGIApp, scope: Scope, receive: Receive):
        self.app = app
        self._scope = scope
        self._receive = receive

        self.http_version: str = scope["http_version"]
        self.asgi_version: str = scope["asgi"]["version"]

        self.headers: Headers = Headers(*scope["headers"])
        self.method: str = scope["method"].upper()
        self.scheme: str = scope["scheme"]
        self.root_path: str = scope["root_path"]
        self.path: str = scope["path"].rstrip("/") or "/"
        self.querystring: typing.Dict[str, typing.List[str]] = parse_qs(
            scope["query_string"].decode("ascii")
        )

        self.server: typing.Tuple[str, int] = scope["server"]
        self.client: typing.Tuple[str, int] = scope["client"]

        # common headers
        self.content_type: str = parse_header(
            self.headers.get("content-type", "")
        )[0]
        self.encoding: str = get_encoding_from_headers(self.headers) or "utf-8"

    async def raw_body(self) -> bytes:
        # caching
        if hasattr(self, "_raw_body"):
            return self._raw_body

        body = b""
        more_body = True

        while more_body:
            message = await self._receive()
            body += message.get("body", b"")
            more_body = message.get("more_body", False)

        self._raw_body = body
        return self._raw_body

    async def body(self) -> str:
        # caching
        if hasattr(self, "_body"):
            return self._body

        raw_body = await self.raw_body()
        self._body = raw_body.decode(self.encoding)
        return self._body

    async def json(self) -> JSONType:
        # caching
        if hasattr(self, "_json"):
            return self._json

        body = await self.body()
        try:
            self._json = json.loads(body)
        except json.JSONDecodeError:
            raise BadRequest(description="Can't decode body as JSON")
        return self._json

    async def form(self, include_querystring: bool = False) -> Form:
        body = await self.raw_body()
        if self.content_type not in FORM_CONTENT_TYPE:
            raise ValueError(
                "Content-type '{}' isn't one of: {}".format(
                    self.content_type, ", ".join(FORM_CONTENT_TYPE)
                )
            )

        if self.content_type == "application/x-www-form-urlencoded":
            form = URLEncodedForm.parse(body.decode(self.encoding))
        elif self.content_type == "multipart/form-data":
            params = parse_header(self.headers.get("content-type", ""))[1]
            form = MultipartForm.parse(
                body,
                boundary=params["boundary"].encode(self.encoding),
                encoding=self.encoding,
            )

        if include_querystring:
            for name, values in self.querystring:
                if name in form.fields:
                    form.fields[name].values.extend(values)
                else:
                    form.fields[name] = Field(name, values)

        return form
