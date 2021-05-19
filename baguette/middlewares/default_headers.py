from ..config import Config
from ..request import Request
from ..responses import Response
from ..types import MiddlewareCallable


class DefaultHeadersMiddleware:
    def __init__(self, next_middleware: MiddlewareCallable, config: Config):
        self.next_middleware = next_middleware
        self.config = config

    async def __call__(self, request: Request) -> Response:
        response = await self.next_middleware(request)
        response.headers += self.config.default_headers
        return response
