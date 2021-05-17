import traceback

from ..config import Config
from ..httpexceptions import HTTPException, InternalServerError
from ..request import Request
from ..responses import Response, make_error_response
from ..types import MiddlewareCallable


class ErrorMiddleware:
    def __init__(self, app: MiddlewareCallable, config: Config):
        self.app = app
        self.config = config

    async def __call__(self, request: Request) -> Response:
        try:
            return await self.app(request)
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
