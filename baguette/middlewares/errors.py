import traceback

from ..httpexceptions import HTTPException, InternalServerError
from ..middleware import Middleware
from ..request import Request
from ..responses import Response, make_error_response


class ErrorMiddleware(Middleware):
    """Middleware to handle errors in request handling. Can be
    :exc:`~baguette.httpexceptions.HTTPException` or other exceptions.

    If :attr:`app.config.debug <baguette.Config.default_headers>` and the HTTP
    status code is higher than 500, then the error traceback is included.
    """

    async def __call__(self, request: Request) -> Response:
        try:
            return await self.next(request)

        except HTTPException as http_exception:
            return make_error_response(
                http_exception,
                type_=self.config.error_response_type,
                include_description=self.config.error_include_description,
                traceback="".join(
                    traceback.format_tb(http_exception.__traceback__)
                )
                if self.config.debug and http_exception.status_code >= 500
                else None,
            )

        except Exception as exception:
            traceback.print_exc()
            http_exception = InternalServerError()
            return make_error_response(
                http_exception,
                type_=self.config.error_response_type,
                include_description=self.config.error_include_description,
                traceback="".join(traceback.format_tb(exception.__traceback__))
                if self.config.debug
                else None,
            )
