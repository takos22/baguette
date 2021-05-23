import json
import pathlib
import re

import aiofiles
import pytest

from baguette.headers import Headers
from baguette.httpexceptions import NotFound
from baguette.responses import (
    EmptyResponse,
    FileResponse,
    HTMLResponse,
    JSONResponse,
    PlainTextResponse,
    RedirectResponse,
    Response,
    make_response,
    redirect,
)

from .conftest import Send


@pytest.mark.parametrize("body", ["Hello, World!", b"Hello, World!"])
def test_response_create(body):
    response = Response(
        body,
        headers={"content_type": "text/plain"},
    )
    assert isinstance(response.body, str)
    assert isinstance(response.raw_body, bytes)
    assert isinstance(response.status_code, int)
    assert isinstance(response.headers, Headers)

    assert response.body == "Hello, World!"
    assert response.raw_body == b"Hello, World!"
    assert response.headers == {"content_type": "text/plain"}


def test_response_create_error():
    with pytest.raises(TypeError):
        Response(1)


def test_response_body():
    response = Response(
        "Hello, World!",
        headers={"content_type": "text/plain"},
    )

    assert response.body == "Hello, World!"
    assert response.raw_body == b"Hello, World!"
    assert response.headers == {"content_type": "text/plain"}

    response.body = "Bye, World!"
    assert response.body == "Bye, World!"
    assert response.raw_body == b"Bye, World!"

    response.body = b"Hello again, World!"
    assert response.body == "Hello again, World!"
    assert response.raw_body == b"Hello again, World!"

    response.raw_body = "Bye, World!"
    assert response.body == "Bye, World!"
    assert response.raw_body == b"Bye, World!"

    response.raw_body = b"Hello again, World!"
    assert response.body == "Hello again, World!"
    assert response.raw_body == b"Hello again, World!"


def test_response_body_error():
    response = Response(
        "Hello, World!",
        headers={"content_type": "text/plain"},
    )
    with pytest.raises(TypeError):
        response.body = 1
    with pytest.raises(TypeError):
        response.raw_body = 1


def test_json_response_create():
    response = JSONResponse({"message": "Hello, World!"})
    assert isinstance(response.json, dict)
    assert isinstance(response.body, str)
    assert isinstance(response.raw_body, bytes)
    assert isinstance(response.status_code, int)
    assert isinstance(response.headers, Headers)

    assert response.headers["content-type"] == "application/json"
    assert json.loads(response.body) == {"message": "Hello, World!"}


def test_plain_text_response_create():
    response = PlainTextResponse("Hello, World!")
    assert isinstance(response.body, str)
    assert isinstance(response.raw_body, bytes)
    assert isinstance(response.status_code, int)
    assert isinstance(response.headers, Headers)

    assert response.body == "Hello, World!"
    assert response.raw_body == b"Hello, World!"
    assert response.headers["content-type"].startswith("text/plain")


def test_html_response_create():
    response = HTMLResponse("<h1>Hello, World!</h1>")
    assert isinstance(response.body, str)
    assert isinstance(response.raw_body, bytes)
    assert isinstance(response.status_code, int)
    assert isinstance(response.headers, Headers)

    assert response.body == "<h1>Hello, World!</h1>"
    assert response.raw_body == b"<h1>Hello, World!</h1>"
    assert response.headers["content-type"].startswith("text/html")


def test_empty_response_create():
    response = EmptyResponse()
    assert isinstance(response.body, str)
    assert isinstance(response.raw_body, bytes)
    assert isinstance(response.status_code, int)
    assert isinstance(response.headers, Headers)

    assert response.body == ""
    assert response.raw_body == b""
    assert response.status_code == 204


def test_redirect_response_create():
    response = RedirectResponse("/home")
    assert isinstance(response.body, str)
    assert isinstance(response.raw_body, bytes)
    assert isinstance(response.status_code, int)
    assert isinstance(response.headers, Headers)

    assert response.body == ""
    assert response.raw_body == b""
    assert response.status_code == 301
    assert response.location == "/home"


def test_redirect():
    response = redirect(
        "/home", status_code=302, headers={"server": "baguette"}
    )
    assert isinstance(response.body, str)
    assert isinstance(response.raw_body, bytes)
    assert isinstance(response.status_code, int)
    assert isinstance(response.headers, Headers)
    assert response.status_code == 302
    assert (
        "location" in response.headers
        and response.headers["location"] == "/home"
    )
    assert (
        "server" in response.headers
        and response.headers["server"] == "baguette"
    )


@pytest.mark.parametrize(
    ["file_path", "mimetype", "kwargs"],
    [
        [
            "tests/static/banner.png",
            "image/png",
            dict(as_attachment=True, attachment_filename="baguette.png"),
        ],
        ["tests/static/css/style.css", "text/css", dict(add_etags=False)],
        ["tests/static/js/script.js", "application/javascript", {}],
    ],
)
def test_file_response_create(file_path, mimetype, kwargs):
    response = FileResponse(file_path, **kwargs)

    path = pathlib.Path(file_path).resolve(strict=True)
    with open(path, "rb") as f:
        content_length = len(f.read())

    assert response.file_path == path
    assert response.mimetype == mimetype
    assert response.headers["content-type"] == mimetype
    assert response.file_size == content_length
    assert int(response.headers["content-length"]) == content_length

    if kwargs.get("as_attachment", False):
        filename = kwargs.get("attachment_filename", path.name)
        assert (
            response.headers["content-disposition"]
            == "attachment; filename=" + filename
        )

    if kwargs.get("add_etags", True):
        assert re.fullmatch(r"(\d|\.)+-\d+-\d+", response.headers["etag"])


def test_file_response_create_error():
    with pytest.raises(NotFound):
        FileResponse("nonexistent")
    with pytest.raises(NotFound):
        FileResponse("tests/static")


@pytest.mark.asyncio
async def test_response_send():
    send = Send()
    response = Response(
        "Hello, World!",
        status_code=200,
        headers={"content-type": "text/plain"},
    )
    await response._send(send)
    assert send.values.pop(0) == {
        "type": "http.response.start",
        "status": 200,
        "headers": [[b"content-type", b"text/plain"]],
    }
    assert send.values.pop(0) == {
        "type": "http.response.body",
        "body": b"Hello, World!",
    }


@pytest.mark.asyncio
async def test_file_response_send():
    send = Send()
    response = FileResponse("tests/static/css/style.css", add_etags=False)
    async with aiofiles.open("tests/static/css/style.css", "rb") as f:
        content = await f.read()

    await response._send(send)
    assert send.values.pop(0) == {
        "type": "http.response.start",
        "status": 200,
        "headers": [
            [b"content-length", str(len(content)).encode()],
            [b"content-type", b"text/css"],
        ],
    }
    assert send.values.pop(0) == {
        "type": "http.response.body",
        "body": content,
    }


@pytest.mark.parametrize(
    ["result", "expected_response"],
    [
        # result is already a response
        [Response("test"), Response("test")],
        [PlainTextResponse("test"), PlainTextResponse("test")],
        # only the response body is provided
        ["test", PlainTextResponse("test")],
        [b"test", PlainTextResponse("test")],
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
    assert response.raw_body == expected_response.raw_body
    assert response.status_code == expected_response.status_code
    assert set(response.headers.keys()) == set(expected_response.headers.keys())
    for name, value in expected_response.headers:
        assert response.headers[name] == value
