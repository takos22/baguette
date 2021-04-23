import pytest

from baguette.headers import Headers
from baguette.responses import (
    EmptyResponse,
    HTMLResponse,
    JSONResponse,
    PlainTextResponse,
    Response,
    make_response,
)

from .conftest import Send


def test_response_create():
    response = Response(
        "Hello, World!",
        headers={"content_type": "text/plain"},
    )
    assert isinstance(response.text, str)
    assert isinstance(response.body, bytes)
    assert isinstance(response.headers, Headers)

    response = Response(
        b"Hello, World!",
        headers={"content_type": "text/plain"},
    )
    assert isinstance(response.text, str)
    assert isinstance(response.body, bytes)
    assert isinstance(response.headers, Headers)

    with pytest.raises(ValueError):
        response = Response({"message": "This won't work"})


def test_json_response_create():
    response = JSONResponse({"message": "Hello, World!"})
    assert isinstance(response.json, dict)
    assert isinstance(response.text, str)
    assert isinstance(response.body, bytes)
    assert isinstance(response.headers, Headers)
    assert (
        "content-type" in response.headers
        and response.headers["content-type"] == "application/json"
    )


def test_plain_text_response_create():
    response = PlainTextResponse("Hello, World!")
    assert isinstance(response.text, str)
    assert isinstance(response.body, bytes)
    assert isinstance(response.headers, Headers)
    assert "content-type" in response.headers and response.headers[
        "content-type"
    ].startswith("text/plain")


def test_html_response_create():
    response = HTMLResponse("<h1>Hello, World!</h1>")
    assert isinstance(response.text, str)
    assert isinstance(response.body, bytes)
    assert isinstance(response.headers, Headers)
    assert "content-type" in response.headers and response.headers[
        "content-type"
    ].startswith("text/html")


def test_empty_response_create():
    response = EmptyResponse()
    assert isinstance(response.text, str)
    assert response.text == ""
    assert isinstance(response.body, bytes)
    assert response.body == b""
    assert response.status_code == 204
    assert isinstance(response.headers, Headers)


@pytest.mark.asyncio
async def test_response_send():
    send = Send()
    response = Response(
        "Hello, World!",
        status_code=200,
        headers={"content-type": "text/plain"},
    )
    await response.send(send)
    assert send.values.pop(0) == {
        "type": "http.response.start",
        "status": 200,
        "headers": [[b"content-type", b"text/plain"]],
    }
    assert send.values.pop(0) == {
        "type": "http.response.body",
        "body": b"Hello, World!",
    }


@pytest.mark.parametrize(
    ["result", "expected_response"],
    [
        # result is already a response
        [Response("test"), Response("test")],
        [PlainTextResponse("test"), PlainTextResponse("test")],
        # only the response body is provided
        ["test", PlainTextResponse("test")],
        ["<h1>test</h1>", HTMLResponse("<h1>test</h1>")],
        [["test", "test2"], JSONResponse(["test", "test2"])],
        [
            {"test": "a", "test2": "b"},
            JSONResponse({"test": "a", "test2": "b"}),
        ],
        [None, EmptyResponse()],
        [2, PlainTextResponse("2")],
        # body and status code are provided
        [("test", 201), PlainTextResponse("test", status_code=201)],
        # body and headers are provided
        [
            ("test", {"server": "baguette"}),
            PlainTextResponse("test", headers=Headers(server="baguette")),
        ],
        # body, status code and headers are provided
        [
            ("test", 201, {"server": "baguette"}),
            PlainTextResponse(
                "test", status_code=201, headers=Headers(server="baguette")
            ),
        ],
    ],
)
def test_make_response(result, expected_response: Response):
    response = make_response(result)
    assert type(response) == type(expected_response)
    assert response.body == expected_response.body
    assert response.status_code == expected_response.status_code
    assert set(response.headers.keys()) == set(expected_response.headers.keys())
    for name, value in expected_response.headers:
        assert response.headers[name] == value
