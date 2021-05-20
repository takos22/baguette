import json
import typing
from cgi import parse_header
from urllib.parse import parse_qs

from .forms import Field, Form, MultipartForm, URLEncodedForm
from .headers import Headers
from .httpexceptions import BadRequest
from .types import ASGIApp, JSONType, Receive, Scope
from .utils import get_encoding_from_headers

FORM_CONTENT_TYPE = ["application/x-www-form-urlencoded", "multipart/form-data"]


class Request:
    """Request class that is passed to the view functions.

    Arguments
    ---------
        app: ASGI App
            The application that handles the request.

        scope: :class:`dict`
            ASGI scope of the request.
            See `HTTP scope ASGI specifications <https://asgi.readthedocs.io/\
            en/latest/specs/www.html#http-connection-scope>`_.

        receive: Asynchronous callable
            Awaitable callable that will yield a
            new event dictionary when one is available.
            See `applications ASGI specifications <https://asgi.readthedocs.io/\
            en/latest/specs/main.html#applications>`_.

    Attributes
    ----------
        app: ASGI App
            The application that handles the request.

        http_version: :class:`str`
            The HTTP version used.
            One of ``"1.0"``, ``"1.1"`` or ``"2"``.

        asgi_version: :class:`str`
            The ASGI specification version used.

        headers: :class:`Headers`
            The HTTP headers included in the request.

        method: :class:`str`
            The HTTP method name, uppercased.

        scheme: :class:`str`
            URL scheme portion (likely ``"http"`` or ``"https"``).

        path: :class:`str`
            HTTP request target excluding any query string,
            with percent-encoded sequences and UTF-8 byte sequences
            decoded into characters.
            ``"/"`` at the end of the path is striped.

        querystring: :class:`dict` with :class:`str` keys and \
        :class:`list` of :class:`str` values
            URL querystring decoded by :func:`urllib.parse.parse_qs`.

        server: :class:`tuple` of (:class:`str`, :class:`int`)
            Adress and port of the server.
            The first element can be the path to the UNIX socket running
            the application, in that case the second element is ``None``.

        client: :class:`tuple` of (:class:`str`, :class:`int`)
            Adress and port of the client.
            The adress can be either IPv4 or IPv6.

        content_type: :class:`str`
            Content type of the response body.

        encoding: :class:`str`
            Encoding of the response body.

    """

    def __init__(self, app: ASGIApp, scope: Scope, receive: Receive):
        self.app = app
        self._scope = scope
        self._receive = receive

        self.http_version: str = scope["http_version"]
        self.asgi_version: str = scope["asgi"]["version"]

        self.headers: Headers = Headers(*scope["headers"])
        self.method: str = scope["method"].upper()
        self.scheme: str = scope.get("scheme", "http")
        self.root_path: str = scope.get("root_path", "")
        self.path: str = scope["path"].rstrip("/") or "/"
        self.querystring: typing.Dict[str, typing.List[str]] = parse_qs(
            scope["query_string"].decode("ascii")
        )

        self.server: typing.Tuple[str, int] = scope["server"]
        self.client: typing.Tuple[str, int] = scope["client"]

        # common headers
        self.content_type: str = parse_header(
            self.headers.get("content-type", "")
        )[0]
        self.encoding: str = get_encoding_from_headers(self.headers) or "utf-8"

    async def raw_body(self) -> bytes:
        """Gets the raw request body in :class:`bytes`.

        Returns
        -------
            :class:`bytes`
                Raw request body.

        """

        # caching
        if hasattr(self, "_raw_body"):
            return self._raw_body

        body = b""
        more_body = True

        while more_body:
            message = await self._receive()
            body += message.get("body", b"")
            more_body = message.get("more_body", False)

        self._raw_body = body
        return self._raw_body

    async def body(self) -> str:
        """Gets the request body in :class:`str`.

        Returns
        -------
            :class:`str`
                Request body.

        """

        # caching
        if hasattr(self, "_body"):
            return self._body

        raw_body = await self.raw_body()
        self._body = raw_body.decode(self.encoding)
        return self._body

    async def json(self) -> JSONType:
        """Parses the request body to JSON.

        Returns
        -------
            Anything that can be decoded from JSON
                Parsed body.

        Raises
        ------
            ~baguette.httpexceptions.BadRequest
                If the JSON body is not JSON.
                You can usually not handle this error as it will be handled by
                the app and converted to a response with a ``400`` status code.

        """

        # caching
        if hasattr(self, "_json"):
            return self._json

        body = await self.body()
        try:
            self._json = json.loads(body)
        except json.JSONDecodeError:
            raise BadRequest(description="Can't decode body as JSON")
        return self._json

    async def form(self, include_querystring: bool = False) -> Form:
        """Parses the request body as form data.

        Arguments
        ---------
            include_querystring : Optional :class:`bool`
                Whether to include the querystrings in the form fields.

        Returns
        -------
            :class:`~baguette.forms.Form`
                Parsed form.

        """

        body = await self.raw_body()
        if self.content_type not in FORM_CONTENT_TYPE:
            raise ValueError(
                "Content-type '{}' isn't one of: {}".format(
                    self.content_type, ", ".join(FORM_CONTENT_TYPE)
                )
            )

        if self.content_type == "application/x-www-form-urlencoded":
            form = URLEncodedForm.parse(body, encoding=self.encoding)
        elif self.content_type == "multipart/form-data":
            params = parse_header(self.headers.get("content-type", ""))[1]
            form = MultipartForm.parse(
                body,
                boundary=params["boundary"].encode(self.encoding),
                encoding=self.encoding,
            )

        if include_querystring:
            for name, values in self.querystring.items():
                if name in form.fields:
                    form.fields[name].values.extend(values)
                else:
                    form.fields[name] = Field(name, values)

        return form
