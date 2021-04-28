import typing
from collections.abc import Mapping, Sequence
from json import dumps
from urllib.parse import urlencode

from .app import Baguette
from .headers import Headers, make_headers
from .request import Request
from .responses import Response
from .types import BodyType, HeadersType, JSONType, ParamsType


class TestClient:
    def __init__(
        self,
        app: Baguette,
        default_headers: typing.Optional[HeadersType] = None,
    ):
        self.app = app
        self.default_headers: Headers = make_headers(default_headers)

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
        request = self._prepare_request(
            method=method,
            path=path,
            params=params,
            body=body,
            json=json,
            headers=headers,
        )
        response = await self.app.handle_request(request)
        return response

    async def get(
        self,
        path: str,
        *,
        params: typing.Optional[ParamsType] = None,
        body: typing.Optional[BodyType] = None,
        json: typing.Optional[JSONType] = None,
        headers: typing.Optional[HeadersType] = None,
    ) -> Response:
        return await self.request(
            method="GET",
            path=path,
            params=params,
            body=body,
            json=json,
            headers=headers,
        )

    async def head(
        self,
        path: str,
        *,
        params: typing.Optional[ParamsType] = None,
        body: typing.Optional[BodyType] = None,
        json: typing.Optional[JSONType] = None,
        headers: typing.Optional[HeadersType] = None,
    ) -> Response:
        return await self.request(
            method="HEAD",
            path=path,
            params=params,
            body=body,
            json=json,
            headers=headers,
        )

    async def post(
        self,
        path: str,
        *,
        params: typing.Optional[ParamsType] = None,
        body: typing.Optional[BodyType] = None,
        json: typing.Optional[JSONType] = None,
        headers: typing.Optional[HeadersType] = None,
    ) -> Response:
        return await self.request(
            method="POST",
            path=path,
            params=params,
            body=body,
            json=json,
            headers=headers,
        )

    async def put(
        self,
        path: str,
        *,
        params: typing.Optional[ParamsType] = None,
        body: typing.Optional[BodyType] = None,
        json: typing.Optional[JSONType] = None,
        headers: typing.Optional[HeadersType] = None,
    ) -> Response:
        return await self.request(
            method="PUT",
            path=path,
            params=params,
            body=body,
            json=json,
            headers=headers,
        )

    async def delete(
        self,
        path: str,
        *,
        params: typing.Optional[ParamsType] = None,
        body: typing.Optional[BodyType] = None,
        json: typing.Optional[JSONType] = None,
        headers: typing.Optional[HeadersType] = None,
    ) -> Response:
        return await self.request(
            method="DELETE",
            path=path,
            params=params,
            body=body,
            json=json,
            headers=headers,
        )

    async def connect(
        self,
        path: str,
        *,
        params: typing.Optional[ParamsType] = None,
        body: typing.Optional[BodyType] = None,
        json: typing.Optional[JSONType] = None,
        headers: typing.Optional[HeadersType] = None,
    ) -> Response:
        return await self.request(
            method="CONNECT",
            path=path,
            params=params,
            body=body,
            json=json,
            headers=headers,
        )

    async def options(
        self,
        path: str,
        *,
        params: typing.Optional[ParamsType] = None,
        body: typing.Optional[BodyType] = None,
        json: typing.Optional[JSONType] = None,
        headers: typing.Optional[HeadersType] = None,
    ) -> Response:
        return await self.request(
            method="OPTIONS",
            path=path,
            params=params,
            body=body,
            json=json,
            headers=headers,
        )

    async def trace(
        self,
        path: str,
        *,
        params: typing.Optional[ParamsType] = None,
        body: typing.Optional[BodyType] = None,
        json: typing.Optional[JSONType] = None,
        headers: typing.Optional[HeadersType] = None,
    ) -> Response:
        return await self.request(
            method="TRACE",
            path=path,
            params=params,
            body=body,
            json=json,
            headers=headers,
        )

    async def patch(
        self,
        path: str,
        *,
        params: typing.Optional[ParamsType] = None,
        body: typing.Optional[BodyType] = None,
        json: typing.Optional[JSONType] = None,
        headers: typing.Optional[HeadersType] = None,
    ) -> Response:
        return await self.request(
            method="PATCH",
            path=path,
            params=params,
            body=body,
            json=json,
            headers=headers,
        )

    def _prepare_request(
        self,
        method: str,
        path: str,
        *,
        params: typing.Optional[ParamsType] = None,
        body: typing.Optional[BodyType] = None,
        json: typing.Optional[JSONType] = None,
        headers: typing.Optional[HeadersType] = None,
    ) -> Request:
        headers: Headers = self._prepare_headers(headers)
        querystring: str = self._prepare_querystring(params)
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
        request._body = self._prepare_body(body=body, json=json)

        return request

    def _prepare_headers(
        self, headers: typing.Optional[HeadersType] = None
    ) -> Headers:
        headers = make_headers(headers)
        headers = self.default_headers + headers

        return headers

    def _prepare_querystring(
        self, params: typing.Optional[ParamsType] = None
    ) -> str:
        query = {}

        if params is None or isinstance(params, str):
            return params or ""

        if isinstance(params, Mapping):
            params = list(params.items())

        if isinstance(params, Sequence):
            if any(len(param) != 2 for param in params):
                raise ValueError("Incorrect param type")

            for name, value in params:
                if isinstance(value, str):
                    values = [value]
                elif isinstance(value, Sequence):
                    if not all(isinstance(v, str) for v in value):
                        raise ValueError("Incorrect param type")
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

    def _prepare_body(
        self,
        body: typing.Optional[BodyType] = None,
        json: typing.Optional[JSONType] = None,
    ) -> str:
        if body is None:
            if json is None:
                return ""

            body = dumps(json)
        return body
