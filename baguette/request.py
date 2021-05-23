import copy
import json
import typing
from cgi import parse_header
from urllib.parse import parse_qs

from .forms import Field, Form, MultipartForm, URLEncodedForm
from .headers import Headers
from .httpexceptions import BadRequest
from .json import UJSONDecoder, UJSONEncoder
from .types import ASGIApp, JSONType, Receive, Scope, StrOrBytes
from .utils import get_encoding_from_headers, to_bytes, to_str

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

        # cached
        self._raw_body: bytes = None
        self._body: str = None
        self._json: JSONType = None
        self._form: Form = None

    # --------------------------------------------------------------------------
    # Body methods

    async def raw_body(self) -> bytes:
        """Gets the raw request body in :class:`bytes`.

        Returns
        -------
            :class:`bytes`
                Raw request body.
        """

        # caching
        if self._raw_body is not None:
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
        if self._body is not None:
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
        if self._json is not None:
            return self._json

        body = await self.body()
        try:
            self._json = json.loads(body, cls=UJSONDecoder)
        except (json.JSONDecodeError, ValueError):
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

        if self._form is None:
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

            self._form = form
        else:
            form = self._form.copy()

        if include_querystring:
            for name, values in self.querystring.items():
                if name in form.fields:
                    form.fields[name].values.extend(values)
                else:
                    form.fields[name] = Field(name, values)

        return form

    # --------------------------------------------------------------------------
    # Setters

    def set_raw_body(self, raw_body: bytes):
        """Sets the raw body of the request.

        Arguments
        ---------
            raw_body : :class:`bytes`
                The new request raw body

        Raises
        ------
            TypeError
                The raw body isn't of type :class:`bytes`
        """

        if not isinstance(raw_body, bytes):
            raise TypeError(
                "Argument raw_body most be of type bytes. Got "
                + raw_body.__class__.__name__
            )
        self._raw_body = raw_body

    def set_body(self, body: StrOrBytes):
        """Sets the request body.

        Parameters
        ----------
            body : :class:`str` or :class:`bytes`
                The new request body

        Raises
        ------
            TypeError
                The body isn't of type :class:`str` or :class:`bytes`
        """

        self._body = to_str(body)
        self.set_raw_body(to_bytes(body))

    def set_json(self, data: JSONType):
        """Sets the request JSON data.

        Parameters
        ----------
            data : Anything JSON serializable
                The data to put in the request body.

        Raises
        ------
            TypeError
                The data isn't JSON serializable.
        """

        self.set_body(json.dumps(data, cls=UJSONEncoder))
        self._json = copy.deepcopy(data)

    def set_form(self, form: Form):
        """Sets the request form.

        Parameters
        ----------
            form : :class:`~baguette.forms.Form`
                The form to add to the request.

        Raises
        ------
            TypeError
                The form isn't a :class:`~baguette.forms.Form`.
        """

        if not isinstance(form, Form):
            raise TypeError(
                "Argument form most be of type Form. Got "
                + form.__class__.__name__
            )
        self._form = form.copy()
