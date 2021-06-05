import inspect
import re
import sys
import typing

from .converters import (
    Converter,
    FloatConverter,
    IntegerConverter,
    PathConverter,
    StringConverter,
)
from .httpexceptions import MethodNotAllowed, NotFound
from .types import Handler
from .view import View
from .websocket import Websocket

if sys.version_info == (3, 6):
    # python 3.6 doesn't include re.Match
    re.Match = type(re.compile("", 0).match(""))


class Route:
    """Class for storing info about a route and setting up converters."""

    PARAM_REGEX = re.compile(
        r"<(?P<name>\w+)(?::(?P<type>\w+)(?:\((?P<args>(?:\w+=(?:\w|\+|-|\.)+,?\s*)*)\))?)?>"  # noqa: E501
    )
    PARAM_ARGS_REGEX = re.compile(r"(\w+)=((?:\w|\+|-|\.)+)")
    PARAM_CONVERTERS = {
        "str": StringConverter,
        "path": PathConverter,
        "int": IntegerConverter,
        "float": FloatConverter,
    }

    def __init__(
        self,
        path: str,
        name: str,
        handler: Handler,
        methods: typing.List[str],
        defaults: typing.Dict[str, typing.Any] = None,
    ):
        """
        Parameters
        ----------
            path : :class:`str`
                The path that the route will be at.

            name : Optional :class:`str`
                The name of the route.

            handler : Async callable
                The function/class that handles requests.

            methods : :class:`list` of :class:`str`
                The methods that the route can handle.

            defaults : Optional :class:`dict`
                Default URL parameters to provide to the handler,
                if none in the URL.
        """

        self.path = path
        self.name = name
        self.handler = handler
        self.methods = methods
        self.defaults = defaults or {}

        handler_signature = inspect.signature(self.handler)
        self.handler_kwargs = [
            param.name
            for param in handler_signature.parameters.values()
            if param.kind in (param.POSITIONAL_OR_KEYWORD, param.KEYWORD_ONLY)
        ]
        self.handler_is_class = isinstance(self.handler, View)

        if self.name is None:
            self.name = (
                self.handler.__class__.__name__
                if self.handler_is_class
                else self.handler.__name__
            )

        self.converters = {}  # name: converter
        self.index_converters = {}  # index: (name, converter)
        self.build_converters()

        self.regex = re.compile("")
        self.build_regex()

    def build_converters(self):
        """Sets up converters for the route URL parameters.

        Raises
        ------
            :exc:`ValueError`
                The converter type isn't one of :attr:`PARAM_CONVERTERS`.
        """

        segments = self.path.strip("/").split("/")
        for index, segment in enumerate(segments):
            param = self.PARAM_REGEX.fullmatch(segment)
            if param is None:
                continue

            groups = param.groupdict()
            if groups["type"] is None:
                groups["type"] = "str"

            if groups["type"] not in self.PARAM_CONVERTERS:
                raise ValueError(
                    "Expected type to be one of: {}. Got {}".format(
                        ", ".join(self.PARAM_CONVERTERS), groups["type"]
                    )
                )
            converter: Converter = self.PARAM_CONVERTERS[groups["type"]]

            kwargs = {}
            if "args" in groups and groups["args"] is not None:
                args = self.PARAM_ARGS_REGEX.findall(groups["args"])
                for name, value in args:
                    if value in ["True", "False"]:
                        value = value == "True"
                    elif value.lstrip("+-").isdecimal():
                        value = int(value)
                    elif value.lstrip("+-").replace(".", "", 1).isdecimal():
                        value = float(value)
                    else:
                        value = value.strip("'\"")
                    kwargs[name] = value

            self.converters[groups["name"]] = converter(**kwargs)
            self.index_converters[index] = (groups["name"], converter(**kwargs))

    def build_regex(self):
        """Sets up the regex for route matching."""

        segments = self.path.strip("/").split("/")
        regex = ""

        for index, segment in enumerate(segments):
            regex += r"\/"
            if index in self.index_converters:
                name, converter = self.index_converters[index]
                regex += "(?P<{}>{})".format(name, converter.REGEX)

                if name in self.defaults:
                    regex += "?"

            else:
                regex += re.escape(segment)

        regex += r"\/?"

        self.regex = re.compile(regex)

    def match(self, path: str) -> typing.Optional[re.Match]:
        """Returns whether the path matches the route regex.

        Parameters
        ----------
            path : :class:`str`
                The path to test.

        Returns
        -------
            Optional :class:`re.Match`
                The match, or None if no match was found.
        """

        return self.regex.fullmatch(path)

    def convert(self, path: str) -> typing.Dict[str, typing.Any]:
        """Converts the URL parameters from the path.

        Parameters
        ----------
            path : :class:`str`
                The path that has the parameters.

        Returns
        -------
            :class:`dict`
                The converted parameters.

        Raises
        ------
            :exc:`ValueError`
                The path doesn't match the route regex.

            :exc:`ValueError`
                Failed a conversion
        """

        kwargs = self.defaults.copy()
        match = self.match(path if path.endswith("/") else path + "/")

        if match is None:
            raise ValueError("Path doesn't match router path")

        parameters = match.groupdict()

        for name, value in parameters.items():
            if value is None:
                if name in kwargs:
                    continue

            converter = self.converters[name]
            try:
                kwargs[name] = converter.convert(value)
            except ValueError as conversion_error:
                raise ValueError(
                    f"Failed to convert {name} argument: "
                    + str(conversion_error)
                ) from conversion_error

        return kwargs


class Router:
    """Class for routing a :class:`~baguette.Request` to the correct
    :class:`Route`."""

    def __init__(self, routes: typing.Optional[typing.List[Route]] = None):
        """
        Parameters
        ----------
            routes : Optional :class:`list` of :class:`Route`
                The routes to include directly.
        """

        self.routes: typing.List[Route] = routes or []

    def add_route(
        self,
        handler: Handler,
        path: str,
        methods: typing.List[str] = None,
        name: str = None,
        defaults: dict = None,
    ) -> Route:
        """Adds a route to the router.

        Parameters
        ----------
            handler : Async callable
                The function/class that handles requests.

            path : :class:`str`
                The path that the route will be at.

            methods : :class:`list` of :class:`str`
                The methods that the route can handle.

            name : Optional :class:`str`
                The name of the route.

            defaults : Optional :class:`dict`
                Default URL parameters to provide to the handler,
                if none in the URL.

        Returns
        -------
            :class:`Route`
                The added route.
        """

        route = Route(
            path=path,
            name=name,
            handler=handler,
            methods=methods,
            defaults=defaults or {},
        )
        self.routes.append(route)
        return route

    def get(self, path: str, method: str) -> Route:
        """Gets the route for a path and a method.

        Parameters
        ----------
            path : :class:`str`
                The path of the request.

            method :  :class:`str`
                The method of the request.

        Returns
        -------
            :class:`Route`
                The correct route.

        Raises
        ------
            :exc:`NotFound`
                No route was found with that path.
            :exc:`MethodNotAllowed`
                Method isn't allowed for that path.
        """

        route = None
        for possible_route in self.routes:
            if possible_route.match(path):
                route = possible_route
                if method not in route.methods:
                    continue
                break

        if route is None:
            raise NotFound()

        if method not in route.methods:
            raise MethodNotAllowed()

        return route


class WebsocketRoute:
    """Class for storing info about a websocket route."""

    def __init__(
        self,
        path: str,
        name: str,
        websocket: typing.Type[Websocket],
    ):
        self.path = path
        self.name = name or websocket.__name__
        self.websocket = websocket


class WebsocketRouter:
    """Class for routing a websocket connection to the correct
    :class:`Websocket`."""

    def __init__(
        self, routes: typing.Optional[typing.Dict[str, WebsocketRoute]] = None
    ):
        self.routes: typing.Dict[str, WebsocketRoute] = routes or {}

    def add_route(
        self,
        websocket: typing.Type[Websocket],
        path: str,
        name: str = None,
    ):
        route = WebsocketRoute(path, name, websocket)
        self.routes[path] = route
        return route

    def get(self, path: str) -> WebsocketRoute:
        if path not in self.routes:
            raise NotFound()

        return self.routes[path]
