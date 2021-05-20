import inspect
import re
import typing

import cachetools

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


class Route:
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
        segments = self.path.strip("/").split("/")
        regex = ""

        for index, segment in enumerate(segments):
            regex += r"\/"
            if index in self.index_converters:
                name, converter = self.index_converters[index]
                regex += "(?P<{}>{})".format(name, converter.REGEX)

                if index == len(segments) - 1 and name in self.defaults:
                    regex += "?"

            else:
                regex += re.escape(segment)

        regex += r"\/?"

        self.regex = re.compile(regex)

    def match(self, path: str) -> bool:
        return self.regex.fullmatch(path if path.endswith("/") else path + "/")

    def convert(self, path: str) -> typing.Dict[str, typing.Any]:
        kwargs = self.defaults.copy()
        match = self.regex.fullmatch(path if path.endswith("/") else path + "/")

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
    def __init__(self, routes: typing.Optional[typing.List[Route]] = None):
        self.routes: typing.List[Route] = routes or []
        self._cache: typing.Mapping[str, Route] = cachetools.LFUCache(256)

    def add_route(
        self,
        handler: Handler,
        path: str,
        methods: typing.List[str] = None,
        name: str = None,
        defaults: dict = None,
    ) -> Route:
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
        route = self._cache.get(method + " " + path)
        if route is None:
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

        self._cache[method + " " + path] = route

        return route
