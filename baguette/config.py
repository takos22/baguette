from .headers import Headers, make_headers
from .types import HeadersType


class Config:
    def __init__(
        self,
        debug: bool = False,
        default_headers: HeadersType = None,
        static_url_path: str = "static",
        static_directory: str = "static",
        templates_directory: str = "static",
        error_response_type: str = "plain",
        error_include_description: bool = True,
    ):
        self.debug = debug
        self.default_headers: Headers = make_headers(default_headers)

        self.static_url_path = static_url_path
        self.static_directory = static_directory
        self.templates_directory = templates_directory

        if error_response_type not in ("plain", "json", "html"):
            raise ValueError(
                "Bad response type. Must be one of: 'plain', 'json', 'html'"
            )
        self.error_response_type = error_response_type
        self.error_include_description = error_include_description or self.debug
