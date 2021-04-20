import cachetools
import re
import typing

from .converters import (
    Converter,
    FloatConverter,
    IntegerConverter,
    StringConverter,
)
from .httpexceptions import MethodNotAllowed, NotFound
from .types import Handler


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

        self.converters = {}
        self.build_converters()

        self.regex = r""
        self.build_regex()

    def build_converters(self):
        segments = self.path.strip("/").split("/")
        for index, segment in enumerate(segments):
            param = self.PARAM_REGEX.match(segment)
            if param is None:
                continue

            groups = param.groupdict()
            groups.setdefault("type", "str")
            groups.setdefault("args", "")

            if groups["type"] not in self.PARAM_CONVERTERS:
                raise ValueError(
                    "Expected type to be one of: {}. Got {}".format(
                        ", ".join(self.PARAM_CONVERTERS), groups["type"]
                    )
                )
            converter: Converter = self.PARAM_CONVERTERS[groups["type"]]

            args = self.PARAM_ARGS_REGEX.findall(groups["args"])
            kwargs = {}
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
        pass

    def match(self, path: str) -> bool:
        return self.regex.match(path)

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
        name = name or handler.__name__
        route = Route(path, name, handler, methods)
        self.routes.append(route)
        return route

    def get(self, path: str, method: str) -> Route:
        # TODO: regex matching
        route = self._cache.get(path)
        if route is None:
            for route in self.routes:
                if route.match(path):
                    break

            self._cache[path] = route

        if method not in route.methods:
            raise MethodNotAllowed()

        return route
