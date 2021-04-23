import json
import re
import typing

from .headers import Headers, make_headers

HTML_TAG_REGEX = re.compile(r"<\s*\w+[^>]*>.*?<\s*/\s*\w+\s*>")


class Response:
    CHARSET = "utf-8"

    def __init__(
        self,
        body: typing.Union[str, bytes],
        status_code: int = 200,
        headers: typing.Union[dict, Headers] = None,
    ):
        if isinstance(body, str):
            self.text: str = body
            self.body: bytes = body.encode(self.CHARSET)
        elif isinstance(body, bytes):
            self.text: str = body.decode(self.CHARSET)
            self.body: bytes = body
        else:
            raise ValueError("body must be str or bytes")

        self.status_code = status_code
        self.headers = Headers(**(headers or {}))

    async def send(self, send):
        await send(
            {
                "type": "http.response.start",
                "status": self.status_code,
                "headers": self.headers.raw(),
            }
        )
        await send(
            {
                "type": "http.response.body",
                "body": self.body,
            }
        )


class JSONResponse(Response):
    def __init__(
        self,
        data: typing.Any,
        status_code: int = 200,
        headers: typing.Union[dict, Headers] = None,
    ):
        self.json = data
        body: str = json.dumps(data)
        headers = headers or {}
        headers["content-type"] = "application/json"
        super().__init__(body, status_code, headers)


class PlainTextResponse(Response):
    def __init__(
        self,
        text: typing.Union[str, bytes],
        status_code: int = 200,
        headers: typing.Union[dict, Headers] = None,
    ):
        headers = headers or {}
        headers["content-type"] = "text/plain; charset=" + self.CHARSET
        super().__init__(text, status_code, headers)


class HTMLResponse(Response):
    def __init__(
        self,
        html: typing.Union[str, bytes],
        status_code: int = 200,
        headers: typing.Union[dict, Headers] = None,
    ):
        headers = headers or {}
        headers["content-type"] = "text/html; charset=" + self.CHARSET
        super().__init__(html, status_code, headers)


class EmptyResponse(PlainTextResponse):
    def __init__(
        self,
        status_code: int = 204,
        headers: typing.Union[dict, Headers] = None,
    ):
        super().__init__("", status_code, headers)


Result = typing.Union[
    Response,
    typing.Tuple[
        typing.Any,
        typing.Optional[int],
        typing.Optional[Headers],
    ],
]


def make_response(result: Result) -> Response:
    """Makes a :class:`Response` object from a handler return value.

    Parameters
    ----------
        result: Anything described in :ref:`responses`
            The handler return value.

    Returns
    -------
        :class:`Response`
            The handler response.
    """

    if issubclass(type(result), Response):
        return result

    if isinstance(result, tuple):
        body, status_code_or_headers, headers = result + (None,) * (
            3 - len(result)
        )
    else:
        body = result
        status_code_or_headers = None
        status_code = None
        headers = None

    if status_code_or_headers is None:
        status_code = None
    elif isinstance(status_code_or_headers, int):
        status_code = status_code_or_headers
    elif isinstance(status_code_or_headers, (list, dict, Headers)):
        headers = status_code_or_headers
        status_code = None

    headers = make_headers(headers)

    if isinstance(body, (list, dict)):
        response = JSONResponse(body, status_code or 200, headers)
    elif isinstance(body, str):
        if HTML_TAG_REGEX.search(body) is not None:
            response = HTMLResponse(body, status_code or 200, headers)
        else:
            response = PlainTextResponse(body, status_code or 200, headers)
    elif body is None:
        response = EmptyResponse(status_code or 204, headers)
        # print(
        #     RuntimeWarning(
        #         "The value returned by the view function shouldn't be None,"  # noqa: E501
        #         " but instead an empty string and a 204 status code or an EmptyResponse() instance"  # noqa: E501
        #     )
        # )
    else:
        response = PlainTextResponse(str(body), status_code or 200, headers)

    return response
