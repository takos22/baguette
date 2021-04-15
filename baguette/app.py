import inspect
import functools
import re
import typing

from .headers import Headers
from .request import Request
from .response import (
    EmptyResponse,
    HTMLResponse,
    JSONResponse,
    PlainTextResponse,
    Response,
)
from .router import Router
from .types import Scope, Receive, Send, Result, Handler
from .view import View

HTML_TAG_REGEX = re.compile(r"<\s*\w+[^>]*>.*?<\s*/\s*\w+\s*>")


class Baguette:
    def __init__(self):
        self.router = Router(self)
        self.default_headers = Headers()

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        assert scope["type"] == "http"
        request = Request(self, scope, receive)
        result = await self.dispatch(request)
        response = self.make_response(result)
        await response.send(send)

    async def dispatch(self, request: Request) -> Result:
        path: str = request.path
        handler: Handler = self.router.get(path)
        return await handler(request)

    def make_response(self, result: Result) -> Response:
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
            print(
                RuntimeWarning(
                    "The value returned by the view function shouldn't be None,"
                    " but instead an empty string and a 204 status code."
                )
            )
        else:
            response = PlainTextResponse(str(body), status_code or 200, headers)

        return response

    def add_route(
        self,
        handler: Handler,
        path: str,
        methods: typing.List[str] = None,
        name: str = None,
    ):
        self.router.add_route(handler, path, methods, name)

    def route(
        self, path: str, methods: typing.List[str] = None, name: str = None
    ):
        def decorator(func_or_class):
            if inspect.isclass(func_or_class) and issubclass(
                func_or_class, View
            ):
                handler: Handler = func_or_class(self)
                allowed_methods = handler.methods
            else:
                allowed_methods = ["GET", "HEAD"]
                if methods is not None:
                    allowed_methods = methods.copy()

                @functools.wraps(func_or_class)
                async def handler(request: Request, *args, **kwargs) -> Result:
                    if request.method not in allowed_methods:
                        return await self.method_not_allowed(request)
                    return await func_or_class(request, *args, **kwargs)

            self.add_route(handler, path, allowed_methods, name)

            if inspect.isclass(func_or_class):
                return func_or_class
            else:
                return handler

        return decorator

    async def not_found(self, request):
        return "404: Not Found", 404

    async def method_not_allowed(self, request):
        return "405: Method Not Allowed", 405
