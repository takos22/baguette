import json
import mimetypes
import re
import typing
import zlib

import aiofiles
import ujson

from .headers import Headers, make_headers
from .httpexceptions import HTTPException, NotFound
from .types import HeadersType, Result, Send
from .utils import safe_join

HTML_TAG_REGEX = re.compile(r"<\s*\w+[^>]*>.*?<\s*/\s*\w+\s*>")


class UJSONEncoder(json.JSONEncoder):
    encode = ujson.encode


class Response:
    """Base response class.

    Arguments
    ---------
        body : :class:`str` or :class:`bytes`
            The response body.

        status_code : :class:`int`
            The HTTP status code of the reponse.

        headers : :class:`list` of ``(str, str)`` tuples, \
        :class:`dict` or :class:`Headers`
            The headers of the reponse.

    Attributes
    ----------
        body : :class:`bytes`
            The raw response body.

        text : :class:`str`
            The response body.

        status_code : :class:`int`
            The HTTP status code of the reponse.

        headers : :class:`Headers`
            The headers of the reponse.
    """

    CHARSET = "utf-8"

    def __init__(
        self,
        body: typing.Union[str, bytes],
        status_code: int = 200,
        headers: typing.Optional[HeadersType] = None,
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
        self.headers = make_headers(headers)

    async def _send(self, send: Send):
        """Sends the response."""
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
    """JSON response class.

    Arguments
    ---------
        data : Anything JSON serializable
            The response body.

        status_code : :class:`int`
            The HTTP status code of the reponse.

        headers : :class:`list` of ``(str, str)`` tuples, \
        :class:`dict` or :class:`Headers`
            The headers of the reponse.

    Attributes
    ----------
        body : :class:`bytes`
            The raw response body.

        text : :class:`str`
            The response body.

        json : Anything JSON serializable
            The response JSON body.

        status_code : :class:`int`
            The HTTP status code of the reponse.

        headers : :class:`Headers`
            The headers of the reponse.

        JSON_ENCODER : JSON encoder
            The JSON encoder to use in :func:`json.dumps` with the ``cls``
            keyword argument. This is a class attribute.
            Default: the encoder from
            `ujson <https://github.com/ultrajson/ultrajson>`_
    """

    JSON_ENCODER = UJSONEncoder

    def __init__(
        self,
        data: typing.Any,
        status_code: int = 200,
        headers: typing.Optional[HeadersType] = None,
    ):
        self.json = data
        body: str = json.dumps(data, cls=self.JSON_ENCODER)
        super().__init__(body, status_code, headers)
        self.headers["content-type"] = "application/json"


class PlainTextResponse(Response):
    def __init__(
        self,
        text: typing.Union[str, bytes],
        status_code: int = 200,
        headers: typing.Optional[HeadersType] = None,
    ):
        super().__init__(text, status_code, headers)
        self.headers["content-type"] = "text/plain; charset=" + self.CHARSET


class HTMLResponse(Response):
    def __init__(
        self,
        html: typing.Union[str, bytes],
        status_code: int = 200,
        headers: typing.Optional[HeadersType] = None,
    ):
        super().__init__(html, status_code, headers)
        self.headers["content-type"] = "text/html; charset=" + self.CHARSET


class EmptyResponse(PlainTextResponse):
    def __init__(
        self,
        status_code: int = 204,
        headers: typing.Optional[HeadersType] = None,
    ):
        super().__init__("", status_code, headers)


class RedirectResponse(Response):
    def __init__(
        self,
        location: str,
        status_code: int = 301,
        headers: typing.Optional[HeadersType] = None,
    ):
        super().__init__("", status_code, headers)
        self.headers["location"] = location


class FileResponse(Response):
    def __init__(
        self,
        *paths,
        attachment_filename: typing.Optional[str] = None,
        mimetype: typing.Optional[str] = None,
        as_attachment: bool = False,
        add_etags: bool = True,
        status_code: int = 200,
        headers: typing.Optional[HeadersType] = None,
    ):
        self.mimetype = mimetype
        self.attachment_filename = attachment_filename
        self.headers = make_headers(headers)
        self.status_code = status_code

        self.file_path = safe_join(*paths)
        if not self.file_path.is_file():
            raise NotFound()

        self.file_size = self.file_path.stat().st_size
        self.headers["content-length"] = str(self.file_size)

        if self.attachment_filename is None:
            self.attachment_filename = self.file_path.name

        if self.mimetype is None and self.attachment_filename is not None:
            self.mimetype = (
                mimetypes.guess_type(self.attachment_filename)[0]
                or "application/octet-stream"
            )

        self.headers["content-type"] = self.mimetype

        if as_attachment:
            self.headers[
                "Content-Disposition"
            ] = f"attachment; filename={attachment_filename}"

        if add_etags:
            etag = "{}-{}-{}".format(
                self.file_path.stat().st_mtime,
                self.file_path.stat().st_size,
                zlib.adler32(bytes(self.file_path)),
            )
            self.headers["etag"] = etag

    async def _send(self, send):
        async with aiofiles.open(self.file_path, "rb") as f:
            file_body = await f.read()

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
                "body": file_body,
            }
        )


def make_response(result: Result) -> Response:
    """Makes a :class:`Response` object from a handler return value.

    Arguments
    ---------
        result: Anything described in :ref:`responses`
            The handler return value.

    Returns
    -------
        :class:`Response`
            The handler response.
    """

    if issubclass(type(result), Response):
        return result

    body = result
    status_code_or_headers = None
    status_code = None
    headers = None

    if isinstance(result, tuple):
        body, status_code_or_headers, headers = result + (None,) * (
            3 - len(result)
        )

    if isinstance(status_code_or_headers, int):
        status_code = status_code_or_headers
    elif isinstance(status_code_or_headers, (list, dict, Headers)):
        headers = status_code_or_headers

    headers = make_headers(headers)

    if not isinstance(body, (list, dict, str, bytes)) and body is not None:
        body = str(body)

    if isinstance(body, (list, dict)):
        response = JSONResponse(body, status_code or 200, headers)
    elif isinstance(body, (str, bytes)):
        if (
            HTML_TAG_REGEX.search(
                body.decode() if isinstance(body, bytes) else body
            )
            is not None
        ):
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

    return response


def make_error_response(
    http_exception: HTTPException,
    type_: str = "plain",
    include_description: bool = True,
    traceback: str = None,
) -> Response:
    """Convert an :class:`~baguette.httpexceptions.HTTPException` to a
    :class:`Response`.

    Arguments
    ---------
        http_exception: :class:`~baguette.httpexceptions.HTTPException`
            The HTTP exception to convert to a response.

        type_: :class:`str`
            Type of response. Must be one of: 'plain', 'json', 'html'.

        include_description: :class:`bool`
            Whether to include the description in the response.

        traceback: Optional[:class:`str`]
            Error traceback, usually only included in debug mode.

    Raises
    ------
        :exc:`ValueError`
            ``type_`` isn't one of: 'plain', 'json', 'html'.

    Returns
    -------
        :class:`Response`
            Response that describes the error.
    """

    if type_ == "plain":
        text = http_exception.name
        if include_description and http_exception.description:
            text += ": " + http_exception.description
        if traceback is not None:
            text += "\n" + traceback
        return PlainTextResponse(text, http_exception.status_code)

    elif type_ == "json":
        data = {
            "error": {
                "status": http_exception.status_code,
                "message": http_exception.name,
            }
        }
        if include_description and http_exception.description:
            data["error"]["description"] = http_exception.description
        if traceback is not None:
            data["error"]["traceback"] = traceback
        return JSONResponse(data, http_exception.status_code)

    elif type_ == "html":
        html = f"<h1>{http_exception.status_code} {http_exception.name}</h1>"
        if include_description and http_exception.description:
            html += f"\n<h2>{http_exception.description}</h2>"
        if traceback is not None:
            html += f"\n<pre><code>{traceback}</code></pre>"
        return HTMLResponse(html, http_exception.status_code)

    else:
        raise ValueError(
            "Bad response type. Must be one of: 'plain', 'json', 'html'"
        )


def redirect(
    location: str,
    status_code: int = 301,
    headers: typing.Optional[HeadersType] = None,
) -> RedirectResponse:
    """Redirect the request to location.

    Arguments
    ---------
        location: :class:`str`
            The location to redirect the request to.

        status_code: :class:`int`
            Status code of the redirect response.
            Default: ``301``.

        headers: anything accepted by :func:`make_headers`
            Headers to include in the response.
            Any location header will be overwritten with the location parameter.
            Default: ``None``.

    Returns
    -------
        :class:`RedirectResponse`
            The created redirect response.
    """
    return RedirectResponse(location, status_code, headers)
