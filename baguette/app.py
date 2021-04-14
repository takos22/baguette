import inspect
import re
from typing import Any, Optional, Union, Tuple

from .headers import Headers
from .request import Request
from .response import (
    Response,
    JSONResponse,
    PlainTextResponse,
    HTMLResponse,
    EmptyResponse,
)
from .view import View


HTML_TAG_REGEX = re.compile(r"<\s*\w+[^>]*>.*?<\s*/\s*\w+\s*>")


class Baguette:
    def __init__(self):
        self.endpoints = {}
        self.default_headers = Headers(**{"server": "baguette"})

    async def __call__(self, scope, receive, send):
        assert scope["type"] == "http"
        request = Request(scope, receive)
        result = await self.dispatch(request)
        response = self.make_response(result)
        await response.send(send)

    async def dispatch(
        self, request: Request
    ) -> Union[
        Response,
        Tuple[
            Any,
            Optional[int],
            Optional[Union[Headers, dict, list]],
        ],
    ]:
        path = request.path
        handler = self.endpoints.get(path, self.not_found)
        return await handler(request)

    def make_response(self, result) -> Response:
        if issubclass(type(result), Response):
            return result

        if isinstance(result, tuple):
            body, status_code, headers = result + (None,) * (3 - len(result))
        else:
            body = result
            status_code = None
            headers = None

        if headers is None:
            headers = Headers()
        elif isinstance(headers, list):
            headers = Headers(*headers)
        elif isinstance(headers, (dict, Headers)):
            headers = Headers(**headers)
        else:
            raise ValueError(
                "headers must be a list, a dict, a Headers instance or None"
            )

        headers += self.default_headers

        if type(body) in (list, dict):
            response = JSONResponse(body, status_code or 200, headers)
        elif type(body) is str:
            if HTML_TAG_REGEX.search(body) is not None:
                response = HTMLResponse(body, status_code or 200, headers)
            else:
                response = PlainTextResponse(body, status_code or 200, headers)
        elif body is None:
            response = EmptyResponse(status_code or 204, headers)
        else:
            response = PlainTextResponse(str(body), status_code or 200, headers)

        return response

    async def not_found(self, request):
        return "404: Not Found", 404

    async def method_not_allowed(self, request):
        return "405: Method Not Allowed", 405

    def endpoint(self, path, methods=["GET", "HEAD"]):
        def decorator(func_or_class):
            if inspect.isclass(func_or_class) and issubclass(
                func_or_class, View
            ):
                endpoint = func_or_class(self)
                allowed_methods = endpoint.methods
            else:
                allowed_methods = methods.copy()

                async def endpoint(request, *args, **kwargs):
                    if request.method not in allowed_methods:
                        return await self.method_not_allowed(request)
                    return await func_or_class(request, *args, **kwargs)

            self.endpoints[path] = endpoint

            if inspect.isclass(func_or_class):
                return func_or_class
            else:
                return endpoint

        return decorator
