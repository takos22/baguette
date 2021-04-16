import typing

from .httpexceptions import MethodNotAllowed
from .types import Handler


class View:
    METHODS = [
        "GET",
        "HEAD",
        "POST",
        "PUT",
        "DELETE",
        "CONNECT",
        "OPTIONS",
        "TRACE",
        "PATCH",
    ]

    def __init__(self, app):
        self.app = app
        self.methods: typing.List[str] = []
        for method in self.METHODS:
            if hasattr(self, method.lower()):
                self.methods.append(method)

    async def __call__(self, request):
        return await self.dispatch(request)

    async def dispatch(self, request):
        if not hasattr(self, request.method.lower()):
            raise MethodNotAllowed()
        handler: Handler = getattr(self, request.method.lower())
        return await handler(request)
