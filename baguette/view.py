import inspect
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

        self.methods_kwargs = {}
        for method in self.methods:
            handler_signature = inspect.signature(getattr(self, method.lower()))
            self.methods_kwargs[method] = [
                param.name
                for param in handler_signature.parameters.values()
                if param.kind
                in (param.POSITIONAL_OR_KEYWORD, param.KEYWORD_ONLY)
            ]

    async def __call__(self, request, **kwargs):
        return await self.dispatch(request, **kwargs)

    async def dispatch(self, request, **kwargs):
        if not hasattr(self, request.method.lower()):
            raise MethodNotAllowed()
        handler: Handler = getattr(self, request.method.lower())

        kwargs["request"] = request
        kwargs = {
            k: v
            for k, v in kwargs.items()
            if k in self.methods_kwargs[request.method]
        }

        return await handler(**kwargs)
