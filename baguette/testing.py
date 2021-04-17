import typing
from collections.abc import Mapping, Sequence
from json import dumps
from urllib.parse import urlencode

from .app import Baguette
from .headers import Headers
from .request import Request
from .response import Response
from .types import Headers as HeadersType

ParamsType = typing.Union[
    str,
    typing.Mapping[str, typing.Union[str, typing.Sequence[str]]],
    typing.Sequence[typing.Tuple[str, typing.Union[str, typing.Sequence[str]]]],
]
BodyType = typing.Union[str, typing.Iterable[str], typing.AsyncIterator[str]]
JSONType = typing.Union[dict, list, tuple, str, int, float, bool]


class TestClient:
    def __init__(
        self,
        app: Baguette,
        default_headers: typing.Optional[HeadersType] = None,
    ):
        self.app = app
        self.default_headers = Headers()
        self.default_headers = self.prepare_headers(default_headers)

        self.default_scope = {
            "type": "http",
            "asgi": {"version": "3.0", "spec_version": "2.1"},
            "http_version": "1.1",
            "server": ("127.0.0.1", 8000),
            "client": ("127.0.0.1", 9000),
            "scheme": "http",
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
    ) -> Response:
        request = self.prepare_request(
            method=method,
            path=path,
            params=params,
            body=body,
            json=json,
            headers=headers,
        )
        response = await self.app.handle_request(request)
        return response

    def prepare_request(
        self,
        method: str,
        path: str,
        *,
        params: typing.Optional[ParamsType] = None,
        body: typing.Optional[BodyType] = None,
        json: typing.Optional[JSONType] = None,
        headers: typing.Optional[HeadersType] = None,
    ) -> Request:
        headers: Headers = self.prepare_headers(headers)
        querystring: str = self.prepare_querystring(params)
        scope = {
            **self.default_scope,
            **{
                "method": method.upper(),
                "path": path,
                "headers": headers.raw(),
                "query_string": querystring.encode("ascii"),
            },
        }

        request = Request(self.app, scope, None)
        request._body = self.prepare_body(body=body, json=json)

        return request

    def prepare_headers(
        self, headers: typing.Optional[HeadersType] = None
    ) -> Headers:
        if headers is None:
            headers = Headers()
        elif isinstance(headers, Sequence):
            headers = Headers(*headers)
        elif isinstance(headers, Mapping):
            headers = Headers(**headers)
        else:
            raise ValueError("Incorrect header type")

        headers = self.default_headers + headers
        return headers

    def prepare_querystring(
        self, params: typing.Optional[ParamsType] = None
    ) -> str:
        query = {}

        if params is None:
            return ""

        if isinstance(params, Mapping):
            params = list(params.items())

        if isinstance(params, Sequence):
            if any(len(param) != 2 for param in params):
                raise ValueError("Incorrect param type")

            for name, value in params:
                if isinstance(value, str):
                    values = [value]
                elif isinstance(value, Sequence):
                    values = list(value)
                else:
                    raise ValueError("Incorrect param type")

                if name in query:
                    query[name].extend(values)
                else:
                    query[name] = values

        else:
            raise ValueError("Incorrect param type")

        querystring = urlencode(query, doseq=True)

        return querystring

    def prepare_body(
        self,
        body: typing.Optional[BodyType] = None,
        json: typing.Optional[JSONType] = None,
    ) -> str:
        if body is None:
            if json is None:
                return ""
            else:
                body = dumps(json)
        return body
