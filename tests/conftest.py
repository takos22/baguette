import pytest

import baguette


@pytest.fixture(name="app")
async def app_test_client():
    from .app import app

    return baguette.testing.TestClient(app)


class Send:
    def __init__(self):
        self.values = []

    async def __call__(self, message):
        return self.values.append(message)


class Receive:
    def __init__(self, values: list = None):
        self.values = values or []

    async def __call__(self):
        return self.values.pop(0)


@pytest.fixture(name="scope")
def create_scope():
    return {
        "type": "http",
        "asgi": {"version": "3.0", "spec_version": "2.1"},
        "http_version": "1.1",
        "server": ("127.0.0.1", 8000),
        "client": ("127.0.0.1", 9000),
        "scheme": "http",
        "root_path": "",
        "method": "GET",
        "path": "/",
        "headers": [
            (b"Host", b"baguette"),
            (b"Content-Type", b"text/plain; charset=utf-8"),
        ],
        "query_string": b"a=b",
    }


@pytest.fixture(name="test_request")
def create_request(scope):
    from .app import app

    return baguette.Request(app, scope, Receive())


# modified verison of https://stackoverflow.com/a/9759329/12815996
def concreter(abcls):
    """Create a concrete class for testing from an ABC.
    >>> import abc
    >>> class Abstract(abc.ABC):
    ...     @abc.abstractmethod
    ...     def bar(self):
    ...        ...

    >>> c = concreter(Abstract)
    >>> c.__name__
    'dummy_concrete_Abstract'
    >>> c().bar()
    """
    if not hasattr(abcls, "__abstractmethods__"):
        return abcls

    new_dict = abcls.__dict__.copy()
    del new_dict["__abstractmethods__"]

    for abstractmethod in abcls.__abstractmethods__:
        method = abcls.__dict__[abstractmethod]
        method.__isabstractmethod__ = False
        new_dict[abstractmethod] = method

    # creates a new class, with the overriden ABCs:
    return type("dummy_concrete_" + abcls.__name__, (abcls,), new_dict)
