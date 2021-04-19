import pytest

from baguette.headers import Headers
from baguette.responses import (
    EmptyResponse,
    HTMLResponse,
    JSONResponse,
    PlainTextResponse,
    Response,
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
