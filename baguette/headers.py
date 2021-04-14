import itertools
from typing import Dict


class Headers:
    def __init__(self, *args, **kwargs):
        self._headers: Dict[str, str] = {}

        for name, value in itertools.chain(args, kwargs.items()):
            if type(name) == bytes:
                name = name.decode("utf-8")
            if type(value) == bytes:
                value = value.decode("utf-8")
            self._headers[name.lower()] = value

    def get(self, name, default=None):
        if type(name) == bytes:
            name = name.decode("utf-8")
        return self._headers.get(name.lower(), default)

    def keys(self):
        return self._headers.keys()

    def items(self):
        return self._headers.items()

    def raw(self):
        return [
            [name.encode("utf-8"), value.encode("utf-8")]
            for name, value in self.items()
        ]

    def __str__(self) -> str:
        return "\n".join(name + ": " + value for name, value in self.items())

    def __iter__(self):
        return iter(self._headers.items())

    def __getitem__(self, name):
        if type(name) == bytes:
            name = name.decode("utf-8")
        return self._headers[name.lower()]

    def __setitem__(self, name, value):
        if type(name) == bytes:
            name = name.decode("utf-8")
        if type(value) == bytes:
            value = value.decode("utf-8")
        self._headers[name.lower()] = value

    def __delitem__(self, name):
        if type(name) == bytes:
            name = name.decode("utf-8")
        del self._headers[name.lower()]

    def __contains__(self, name):
        return name in self._headers
