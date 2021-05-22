import inspect
import ssl
import typing

from . import rendering
from .config import Config
from .headers import make_headers
from .httpexceptions import BadRequest
from .middleware import Middleware
from .middlewares import DefaultHeadersMiddleware, ErrorMiddleware
from .request import Request
from .responses import FileResponse, Response, make_response
from .router import Route, Router
from .types import Handler, HeadersType, Receive, Result, Scope, Send
from .view import View


class Baguette:
    """Implements an ASGI application.

    This class is the main class for any application written with the baguette
    framework.

    Keyword Arguments
    -----------------
        config : :class:`Config`
            Config to use for the application.
            This replaces the other keyword arguments except ``middlewares``.
            Default: see :class:`Config` defaults.

        debug : :class:`bool`
            Whether to run the application in debug mode.
            Default: ``False``.

        default_headers : :class:`list` of ``(str, str)`` tuples, \
        :class:`dict` or :class:`Headers`
            Default headers to include in every response.
            Default: No headers.

        static_url_path : :class:`str`
            URL path for the static file handler.
            Default: ``"static"``.

        static_directory : :class:`str`
            Path to the folder containing static files.
            Default: ``"static"``.

        templates_directory : :class:`str`
            Path to the folder containing the HTML templates.
            Default: ``"templates"``.

        error_response_type : :class:`str`
            Type of response to use in case of error.
            One of: ``"plain"``, ``"json"``, ``"html"``.
            Default: ``"plain"``.

        error_include_description : :class:`bool`
            Whether to include the error description in the response
            in case of error.
            If debug is ``True``, this will also be ``True``.
            Default: ``True``.

        middlewares : :class:`list` of middleware classes
            The middlewares to add to the application.
            Default: ``[]``.

    Attributes
    ----------
        config : :class:`Config`
            The configuration of the app.

        router : :class:`~baguette.router.Router`
            The URL router of the app.

        renderer : :class:`~baguette.rendering.Renderer`
            Class that renders the templates.

        debug : :class:`bool`
            Whether the application is running in debug mode.

        default_headers : :class:`Headers`
            Default headers included in every response.

        static_url_path : :class:`str`
            URL path for the static file handler.

        static_directory : :class:`str`
            Path to the folder containing static files.

        templates_directory : :class:`str`
            Path to the folder containing the HTML templates.

        error_response_type : :class:`str`
            Type of response to use in case of error.
            One of: ``"plain"``, ``"json"``, ``"html"``

        error_include_description : :class:`bool`
            Whether the error description is included in the response
            in case of error.
            If debug is ``True``, this will also be ``True``.

        middlewares : :class:`list` of middlewares
            The middlewares of the application.
    """

    def __init__(
        self,
        *,
        config: Config = None,
        debug: bool = False,
        default_headers: HeadersType = None,
        static_url_path: str = "static",
        static_directory: str = "static",
        templates_directory: str = "static",
        error_response_type: str = "plain",
        error_include_description: bool = True,
        middlewares: typing.List[typing.Type[Middleware]] = [],
    ):
        self.router = Router()
        self.config = config or Config(
            debug=debug,
            default_headers=default_headers,
            static_url_path=static_url_path,
            static_directory=static_directory,
            templates_directory=templates_directory,
            error_response_type=error_response_type,
            error_include_description=error_include_description,
        )

        self.renderer = rendering.init(self.config.templates_directory)

        self.add_route(
            path=f"{self.config.static_url_path}/<filename:path>",
            handler=self.handle_static_file,
            name="static",
        )

        self.build_middlewares(
            [ErrorMiddleware, *middlewares, DefaultHeadersMiddleware]
        )

    def __getattr__(self, name):
        return getattr(self.config, name)

    # --------------------------------------------------------------------------
    # ASGI stuff

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
        """Handles rquests where ``scope["type"] == "http"``."""

        request = Request(self, scope, receive)
        response = await self.handle_request(request)
        await response._send(send)

    async def _handle_lifespan(
        self, scope: Scope, receive: Receive, send: Send
    ):
        """Handles rquests where ``scope["type"] == "lifespan"``."""

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

    # --------------------------------------------------------------------------
    # Lifespan

    async def startup(self):
        """Runs on application startup.

        This will be executed when you start the application.
        For example, you can connect to a database.

        .. versionadded:: 0.1.0
        """

    async def shutdown(self):
        """Runs on application shutdown.

        This will be executed when you stop the application.
        For example, you can disconnect from a database.


        .. versionadded:: 0.1.0
        """

    # --------------------------------------------------------------------------
    # HTTP

    async def handle_request(self, request: Request) -> Response:
        """Handles a request and returns a response.

        Arguments
        ---------
            request: :class:`Request`
                The request to handle.

        Returns
        -------
            :class:`Response`
                A response.
        """

        return await self.middlewares[0](request)

    async def dispatch(self, request: Request) -> Response:
        """Dispatches a request to the correct handler and return its result.

        Arguments
        ---------
            request: :class:`Request`
                The request to handle.

        Returns
        -------
            :class:`Response`
                The handler response.

        .. versionchanged:: 0.3.0
            The return value isn't the handler return value anymore, but instead
            a :class:`Response`.
        """

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

        result: Result = await handler(**kwargs)
        return make_response(result)

    # --------------------------------------------------------------------------
    # Routes

    def add_route(
        self,
        path: str,
        handler: Handler,
        methods: typing.List[str] = None,
        name: str = None,
        defaults: dict = None,
    ) -> Route:
        """Adds a route to the application router.

        Arguments
        ---------
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

            defaults: Optional :class:`dict`
                Default arguments to give to your handler.
                Default: ``{}``.

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
        """Decorator to add a handler function to the router with the given
        path.

        Arguments
        ---------
            path: :class:`str`
                The path that the handler will handle.
                Can be dynamic, see :ref:`dynamic_routing`.

            methods: Optional :class:`list` of :class:`str`
                Allowed methods for this path.
                Default: ``["GET", "HEAD"]``.

            name: Optional :class:`str`
                Name of the route.
                Default: handler function name.

            defaults: Optional :class:`dict`
                Default arguments to give to your handler.
                Default: ``{}``.

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

    # --------------------------------------------------------------------------
    # Middleware

    def build_middlewares(
        self, middlewares: typing.List[typing.Type[Middleware]] = []
    ):
        """Builds the middleware stack from a list of middleware classes.

        .. note::
            The first middleware in the list will be the first called on a
            request.

        .. seealso::
            There are middlewares included by default.
            See :ref:`default_middlewares`.

        Arguments
        ---------
            middlewares: :class:`list` of :class:`Middleware`
                The middlewares to add.

        .. versionadded:: 0.3.0
        """

        # first in the list, first called
        self._raw_middlewares = middlewares
        self.middlewares: typing.List[Middleware] = []

        last = self.dispatch
        for middleware in reversed(middlewares):
            last = middleware(last, self.config)
            self.middlewares.insert(0, last)

    def add_middleware(
        self, middleware: typing.Type[Middleware], index: int = 1
    ):
        """Adds a middleware to the middleware stack.

        Arguments
        ---------
            middleware: :class:`Middleware`
                The middleware to add.

            index: Optional :class:`int`
                The index to add the middlware to.
                Default: ``1`` (second middleware, called after
                :class:`~baguette.middlewares.ErrorMiddleware`)

        .. versionadded:: 0.3.0
        """

        middlewares = self._raw_middlewares.copy()
        middlewares.insert(index, middleware)
        self.build_middlewares(middlewares)

    def remove_middleware(self, middleware: typing.Type[Middleware]):
        """Removes a middleware from the middleware stack.

        Arguments
        ---------
            middleware: :class:`Middleware`
                The middleware to remove.

        .. versionadded:: 0.3.0
        """

        middlewares = self._raw_middlewares.copy()
        middlewares.remove(middleware)
        self.build_middlewares(middlewares)

    def middleware(
        self,
        index: int = 1,
    ):
        """Decorator to add a middleware to the app.

        Arguments
        ---------
            index: Optional :class:`int`
                The index to add the middlware to.
                Default: ``1`` (second middleware, called after
                :class:`~baguette.middlewares.ErrorMiddleware`)

        .. versionadded:: 0.3.0
        """

        def decorator(func_or_class):
            if inspect.isclass(func_or_class):
                middleware: typing.Type[Middleware] = func_or_class

            else:

                class middleware(Middleware):
                    async def __call__(self, request: Request) -> Response:
                        return await func_or_class(
                            self.next_middleware, request
                        )

            self.add_middleware(middleware, index)

            return middleware

        return decorator

    # --------------------------------------------------------------------------
    # Other methods

    async def handle_static_file(self, filename: str) -> FileResponse:
        return FileResponse(self.config.static_directory, filename)

    def run(
        self,
        *,
        host: str = "127.0.0.1",
        port: int = 8000,
        uds: str = None,
        fd: int = None,
        debug: bool = None,
        headers=None,
        loop: str = "auto",
        http: str = "auto",
        ws: str = "auto",
        env_file: str = None,
        log_config=None,
        log_level: str = None,
        access_log: bool = True,
        use_colors: bool = None,
        workers: int = None,
        proxy_headers: bool = True,
        forwarded_allow_ips: str = None,
        root_path: str = "",
        limit_concurrency: int = None,
        limit_max_requests: int = None,
        backlog: int = 2048,
        timeout_keep_alive: int = 5,
        timeout_notify: int = 30,
        callback_notify: typing.Callable = None,
        ssl_keyfile: str = None,
        ssl_certfile: str = None,
        ssl_keyfile_password: str = None,
        ssl_version: int = None,
        ssl_cert_reqs: int = ssl.CERT_NONE,
        ssl_ca_certs: str = None,
        ssl_ciphers: str = "TLSv1",
    ):
        """Runs the server with uvicorn.

        .. warning::
            You need ``uvicorn`` installed in order to use this.
            See :ref:`installing_asgi_server`.

        Keyword Arguments
        -----------------
            host: Optional :class:`str`
                Bind socket to this host.
                IPv6 addresses are supported.
                Default: ``127.0.0.1``

            port: Optional :class:`int`
                Bind to a socket with this port.
                Default: ``8000``.

            uds: Optional :class:`str`
                Bind to a UNIX domain socket.
                Default: ``None``.

            fd: Optional :class:`int`
                Bind to socket from this file descriptor.
                Default: ``None``.

            debug: Optional :class:`bool`
                Update the app.debug variable while the app is running.
                Default: ``None``.

            headers: Optional :class:`list` of ``(str, str)`` tuples, \
            :class:`dict` or :class:`Headers`
                Add headers to every response while the app is running.
                Default: ``None``.

            loop: Optional ``"auto"``, ``"asyncio"`` or ``"uvloop"``
                Event loop implementation. The uvloop implementation provides
                greater performance, but is not compatible with Windows or PyPy.
                Default: ``"auto"``

            http: Optional ``"auto"``, ``"h11"`` or ``"httptools"``
                HTTP protocol implementation. The httptools implementation
                provides greater performance, but it not compatible with PyPy,
                and requires compilation on Windows.
                Default: ``"auto"``

            ws: Optional ``"auto"``, ``"none"``, ``"websockets"`` \
            or ``"wsproto"``
                WebSocket protocol implementation. Either of the ``websockets``
                and ``wsproto`` packages are supported.
                Use ``"none"`` to deny all websocket requests.
                Default: ``"auto"``

            env_file: Optional :class:`str` (path to file)
                Environment configuration file. Loaded with
                `python-dotenv <https://pypi.org/project/python-dotenv/>`_
                Default: ``None``

            log_config: Optional :func:`~logging.config.dictConfig` formats, \
            ``.json`` and ``.yaml`` file paths or \
            :func:`~logging.config.fileConfig` formats.
                Logging configuration.
                Default: `uvicorn.config.LOGGING_CONFIG \
                <https://github.com/encode/uvicorn/blob/master/uvicorn/config.py#L68>`_

            log_level: ``"critical"``, ``"error"``, ``"warning"``, ``"info"``, \
            ``"debug"`` or ``"trace"``
                Application log level.
                Default: ``"info"``

            access_log: Optional :class:`bool`
                Whether to log every request.
                Default: ``True``

            use_colors: Optional :class:`bool`
                Whether to enable colorized formatting of the log records,
                in case this is not set it will be auto-detected.
                This option is ignored if  ``log_config`` is given.
                Default: ``None``

            workers: Optional :class:`int`
                Number of worker processes to use.
                Default: ``WEB_CONCURRENCY`` environment variable
                if available, or ``1``

            proxy_headers: Optional :class:`bool`
                Whether to enable ``X-Forwarded-Proto``, ``X-Forwarded-For`` and
                ``X-Forwarded-Port`` headers to populate remote address info.
                Restricted to only trusting connecting IPs in the
                ``forwarded_allow_ips`` parameter.
                Default: ``True``

            forwarded_allow_ips: Optional :class:`str`
                Comma separated list of IPs to trust with proxy headers.
                A wildcard ``"*"`` means always trust.
                Default: ``FORWARDED_ALLOW_IPS`` environment variable
                if available, or ``127.0.0.1``

            ssl_keyfile: Optional :class:`str` (path to file)
                SSL key file
                Default: ``None``

            ssl_certfile: Optional :class:`str` (path to file)
                SSL certificate file
                Default: ``None``

            ssl_keyfile_password: Optional :class:`str`
                Password to decrypt the ssl key
                Default: ``None``

            ssl_version: Optional :class:`int`
                SSL version to use. See :mod:`ssl` module.
                Default: :data:`ssl.PROTOCOL_TLS`

            ssl_cert_reqs: Optional :class:`int`
                Whether client certificate is required.
                One of :class:`ssl.VerifyMode` values,
                a constant of the :mod:`ssl` module that starts with ``CERT_``.
                Default: :data:`ssl.CERT_NONE`

            ssl_ca_certs: Optional :class:`str` (path to file)
                CA certificates file
                Default: ``None``

            ssl_ciphers: Optional :class:`str`
                Ciphers to use. See :mod:`ssl` module.
                Default: ``"TLSv1"``

        .. note::
            Doesn't support reloading, if you want reloading,
            run the application from the console with uvicorn
            and add the ``--reload`` flag.

        .. versionadded:: 0.1.2
        """

        try:
            import uvicorn
        except ModuleNotFoundError:  # pragma: no cover
            raise RuntimeError("Install uvicorn to use app.run()")

        last_debug = self.debug
        if isinstance(debug, bool):
            self.debug = debug

        last_default_headers = self.default_headers
        headers = make_headers(self.default_headers) + make_headers(headers)
        self.default_headers = headers

        log_config = log_config or uvicorn.config.LOGGING_CONFIG
        workers = workers or 1
        ssl_version = ssl_version or uvicorn.config.SSL_PROTOCOL_VERSION

        uvicorn.run(
            self,
            host=host,
            port=port,
            uds=uds,
            fd=fd,
            loop=loop,
            http=http,
            ws=ws,
            env_file=env_file,
            log_config=log_config,
            log_level=log_level,
            access_log=access_log,
            use_colors=use_colors,
            workers=workers,
            proxy_headers=proxy_headers,
            forwarded_allow_ips=forwarded_allow_ips,
            root_path=root_path,
            limit_concurrency=limit_concurrency,
            limit_max_requests=limit_max_requests,
            backlog=backlog,
            timeout_keep_alive=timeout_keep_alive,
            timeout_notify=timeout_notify,
            callback_notify=callback_notify,
            ssl_keyfile=ssl_keyfile,
            ssl_certfile=ssl_certfile,
            ssl_keyfile_password=ssl_keyfile_password,
            ssl_version=ssl_version,
            ssl_cert_reqs=ssl_cert_reqs,
            ssl_ca_certs=ssl_ca_certs,
            ssl_ciphers=ssl_ciphers,
        )

        self.debug = last_debug
        self.default_headers = last_default_headers
