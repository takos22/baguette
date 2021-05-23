import itertools
import typing
from collections.abc import Mapping, Sequence

from .types import HeadersType
from .utils import to_str


class Headers:
    """Headers implementation for handling :class:`str` or :class:`bytes` names
    and values.

    .. tip::
        Use :func:`make_headers` to easily make a header from a :class:`list` or
        a :class:`dict`.
    """

    def __init__(self, *args, **kwargs):
        self._headers: typing.Dict[str, str] = {}

        for name, value in itertools.chain(args, kwargs.items()):
            self[name] = value

    def get(self, name, default=None):
        """Gets a header from its name. If not found, returns ``default``.

        Arguments
        ---------
            name: :class:`str` or :class:`bytes`
                Name of the header to get.
            default: Optional anything
                Value to return if header not found.
                Default: ``None``

        Returns
        -------
            :class:`str`
                Header value if found.
            Anything
                ``default``'s value.
        """

        name = to_str(name, encoding="ascii")
        return self._headers.get(name.lower().strip(), default)

    def keys(self):
        """Returns an iterator over the headers names.

        Returns
        -------
            Iterator of :class:`str`
                Iterator over the headers names.
        """

        return self._headers.keys()

    def items(self):
        """Returns an iterator over the headers names and values.

        Returns
        -------
            Iterator of ``(name, value)`` :class:`tuple`
                Iterator over the headers names and values.
        """

        return self._headers.items()

    def raw(self):
        """Returns the raw headers, a :class:`list` of ``[name, value]`` where
        ``name`` and ``value`` are :class:`bytes`.

        Returns
        -------
            :class:`list` of ``[name, value]`` where ``name`` and ``value`` are\
            :class:`bytes`
                Raw headers for the ASGI response.
        """

        return [
            [name.encode("ascii"), value.encode("ascii")]
            for name, value in self
        ]

    def __str__(self) -> str:
        return "\n".join(name + ": " + value for name, value in self)

    def __iter__(self):
        return iter(self.items())

    def __len__(self):
        return len(self._headers)

    def __getitem__(self, name):
        name = to_str(name, encoding="ascii")
        return self._headers[name.lower().strip()]

    def __setitem__(self, name, value):
        name = to_str(name, encoding="ascii")
        value = to_str(value, encoding="ascii")
        self._headers[name.lower().strip()] = value.strip()

    def __delitem__(self, name):
        name = to_str(name, encoding="ascii")
        del self._headers[name.lower().strip()]

    def __contains__(self, name):
        name = to_str(name, encoding="ascii")
        return name.lower().strip() in self._headers

    def __add__(self, other: HeadersType):
        new = Headers(**self)
        new += other
        return new

    def __iadd__(self, other: HeadersType):
        other = make_headers(other)
        for name, value in other:
            self._headers[name] = value
        return self

    def __eq__(self, other: HeadersType) -> bool:
        other = make_headers(other)
        if len(self) != len(other):
            return False
        for name, value in self:
            if other[name] != value:
                return False
        return True


def make_headers(headers: HeadersType = None) -> Headers:
    """Makes a :class:`Headers` object from a :class:`list` of ``(str, str)``
    tuples, a :class:`dict`, or a :class:`Headers` instance.

    Arguments
    ---------
        headers: :class:`list` of ``(str, str)`` tuples, \
        :class:`dict` or :class:`Headers`
            The raw headers to convert.

    Raises
    ------
        :exc:`TypeError`
            ``headers`` isn't of type :class:`str`, :class:`list`,
            :class:`dict`, :class:`Headers` or :obj:`None`

    Returns
    -------
        :class:`Headers`
            The converted headers.
    """

    if headers is None:
        headers = Headers()
    elif isinstance(headers, (str, bytes)):
        headers = to_str(headers, encoding="ascii")
        headers = Headers(
            *[header.split(":") for header in headers.splitlines()]
        )
    elif isinstance(headers, Sequence):
        headers = Headers(*headers)
    elif isinstance(headers, (Mapping, Headers)):
        new_headers = Headers()
        for name, value in headers.items():
            new_headers[name] = value
        headers = new_headers
    else:
        raise TypeError(
            "headers must be a str, a list, a dict, a Headers instance or None"
        )

    return headers
