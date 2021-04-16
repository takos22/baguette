from json import dumps
import typing

from .app import Baguette
from .request import Request
from .headers import Headers
from .types import Headers as HeadersType

ParamsType = typing.Union[
    str, typing.Dict[str, str], typing.List[typing.Tuple[str, str]]
]
BodyType = typing.Union[str, typing.Iterable[str], typing.AsyncIterator[str]]
JSONType = typing.Union[dict, list, tuple, str, int, float, bool]


class TestClient:
    def __init__(self, app: Baguette, default_headers: HeadersType = {}):
        self.app = app
        if isinstance(default_headers, list):
            self.default_headers = Headers(*default_headers)
        else:
            self.default_headers = Headers(**default_headers)

        self.default_scope = {
            "type": "http",
            "asgi": {"version": "3.0", "spec_version": "2.1"},
            "http_version": "1.1",
            "server": ("127.0.0.1", 8000),
            "client": ("127.0.0.1", 9000),
            "root_path": "",
        }

    async def request(
        self,
        method: str,
        path: str,
        *,
        params: typing.Optional[ParamsType] = None,
        body: typing.Optional[BodyType] = None,
        json: typing.Optional[JSONType] = None,
        headers: typing.Optional[HeadersType] = None,
    ):
        headers = self.default_headers + headers
        scope = self.default_scope + {
            "method": method.upper(),
            "path": path,
        }
        if body is None and json is not None:
            body = dumps(json)

        request = Request(self.app, scope, None)
        request._body = body

        raise NotImplementedError()
