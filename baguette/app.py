import inspect
import traceback
import typing

from .headers import Headers, make_headers
from .httpexceptions import BadRequest, HTTPException
from .request import Request
from .responses import Response, make_response
from .router import Route, Router
from .types import Handler, Receive, Result, Scope, Send
from .view import View


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
        default_headers=None,
        error_response_type: str = "plain",
        error_include_description: bool = True,
    ):
        self.router = Router()
        self.debug = debug
        self.default_headers: Headers = make_headers(default_headers)

        if error_response_type not in ("plain", "json", "html"):
            raise ValueError(
                "Bad response type. Must be one of: 'plain', 'json', 'html'"
            )

        self.error_response_type = error_response_type
        self.error_include_description = error_include_description or self.debug

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        """Entry point of the ASGI application."""

        asgi_handlers = {
            "http": self._handle_http,
            "lifespan": self._handle_lifespan,
        }

        asgi_handler = asgi_handlers.get(scope["type"])
        if asgi_handler is None:
            raise NotImplementedError(
                "{0!r} scope is not supported".format(scope["type"])
            )

        await asgi_handler(scope, receive, send)

    async def _handle_http(self, scope: Scope, receive: Receive, send: Send):
        request = Request(self, scope, receive)
        response = await self.handle_request(request)
        await response.send(send)

    async def _handle_lifespan(
        self, scope: Scope, receive: Receive, send: Send
    ):
        while True:
            message = await receive()
            if message["type"] == "lifespan.startup":
                try:
                    await self.startup()
                except Exception as e:
                    await send(
                        {
                            "type": "lifespan.startup.failed",
                            "message": str(e),
                        }
                    )
                else:
                    await send({"type": "lifespan.startup.complete"})

            elif message["type"] == "lifespan.shutdown":
                try:
                    await self.shutdown()
                except Exception as e:
                    await send(
                        {
                            "type": "lifespan.shutdown.failed",
                            "message": str(e),
                        }
                    )
                else:
                    await send({"type": "lifespan.shutdown.complete"})

                return

    async def startup(self):
        pass

    async def shutdown(self):
        pass

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
        response = make_response(result)
        response.headers += self.default_headers
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

    def add_route(
        self,
        path: str,
        handler: Handler,
        methods: typing.List[str] = None,
        name: str = None,
        defaults: dict = None,
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
            path=path,
            name=name,
            handler=handler,
            methods=methods or ["GET", "HEAD"],
            defaults=defaults or {},
        )

    def route(
        self,
        path: str,
        methods: typing.List[str] = None,
        name: str = None,
        defaults: dict = None,
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

        .. versionchanged:: 0.0.3
            Renamed from ``Baguette.endpoint`` to :meth:`Baguette.route`

        """

        def decorator(func_or_class):
            if inspect.isclass(func_or_class) and issubclass(
                func_or_class, View
            ):
                handler: Handler = func_or_class(self)
                allowed_methods = handler.methods

            else:
                allowed_methods = methods
                handler: Handler = func_or_class

            self.add_route(
                path=path,
                name=name or func_or_class.__name__,
                handler=handler,
                methods=allowed_methods,
                defaults=defaults or {},
            )

            return func_or_class

        return decorator
