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
        r"{(?P<name>\w+)(?::(?P<type>\w+)(?:\((?P<args>(?:\w+=\w+,?\s*)*)\))?)?}"  # noqa: E501
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
    ):
        self.path = path
        self.name = name
        self.handler = handler
        self.methods = methods
        self.converters = {}
        self.build_converters()
        # TODO: make regex builder

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

            self.converters[index] = {
                "name": groups["name"],
                "converter": converter(**kwargs),
            }


class Router:
    def __init__(self, routes: typing.List[Route] = []):
        self.routes: typing.Dict[str, Route] = {
            route.name: route for route in routes
        }

    def add_route(
        self,
        handler: Handler,
        path: str,
        methods: typing.List[str] = None,
        name: str = None,
    ) -> Route:
        name = name or handler.__name__
        route = Route(path, name, handler, methods)
        self.routes[name] = route
        return route

    def get(self, path: str, method: str) -> Route:
        # TODO: regex matching
        # temp
        paths = {route.path: route.name for route in self.routes.values()}
        if path not in paths:
            raise NotFound()

        route = self.routes[paths[path]]
        if method not in route.methods:
            raise MethodNotAllowed()
        return route
