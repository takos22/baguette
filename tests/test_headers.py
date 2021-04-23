import pytest

from baguette.headers import Headers, make_headers


def test_create_headers():
    Headers()
    Headers(("Content-Type", "text/html"), (b"Server", b"baguette"))
    Headers(*[("Content-Type", "text/html"), (b"Server", b"baguette")])
    Headers(server="baguette")
    Headers(**{"Content-Type": "text/html", "Server": b"baguette"})


@pytest.fixture(name="headers")
def create_headers():
    return Headers(**{"Content-Type": "text/html", "Server": "baguette"})


def test_headers_get(headers: Headers):
    assert (
        headers.get("server")
        == headers.get("SERVER")
        == headers.get(b"server")
        == "baguette"
    )
    assert headers.get("baguette") is None
    assert headers.get("baguette", default="baguette") == "baguette"


def test_headers_raw(headers: Headers):
    assert isinstance(headers.raw(), list)
    for header in headers.raw():
        assert isinstance(header, list)
        assert len(header) == 2
        name, value = header
        assert isinstance(name, bytes)
        assert isinstance(value, bytes)


def test_headers_str(headers: Headers):
    assert len(str(headers).splitlines()) == len(headers)
    for line in str(headers).splitlines():
        assert len(line.split(": ")) == 2
        name, value = line.split(": ")
        assert headers[name] == value


def test_headers_getitem(headers: Headers):
    assert (
        headers["server"]
        == headers["SERVER"]
        == headers[b"server"]
        == "baguette"
    )

    with pytest.raises(KeyError):
        headers["baguette"]


@pytest.mark.parametrize("name", ["connection", "CONNECTION", b"connection"])
def test_headers_setitem(headers: Headers, name: str):
    headers[name] = (
        "Keep-Alive".encode("ascii")
        if isinstance(name, bytes)
        else "Keep-Alive"
    )
    assert headers["connection"] == "Keep-Alive"


@pytest.mark.parametrize("name", ["server", "SERVER", b"server"])
def test_headers_delitem(headers: Headers, name: str):
    del headers[name]
    assert "server" not in headers


@pytest.mark.parametrize(
    "other",
    [
        {"server": "uvicorn"},
        {"connection": "Keep-Alive"},
        {"CONNECTION": "Keep-Alive"},
        {b"connection": b"Keep-Alive"},
        Headers(connection="Keep-Alive"),
    ],
)
def test_headers_add(headers: Headers, other):
    new_headers = headers + other
    assert isinstance(new_headers, Headers)

    for name, value in headers.items():
        if name in other:
            continue
        assert new_headers[name] == value

    for name, value in other.items():
        if isinstance(value, bytes):
            value = value.decode("ascii")
        assert new_headers[name] == value


@pytest.mark.parametrize(
    "other",
    [
        {"server": "uvicorn"},
        {"connection": "Keep-Alive"},
        {"CONNECTION": "Keep-Alive"},
        {b"connection": b"Keep-Alive"},
        Headers(connection="Keep-Alive"),
    ],
)
def test_headers_iadd(headers: Headers, other):
    old_headers = Headers(**headers)
    headers += other
    assert isinstance(headers, Headers)

    for name, value in old_headers.items():
        if name in other:
            continue
        assert headers[name] == value

    for name, value in other.items():
        if isinstance(value, bytes):
            value = value.decode("ascii")
        assert headers[name] == value


@pytest.mark.parametrize(
    ["headers", "expected_headers"],
    [
        [None, Headers()],
        [[["server", "baguette"]], Headers(server="baguette")],
        [{"server": "baguette"}, Headers(server="baguette")],
        [Headers(server="baguette"), Headers(server="baguette")],
    ],
)
def test_make_headers(headers, expected_headers):
    headers = make_headers(headers)
    for name, value in expected_headers:
        assert headers[name] == value


def test_make_headers_error():
    with pytest.raises(ValueError):
        make_headers(1)
