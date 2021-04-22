import inspect
import re
import traceback
import typing
from collections.abc import Mapping, Sequence

from .headers import Headers
from .httpexceptions import BadRequest, HTTPException
from .request import Request
from .responses import (
    EmptyResponse,
    HTMLResponse,
    JSONResponse,
    PlainTextResponse,
    Response,
)
from .router import Route, Router
from .types import Handler
from .types import Headers as HeaderType
from .types import Receive, Result, Scope, Send
from .view import View

HTML_TAG_REGEX = re.compile(r"<\s*\w+[^>]*>.*?<\s*/\s*\w+\s*>")


class Baguette:
    """Implements an ASGI application.

    This class is the main class for any application written with the baguette
    framework

    Parameters
    ----------
        debug: :class:`bool`
            Whether to run the application in debug mode.
            Default: ``False``.

        default_headers: :class:`list` of ``(str, str)`` tuples, \
        :class:`dict` or :class:`Headers`
            Default headers to include in every request.
            Default: No headers.

        error_response_type: :class:`str`
            Type of response to use in case of error.
            One of: ``"plain"``, ``"json"``, ``"html"``.
            Default: ``"plain"``.

        error_include_description: :class:`bool`
            Whether to include the error description in the response
            in case of error.
            If debug is ``True``, this will also be ``True``.
            Default: ``True``.


    Attributes
    ----------
        router: :class:`~baguette.router.Router`
            The URL router of the app.

        debug: :class:`bool`
            Whether the application is running in debug mode.

        default_headers: :class:`Headers`
            Default headers included in every request.

        error_response_type: :class:`str`
            Type of response to use in case of error.
            One of: ``"plain"``, ``"json"``, ``"html"``

        error_include_description: :class:`bool`
            Whether the error description is included in the response
            in case of error.
            If debug is ``True``, this will also be ``True``.
    """

    def __init__(
        self,
        *,
        debug: bool = False,
        default_headers: HeaderType = None,
        error_response_type: str = "plain",
        error_include_description: bool = True,
    ):
        self.router = Router()
        self.debug = debug
        self.default_headers = self.make_headers(default_headers)

        if error_response_type not in ("plain", "json", "html"):
            raise ValueError(
                "Bad response type. Must be one of: 'plain', 'json', 'html'"
            )

        self.error_response_type = error_response_type
        self.error_include_description = error_include_description or self.debug

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        """Entry point of the ASGI application."""

        assert scope["type"] == "http"
        request = Request(self, scope, receive)
        response = await self.handle_request(request)
        await response.send(send)

    async def handle_request(self, request: Request) -> Response:
        """Handles a request and returns a response.

        Parameters
        ----------
            request: :class:`Request`
                The request to handle.

        Returns
        -------
            :class:`Response`
                A response.
        """

        result = await self.dispatch(request)
        response = self.make_response(result)
        return response

    async def dispatch(self, request: Request) -> Result:
        """Dispatches a request to the correct handler and return its result.

        Parameters
        ----------
            request: :class:`Request`
                The request to handle.

        Returns
        -------
            Anything described in :ref:`responses`
                The handler function return value.
        """

        try:
            route: Route = self.router.get(request.path, request.method)
            handler: Handler = route.handler

            try:
                kwargs = route.convert(request.path)
            except ValueError:
                raise BadRequest(description="Failed to convert URL parameters")
            kwargs["request"] = request
            if not route.handler_is_class:
                kwargs = {
                    k: v for k, v in kwargs.items() if k in route.handler_kwargs
                }

            return await handler(**kwargs)

        except HTTPException as e:
            return e.response(
                type_=self.error_response_type,
                include_description=self.error_include_description,
                traceback="".join(traceback.format_tb(e.__traceback__))
                if self.debug
                else None,
            )

    def make_response(self, result: Result) -> Response:
        """Makes a :class:`Response` object from a handler return value.

        Parameters
        ----------
            result: Anything described in :ref:`responses`
                The handler return value.

        Returns
        -------
            :class:`Response`
                The handler response.
        """

        if issubclass(type(result), Response):
            return result

        if isinstance(result, tuple):
            body, status_code_or_headers, headers = result + (None,) * (
                3 - len(result)
            )
        else:
            body = result
            status_code_or_headers = None
            status_code = None
            headers = None

        if status_code_or_headers is None:
            status_code = None
        elif isinstance(status_code_or_headers, int):
            status_code = status_code_or_headers
        elif isinstance(status_code_or_headers, (list, dict, Headers)):
            headers = status_code_or_headers

        headers = self.make_headers(headers)
        headers += self.default_headers

        if isinstance(body, (list, dict)):
            response = JSONResponse(body, status_code or 200, headers)
        elif isinstance(body, str):
            if HTML_TAG_REGEX.search(body) is not None:
                response = HTMLResponse(body, status_code or 200, headers)
            else:
                response = PlainTextResponse(body, status_code or 200, headers)
        elif body is None:
            response = EmptyResponse(status_code or 204, headers)
            # print(
            #     RuntimeWarning(
            #         "The value returned by the view function shouldn't be None,"  # noqa: E501
            #         " but instead an empty string and a 204 status code or an EmptyResponse() instance"  # noqa: E501
            #     )
            # )
        else:
            response = PlainTextResponse(str(body), status_code or 200, headers)

        return response

    def make_headers(self, headers=None) -> Headers:
        """Makes a :class:`Headers` object from a :class:`list` of
        ``(str, str)`` tuples, a :class:`dict`, or a :class:`Headers` instance.

        Parameters
        ----------
            headers: :class:`list` of ``(str, str)`` tuples, \
            :class:`dict` or :class:`Headers`
                The raw headers to convert.

        Raises
        ------
            :exc:`ValueError`
                ``type_`` isn't one of: 'plain', 'json', 'html'.

        Returns
        -------
            :class:`Headers`
                The converted headers.
        """

        if headers is None:
            headers = Headers()
        elif isinstance(headers, Sequence):
            headers = Headers(*headers)
        elif isinstance(headers, (Mapping, Headers)):
            headers = Headers(**headers)
        else:
            raise ValueError(
                "headers must be a list, a dict, a Headers instance or None"
            )

        return headers

    def add_route(
        self,
        handler: Handler,
        path: str,
        methods: typing.List[str] = None,
        name: str = None,
    ) -> Route:
        """Adds a route to the application router.

        Parameters
        ----------
            handler: Async callable
                An asynchronous callable (function or class)
                that can handle a request.

            path: :class:`str`
                The path that the handler will handle.
                Can be dynamic, see :ref:`dynamic_routing`.

            methods: :class:`list` of :class:`str`
                Allowed methods for this path.
                Default: ``["GET", "HEAD"]``.

            name: :class:`str`
                Name of the route.
                Default: handler function name.

        Returns
        -------
            :class:`~baguette.router.Route`
                The created route.
        """

        return self.router.add_route(
            handler, path, methods or ["GET", "HEAD"], name
        )

    def route(
        self, path: str, methods: typing.List[str] = None, name: str = None
    ):
        """Adds the handler function to the router with the given path.

        Parameters
        ----------
            path: :class:`str`
                The path that the handler will handle.
                Can be dynamic, see :ref:`dynamic_routing`.

            methods: :class:`list` of :class:`str`
                Allowed methods for this path.
                Default: ``["GET", "HEAD"]``.

            name: :class:`str`
                Name of the route.
                Default: handler function name.
        """

        def decorator(func_or_class):
            if inspect.isclass(func_or_class) and issubclass(
                func_or_class, View
            ):
                handler: Handler = func_or_class(self)
                allowed_methods = handler.methods

            else:
                allowed_methods = methods or ["GET", "HEAD"]
                handler: Handler = func_or_class

            self.add_route(
                handler, path, allowed_methods, name or func_or_class.__name__
            )

            return func_or_class

        return decorator
