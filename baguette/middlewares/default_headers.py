from ..middleware import Middleware
from ..request import Request
from ..responses import Response


class DefaultHeadersMiddleware(Middleware):
    async def __call__(self, request: Request) -> Response:
        response = await self.next(request)
        response.headers += self.config.default_headers
        return response
