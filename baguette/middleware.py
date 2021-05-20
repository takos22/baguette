from .config import Config
from .request import Request
from .responses import Response


class Middleware:
    """Base class for middlewares.

    Arguments
    ---------
        next_middleware : :class:`Middleware`
            The next middleware to call.

        config : :class:`Config`
            The application configuration.

    Attributes
    ----------
        next_middleware : :class:`Middleware`
            The next middleware to call.

        nexte : :class:`Middleware`
            The next middleware to call.
            (Alias for :attr:`next_middleware`)

        config : :class:`Config`
            The application configuration.
    """

    def __init__(self, next_middleware: "Middleware", config: Config):
        self.next_middleware = self.next = next_middleware
        self.config = config

    async def __call__(self, request: Request) -> Response:
        """Call the middleware, executed at every request.

        Arguments
        ---------
            request: :class:`Request`
                The request to handle.

        Returns
        -------
            :class:`Response`
                The handled response.
        """

        return await self.next(request)  # pragma: no cover
