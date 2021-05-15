from ..config import Config
from ..request import Request
from ..responses import Response
from ..types import MiddlewareCallable


class DefaultHeadersMiddleware:
    def __init__(self, app: MiddlewareCallable, config: Config):
        self.app = app
        self.config = config

    async def __call__(self, request: Request) -> Response:
        response = await self.app(request)
        response.headers += self.config.default_headers
        return response
