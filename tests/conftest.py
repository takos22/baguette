import os
import shutil

import pytest

from baguette.app import Baguette
from baguette.headers import make_headers
from baguette.request import Request


class Send:
    def __init__(self):
        self.values = []

    async def __call__(self, message):
        self.values.append(message)


class Receive:
    def __init__(self, values: list = None):
        self.values = values or []

    async def __call__(self):
        return self.values.pop(0)


def create_http_scope(
    path: str = "/",
    method: str = "GET",
    headers={"server": "baguette", "content-type": "text/plain; charset=utf-8"},
    querystring: str = "a=b",
):
    return {
        "type": "http",
        "asgi": {"version": "3.0", "spec_version": "2.1"},
        "http_version": "1.1",
        "server": ("127.0.0.1", 8000),
        "client": ("127.0.0.1", 9000),
        "scheme": "http",
        "root_path": "",
        "method": method.upper(),
        "path": path,
        "headers": make_headers(headers).raw(),
        "query_string": querystring.encode("ascii"),
    }


@pytest.fixture(name="http_scope")
def create_http_scope_fixture():
    return create_http_scope()


def create_test_request(
    path: str = "/",
    method: str = "GET",
    headers={"server": "baguette", "content-type": "text/plain; charset=utf-8"},
    querystring: str = "a=b",
    body: str = "",
    json=None,
):
    request = Request(
        Baguette(),
        create_http_scope(
            path=path,
            method=method,
            headers=headers,
            querystring=querystring,
        ),
        Receive(),
    )
    request._body = body
    if json is not None:
        request._json = json

    return request


@pytest.fixture(name="test_request")
def create_test_request_fixture():
    return create_test_request()


@pytest.fixture(name="static_files", scope="session", autouse=True)
def create_static_files():
    os.mkdir("static")
    os.mkdir("static/css")
    os.mkdir("static/js")

    shutil.copy("docs/_static/images/banner.png", "static")

    with open("static/css/style.css", "w+") as f:
        f.write("h1 {\r\n  color: red;\r\n}\r\n")

    with open("static/js/script.js", "w+") as f:
        f.write("console.log('10'+1)\r\nconsole.log('10'-1)\r\n")

    yield None

    shutil.rmtree("static", ignore_errors=True)


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
