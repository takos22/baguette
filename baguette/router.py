import typing

from .httpexceptions import MethodNotAllowed, NotFound
from .types import Handler


class Route:
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


class Router:
    def __init__(self, routes: typing.List[Route] = []):
        self.routes: typing.List[Route] = routes
        self.paths = {route.path: route for route in self.routes}

    def add_route(
        self,
        handler: Handler,
        path: str,
        methods: typing.List[str] = None,
        name: str = None,
    ) -> Route:
        route = Route(path, name, handler, methods)
        self.routes.append(route)
        self.paths = {route.path: route for route in self.routes}
        return route

    def get(self, path: str, method: str) -> Route:
        if path not in self.paths:
            raise NotFound()
        route = self.paths[path]
        if method not in route.methods:
            raise MethodNotAllowed()
        return route
