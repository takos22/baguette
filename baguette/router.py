import inspect
import re
import typing

import cachetools

from .converters import (
    Converter,
    FloatConverter,
    IntegerConverter,
    StringConverter,
)
from .httpexceptions import MethodNotAllowed, NotFound
from .types import Handler
from .view import View


class Route:
    PARAM_REGEX = re.compile(
        r"<(?P<name>\w+)(?::(?P<type>\w+)(?:\((?P<args>(?:\w+=\w+,?\s*)*)\))?)?>"  # noqa: E501
    )
    PARAM_ARGS_REGEX = re.compile(r"(\w+)=(\w+)")
    PARAM_CONVERTERS = {
        "str": StringConverter,
        "int": IntegerConverter,
        "float": FloatConverter,
    }

    def __init__(
        self,
        path: str,
        name: str,
        handler: Handler,
        methods: typing.List[str],
        defaults: typing.Dict[str, typing.Any] = {},
    ):
        self.path = path
        self.name = name
        self.handler = handler
        self.methods = methods
        self.defaults = defaults

        handler_signature = inspect.signature(self.handler)
        self.handler_kwargs = [
            param.name
            for param in handler_signature.parameters.values()
            if param.kind in (param.POSITIONAL_OR_KEYWORD, param.KEYWORD_ONLY)
        ]
        self.handler_is_class = isinstance(handler, View)

        self.converters = {}
        self.build_converters()

        self.regex = re.compile(path)
        self.build_regex()

    def build_converters(self):
        segments = self.path.strip("/").split("/")
        for index, segment in enumerate(segments):
            param = self.PARAM_REGEX.fullmatch(segment)
            if param is None:
                continue

            groups = param.groupdict()
            groups.setdefault("type", "str")

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
                        value = True if value == "True" else False
                    elif value.lstrip("+-").isdecimal():
                        value = int(value)
                    elif value.lstrip("+-").replace(".", "", 1).isdecimal():
                        value = float(value)
                    else:
                        value = value.strip("'\"")
                    kwargs[name] = value

            self.converters[index] = (groups["name"], converter(**kwargs))

    def build_regex(self):
        segments = self.path.strip("/").split("/")
        regex = r""
        for index, segment in enumerate(segments):
            regex += r"\/"
            if index in self.converters:
                regex += self.converters[index][1].REGEX
            else:
                regex += re.escape(segment)

        self.regex = re.compile(regex)

    def match(self, path: str) -> bool:
        return self.regex.fullmatch(path)

    def convert(self, path: str) -> typing.Dict[str, typing.Any]:
        kwargs = self.defaults.copy()
        segments = path.strip("/").split("/")

        for index, (name, converter) in self.converters.items():
            if index >= len(segments):
                if name in kwargs:
                    continue
                else:
                    raise ValueError(
                        f"{name} is a required value that is missing."
                    )

            segment = segments[index]
            try:
                kwargs[name] = converter.convert(segment)
            except ValueError as conversion_error:
                raise ValueError(
                    f"Failed to convert {name} argument: "
                    + str(conversion_error)
                ) from conversion_error

        return kwargs


class Router:
    def __init__(self, routes: typing.List[Route] = []):
        self.routes: typing.List[Route] = routes
        self._cache: typing.Mapping[str, Route] = cachetools.LFUCache(256)

    def add_route(
        self,
        handler: Handler,
        path: str,
        methods: typing.List[str] = None,
        name: str = None,
    ) -> Route:
        name = name
        route = Route(path, name, handler, methods)
        self.routes.append(route)
        return route

    def get(self, path: str, method: str) -> Route:
        route = self._cache.get(path)
        if route is None:
            for possible_route in self.routes:
                if possible_route.match(path):
                    route = possible_route
                    break

            if route is None:
                raise NotFound()

            self._cache[path] = route

        if method not in route.methods:
            raise MethodNotAllowed()

        return route
