from .config import Config
from .request import Request
from .responses import Response


class Middleware:
    """Base class for middlewares."""

    def __init__(self, next_middleware: "Middleware", config: Config):
        self.next_middleware = self.next = next_middleware
        self.config = config

    async def __call__(self, request: "Request") -> "Response":
        return await self.next(request)  # pragma: no cover
