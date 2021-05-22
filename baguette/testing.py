import typing
from collections.abc import Mapping, Sequence
from urllib.parse import urlencode

from .app import Baguette
from .headers import Headers, make_headers
from .request import Request
from .responses import Response
from .types import BodyType, HeadersType, JSONType, ParamsType

METHOD_DOCS = """Sends a {method} request to :attr:`app`.

Arguments
---------
    path : :class:`str`
        The path of the request.

Keyword Arguments
-----------------
    params : :class:`str` or :class:`dict` with :class:`str` keys and \
    :class:`str` or :class:`list` values
        The parameters to send in the querystring.

    body : :class:`str` or :class:`bytes`
        The data to send in the request body.

    json : Anything JSON serializable
        The JSON data to send in the request body.

    headers : :class:`list` of ``(str, str)`` tuples, \
    :class:`dict` or :class:`Headers`
        The headers to send in the request.
"""


class TestClient:
    """Test client for a :class:`Baguette` application.

    This class works like a :class:`req:requests.Session`.

    Arguments
    ---------
        app : :class:`Baguette`
            Application tho send the test requests to.

        default_headers : :class:`list` of ``(str, str)`` tuples, \
        :class:`dict` or :class:`Headers`
            Default headers to include in every request.
            Default: No headers.

    Attributes
    ----------
        app : :class:`Baguette`
            Application tho send the test requests to.

        default_headers : :class:`list` of ``(str, str)`` tuples, \
        :class:`dict` or :class:`Headers`
            Default headers included in every request.
    """

    DEFAULT_SCOPE = {
        "type": "http",
        "asgi": {"version": "3.0", "spec_version": "2.1"},
        "http_version": "1.1",
        "server": ("127.0.0.1", 8000),
        "client": ("127.0.0.1", 9000),
        "scheme": "http",
        "root_path": "",
    }

    def __init__(
        self,
        app: Baguette,
        default_headers: typing.Optional[HeadersType] = None,
    ):
        self.app = app
        self.default_headers: Headers = make_headers(default_headers)

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
        """Creates and sends a request to :attr:`app`.

        Arguments
        ---------
            method : :class:`str`
                The HTTP method for the request.

            path : :class:`str`
                The path of the request.

        Keyword Arguments
        -----------------
            params : :class:`str` or :class:`dict` with :class:`str` keys and \
            :class:`str` or :class:`list` values
                The parameters to send in the querystring.

            body : :class:`str` or :class:`bytes`
                The data to send in the request body.

            json : Anything JSON serializable
                The JSON data to send in the request body.

            headers : :class:`list` of ``(str, str)`` tuples, \
            :class:`dict` or :class:`Headers`
                The headers to send in the request.
        """

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
            **self.DEFAULT_SCOPE,
            **{
                "method": method.upper(),
                "path": path,
                "headers": headers.raw(),
                "query_string": querystring.encode("ascii"),
            },
        }

        request = Request(self.app, scope, None)
        request.set_body(body or "")
        if json is not None:
            request.set_json(json)

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

    for method in [
        "GET",
        "HEAD",
        "POST",
        "PUT",
        "DELETE",
        "CONNECT",
        "OPTIONS",
        "TRACE",
        "PATCH",
    ]:
        locals().get(method.lower()).__doc__ = METHOD_DOCS.format(method=method)
