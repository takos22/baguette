import itertools
import typing


class Headers:
    def __init__(self, *args, **kwargs):
        self._headers: typing.Dict[str, str] = {}

        for name, value in itertools.chain(args, kwargs.items()):
            if type(name) == bytes:
                name = name.decode("ascii")
            if type(value) == bytes:
                value = value.decode("ascii")
            self._headers[name.lower()] = value

    def get(self, name, default=None):
        if type(name) == bytes:
            name = name.decode("ascii")
        return self._headers.get(name.lower(), default)

    def keys(self):
        return self._headers.keys()

    def items(self):
        return self._headers.items()

    def raw(self):
        return [
            [name.encode("ascii"), value.encode("ascii")]
            for name, value in self.items()
        ]

    def __str__(self) -> str:
        return "\n".join(name + ": " + value for name, value in self.items())

    def __iter__(self):
        return iter(self._headers.items())

    def __getitem__(self, name):
        if type(name) == bytes:
            name = name.decode("ascii")
        return self._headers[name.lower()]

    def __setitem__(self, name, value):
        if type(name) == bytes:
            name = name.decode("ascii")
        if type(value) == bytes:
            value = value.decode("ascii")
        self._headers[name.lower()] = value

    def __delitem__(self, name):
        if type(name) == bytes:
            name = name.decode("ascii")
        del self._headers[name.lower()]

    def __contains__(self, name):
        return name in self._headers

    def __add__(self, other: typing.Union["Headers", typing.Mapping[str, str]]):
        return Headers(**self, **other)

    def __iadd__(
        self, other: typing.Union["Headers", typing.Mapping[str, str]]
    ):
        for name, value in other.items():
            if type(name) == bytes:
                name = name.decode("ascii")
            if type(value) == bytes:
                value = value.decode("ascii")
            self._headers[name.lower()] = value
        return self
