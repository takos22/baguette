import pytest

from baguette.app import Baguette
from baguette.responses import PlainTextResponse

# need to change name to make sure pytest doesn't think this is a test class
from baguette.testing import TestClient as Client

from .conftest import create_test_request


@pytest.fixture(name="test_client")
def create_test_client():
    app = Baguette()

    @app.route(
        "/any/method",
        methods=[
            "GET",
            "HEAD",
            "POST",
            "PUT",
            "DELETE",
            "CONNECT",
            "OPTIONS",
            "TRACE",
            "PATCH",
        ],
    )
    async def any_method(request):
        return request.method

    return Client(app, default_headers={"server": "baguette"})


@pytest.mark.parametrize(
    ["params", "expected_querystring"],
    [
        [None, ""],
        ["", ""],
        ["a=b", "a=b"],
        [[("a", "b")], "a=b"],
        [[("a", "b"), ("a", "c"), ("b", "d")], "a=b&a=c&b=d"],
        [[("a", ["b", "c"]), ("b", "d")], "a=b&a=c&b=d"],
        [{"a": ["b", "c"], "b": "d"}, "a=b&a=c&b=d"],
        [{"a": [], "b": "d"}, "b=d"],
    ],
)
def test_test_client_prepare_querystring(
    test_client: Client, params, expected_querystring
):
    querystring = test_client._prepare_querystring(params)
    assert querystring == expected_querystring


@pytest.mark.parametrize(
    "params",
    [
        1,
        [["a", "b", "c"]],
        {"a": 1},
        {"a": [1, 2]},
    ],
)
def test_test_client_prepare_querystring_error(test_client: Client, params):
    with pytest.raises(ValueError):
        test_client._prepare_querystring(params)


@pytest.mark.parametrize(
    ["body", "json", "expected_body"],
    [
        [None, None, ""],
        [None, {"a": "b"}, '{"a": "b"}'],
        ["test", None, "test"],
        ["test", {"a": "b"}, "test"],
    ],
)
def test_test_client_prepare_body(
    test_client: Client, body, json, expected_body
):
    body = test_client._prepare_body(body, json)
    assert body == expected_body


def test_test_client_prepare_request(test_client: Client):
    request = test_client._prepare_request(
        method="GET",
        path="/",
        params={"a": "b"},
        body="Hello, World!",
        headers={"content-type": "text/plain; charset=utf-8"},
    )
    expected_request = create_test_request(body="Hello, World!")

    for attr in [
        "http_version",
        "asgi_version",
        "encoding",
        "method",
        "scheme",
        "root_path",
        "path",
        "querystring",
        "server",
        "client",
    ]:
        assert getattr(request, attr) == getattr(expected_request, attr)

    assert len(request.headers) == len(expected_request.headers)
    for name, value in request.headers:
        assert expected_request.headers[name] == value


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "method",
    [
        "GET",
        "HEAD",
        "POST",
        "PUT",
        "DELETE",
        "CONNECT",
        "OPTIONS",
        "TRACE",
        "PATCH",
    ],
)
async def test_test_client_request(test_client: Client, method: str):
    response = await test_client.request(method, "/any/method")
    assert isinstance(response, PlainTextResponse)
    assert response.text == method


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "method",
    [
        "GET",
        "HEAD",
        "POST",
        "PUT",
        "DELETE",
        "CONNECT",
        "OPTIONS",
        "TRACE",
        "PATCH",
    ],
)
async def test_test_client_request_method(test_client: Client, method: str):
    response = await getattr(test_client, method.lower())("/any/method")
    assert isinstance(response, PlainTextResponse)
    assert response.text == method
