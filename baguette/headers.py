import itertools


class Headers:
    def __init__(self, *args, **kwargs):
        self._headers = {}

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
