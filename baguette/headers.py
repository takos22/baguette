import itertools
import typing
from collections.abc import Mapping, Sequence


class Headers:
    def __init__(self, *args, **kwargs):
        self._headers: typing.Dict[str, str] = {}

        for name, value in itertools.chain(args, kwargs.items()):
            if isinstance(name, bytes):
                name = name.decode("ascii")
            if isinstance(value, bytes):
                value = value.decode("ascii")
            self._headers[name.lower()] = value

    def get(self, name, default=None):
        if isinstance(name, bytes):
            name = name.decode("ascii")
        return self._headers.get(name.lower(), default)

    def keys(self):
        return self._headers.keys()

    def items(self):
        return self._headers.items()

    def raw(self):
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
        if isinstance(name, bytes):
            name = name.decode("ascii")
        return self._headers[name.lower()]

    def __setitem__(self, name, value):
        if isinstance(name, bytes):
            name = name.decode("ascii")
        if isinstance(value, bytes):
            value = value.decode("ascii")
        self._headers[name.lower()] = value

    def __delitem__(self, name):
        if isinstance(name, bytes):
            name = name.decode("ascii")
        del self._headers[name.lower()]

    def __contains__(self, name):
        return name in self._headers

    def __add__(self, other: typing.Union["Headers", typing.Mapping[str, str]]):
        new = Headers(**self)
        new += other
        return new

    def __iadd__(
        self, other: typing.Union["Headers", typing.Mapping[str, str]]
    ):
        for name, value in other.items():
            if isinstance(name, bytes):
                name = name.decode("ascii")
            if isinstance(value, bytes):
                value = value.decode("ascii")
            self._headers[name.lower()] = value
        return self


def make_headers(headers=None) -> Headers:
    """Makes a :class:`Headers` object from a :class:`list` of
        ``(str, str)`` tuples, a :class:`dict`, or a :class:`Headers` instance.

        Parameters
        ----------
            headers: :class:`list` of ``(str, str)`` tuples, \
            :class:`dict` or :class:`Headers`
                The raw headers to convert.

        Raises
        ------
            :exc:`ValueError`
                ``type_`` isn't one of: 'plain', 'json', 'html'.

        Returns
        -------
            :class:`Headers`
                The converted headers.
        """

    if headers is None:
        headers = Headers()
    elif isinstance(headers, Sequence):
        headers = Headers(*headers)
    elif isinstance(headers, Mapping):
        headers = Headers(**headers)
    elif isinstance(headers, Headers):
        pass
    else:
        raise ValueError(
            "headers must be a list, a dict, a Headers instance or None"
        )

    return headers
