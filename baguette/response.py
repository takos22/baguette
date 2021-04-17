import json
import typing

from .headers import Headers


class Response:
    CHARSET = "utf-8"

    def __init__(
        self,
        body: typing.Union[str, bytes],
        status_code: int = 200,
        headers: typing.Union[dict, Headers] = {},
    ):
        if type(body) == str:
            body = body.encode(self.CHARSET)
        self.body: bytes = body
        self.status_code = status_code
        self.headers = Headers(**headers)

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
        headers: typing.Union[dict, Headers] = {},
    ):
        body: str = json.dumps(data)
        headers["content-type"] = "application/json"
        super().__init__(body, status_code, headers)


class PlainTextResponse(Response):
    def __init__(
        self,
        text: typing.Union[str, bytes],
        status_code: int = 200,
        headers: typing.Union[dict, Headers] = {},
    ):
        headers["content-type"] = "text/plain; charset=" + self.CHARSET
        super().__init__(text, status_code, headers)


class HTMLResponse(Response):
    def __init__(
        self,
        html: typing.Union[str, bytes],
        status_code: int = 200,
        headers: typing.Union[dict, Headers] = {},
    ):
        headers["content-type"] = "text/html; charset=" + self.CHARSET
        super().__init__(html, status_code, headers)


class EmptyResponse(PlainTextResponse):
    def __init__(
        self,
        status_code: int = 204,
        headers: typing.Union[dict, Headers] = {},
    ):
        super().__init__("", status_code, headers)
