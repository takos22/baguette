from ..middleware import Middleware
from ..request import Request
from ..responses import Response


class DefaultHeadersMiddleware(Middleware):
    """Middleware to add the :attr:`app.config.default_headers
    <baguette.Config.default_headers>` to every response."""

    async def __call__(self, request: Request) -> Response:
        response = await self.next(request)
        response.headers = self.config.default_headers + response.headers
        return response
