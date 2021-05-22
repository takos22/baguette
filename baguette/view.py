import inspect
import typing

from .httpexceptions import MethodNotAllowed
from .request import Request
from .responses import Response
from .types import Handler

if typing.TYPE_CHECKING:
    from .app import Baguette


class View:
    """Base view class.

    Arguments
    ---------
        app : :class:`Baguette`
            The app that the view was added to.

    Attributes
    ----------
        app : :class:`Baguette`
            The app that the view was added to.

        methods : :class:`list` of :class:`str`
            The methods that this view can handle.
    """

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

    def __init__(self, app: "Baguette"):
        self.app: "Baguette" = app
        self.methods: typing.List[str] = []
        for method in self.METHODS:
            if hasattr(self, method.lower()):
                self.methods.append(method)

        self._methods_kwargs = {}
        for method in self.methods:
            handler_signature = inspect.signature(getattr(self, method.lower()))
            self._methods_kwargs[method] = [
                param.name
                for param in handler_signature.parameters.values()
                if param.kind
                in (param.POSITIONAL_OR_KEYWORD, param.KEYWORD_ONLY)
            ]

    async def __call__(self, request: Request, **kwargs) -> Response:
        return await self.dispatch(request, **kwargs)

    async def dispatch(self, request: Request, **kwargs) -> Response:
        """Dispatch the request to the right method handler."""

        if request.method not in self.methods:
            raise MethodNotAllowed()
        handler: Handler = getattr(self, request.method.lower())

        kwargs["request"] = request
        kwargs = {
            k: v
            for k, v in kwargs.items()
            if k in self._methods_kwargs[request.method]
        }

        return await handler(**kwargs)
