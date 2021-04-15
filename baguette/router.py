import typing

from .types import Handler

class Router:
    def __init__(self, app):
        self.app = app

    def add_route(
        self,
        handler: Handler,
        path: str,
        methods: typing.List[str] = None,
        name: str = None,
    ):
        pass
