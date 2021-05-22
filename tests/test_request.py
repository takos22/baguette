import json
from urllib.parse import urlencode

import pytest

from baguette.app import Baguette
from baguette.forms import Field, FileField, Form
from baguette.httpexceptions import BadRequest
from baguette.request import Request

from .conftest import Receive, create_http_scope


def test_request_create(http_scope):
    request = Request(Baguette(), http_scope, Receive())
    assert request.http_version == "1.1"
    assert request.asgi_version == "3.0"
    assert request.headers["server"] == "baguette"
    assert request.headers["content-type"] == "text/plain; charset=utf-8"
    assert request.content_type == "text/plain"
    assert request.encoding == "utf-8"
    assert request.method == "GET"
    assert request.scheme == "http"
    assert request.root_path == ""
    assert request.path == "/"
    assert request.querystring == {"a": ["b"]}
    assert request.server == ("127.0.0.1", 8000)
    assert request.client == ("127.0.0.1", 9000)


@pytest.mark.asyncio
async def test_request_raw_body(http_scope):
    receive = Receive(
        [
            {
                "type": "http.request.body",
                "body": b"Hello, ",
                "more_body": True,
            },
            {
                "type": "http.request.body",
                "body": b"World!",
            },
        ]
    )
    request = Request(Baguette(), http_scope, receive)
    assert await request.raw_body() == b"Hello, World!"
    assert len(receive.values) == 0
    # caching
    assert hasattr(request, "_raw_body")
    assert await request.raw_body() == b"Hello, World!"


@pytest.mark.asyncio
async def test_request_body(http_scope):
    receive = Receive(
        [
            {
                "type": "http.request.body",
                "body": b"Hello, ",
                "more_body": True,
            },
            {
                "type": "http.request.body",
                "body": b"World!",
            },
        ]
    )
    request = Request(Baguette(), http_scope, receive)
    assert await request.body() == "Hello, World!"
    assert len(receive.values) == 0
    # caching
    assert hasattr(request, "_raw_body")
    assert hasattr(request, "_body")
    assert await request.body() == "Hello, World!"


@pytest.mark.asyncio
async def test_request_json(http_scope):
    receive = Receive(
        [
            {
                "type": "http.request.body",
                "body": json.dumps({"message": "Hello, World!"}).encode(
                    "utf-8"
                ),
            }
        ]
    )
    request = Request(Baguette(), http_scope, receive)
    assert await request.json() == {"message": "Hello, World!"}
    assert len(receive.values) == 0
    # caching
    assert hasattr(request, "_raw_body")
    assert hasattr(request, "_body")
    assert hasattr(request, "_json")
    assert await request.json() == {"message": "Hello, World!"}


@pytest.mark.asyncio
async def test_request_json_error(http_scope):
    receive = Receive(
        [
            {
                "type": "http.request.body",
                "body": b"no json",
            }
        ]
    )
    request = Request(Baguette(), http_scope, receive)
    with pytest.raises(BadRequest):
        await request.json()


@pytest.mark.asyncio
async def test_request_form_url_encoded():
    http_scope = create_http_scope(
        headers="content-type: application/x-www-form-urlencoded",
        querystring=urlencode({"test2": "test test test"}),
    )
    receive = Receive(
        [
            {
                "type": "http.request.body",
                "body": urlencode({"test": "test test"}).encode("utf-8"),
            }
        ]
    )
    request = Request(Baguette(), http_scope, receive)
    assert {
        field.name: field.value
        for field in (await request.form()).fields.values()
    } == {"test": "test test"}
    assert len(receive.values) == 0
    # caching
    assert hasattr(request, "_raw_body")
    assert {
        field.name: field.value
        for field in (await request.form()).fields.values()
    } == {"test": "test test"}

    # include querystring
    assert {
        field.name: field.value
        for field in (
            await request.form(include_querystring=True)
        ).fields.values()
    } == {"test": "test test", "test2": "test test test"}


multipart_body = (
    b"--abcd1234\r\n"
    b'Content-Disposition: form-data; name="test"\r\n\r\n'
    b"test test\r\n"
    b"--abcd1234\r\n"
    b'Content-Disposition: form-data; name="file"; filename="script.js"\r\n'
    b"Content-Type: application/javascript\r\n\r\n"
    b'console.log("Hello, World!")\r\n'
    b"--abcd1234\r\n"
    b'Content-Disposition: form-data; name="another test"\r\n\r\n'
    b"another test test\r\n"
    b"--abcd1234--\r\n"
)


@pytest.mark.asyncio
async def test_request_form_multipart():
    http_scope = create_http_scope(
        headers="content-type: multipart/form-data; boundary=abcd1234",
        querystring=urlencode({"test": "test test test"}),
    )
    receive = Receive(
        [
            {
                "type": "http.request.body",
                "body": multipart_body,
            }
        ]
    )
    request = Request(Baguette(), http_scope, receive)
    form = await request.form()
    assert {
        field.name: field.value
        for field in form.fields.values()
        if not field.is_file
    } == {"test": "test test", "another test": "another test test"}
    assert {file.name: file.content for file in form.files.values()} == {
        "file": b'console.log("Hello, World!")'
    }
    assert len(receive.values) == 0
    # caching
    assert hasattr(request, "_raw_body")
    form = await request.form()
    assert {
        field.name: field.value
        for field in form.fields.values()
        if not field.is_file
    } == {"test": "test test", "another test": "another test test"}
    assert {file.name: file.content for file in form.files.values()} == {
        "file": b'console.log("Hello, World!")'
    }

    # include querystring
    form = await request.form(include_querystring=True)
    assert {
        field.name: field.values
        for field in form.fields.values()
        if not field.is_file
    } == {
        "test": ["test test", "test test test"],
        "another test": ["another test test"],
    }


@pytest.mark.asyncio
async def test_request_form_error():
    http_scope = create_http_scope(
        headers="content-type: text/plain",
    )
    receive = Receive(
        [
            {
                "type": "http.request.body",
                "body": b"",
            }
        ]
    )
    request = Request(Baguette(), http_scope, receive)
    with pytest.raises(ValueError):
        await request.form()


@pytest.mark.asyncio
async def test_request_set_raw_body(test_request: Request):
    test_request.set_raw_body(b"Hello, World!")
    assert test_request._raw_body == b"Hello, World!"
    assert (await test_request.raw_body()) == b"Hello, World!"


def test_request_set_raw_body_error(test_request: Request):
    with pytest.raises(TypeError):
        test_request.set_raw_body("Hello, World!")


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ["body", "expected_body", "expected_raw_body"],
    [
        ["Hello, World!", "Hello, World!", b"Hello, World!"],
        [b"Hello, World!", "Hello, World!", b"Hello, World!"],
    ],
)
async def test_request_set_body(
    test_request: Request, body, expected_body, expected_raw_body
):
    test_request.set_body(body)
    assert test_request._raw_body == expected_raw_body
    assert (await test_request.raw_body()) == expected_raw_body
    assert test_request._body == expected_body
    assert (await test_request.body()) == expected_body


def test_request_set_body_error(test_request: Request):
    with pytest.raises(TypeError):
        test_request.set_body(1)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ["json", "expected_json", "expected_body", "expected_raw_body"],
    [
        [
            "Hello, World!",
            "Hello, World!",
            '"Hello, World!"',
            b'"Hello, World!"',
        ],
        [
            {"Hello": "World!"},
            {"Hello": "World!"},
            '{"Hello":"World!"}',
            b'{"Hello":"World!"}',
        ],
    ],
)
async def test_request_set_json(
    test_request: Request, json, expected_json, expected_body, expected_raw_body
):
    test_request.set_json(json)
    assert test_request._raw_body == expected_raw_body
    assert (await test_request.raw_body()) == expected_raw_body
    assert test_request._body == expected_body
    assert (await test_request.body()) == expected_body
    assert test_request._json == expected_json
    assert (await test_request.json()) == expected_json


def test_request_set_json_error(test_request: Request):
    with pytest.raises(TypeError):
        test_request.set_json(set())


@pytest.mark.asyncio
async def test_request_set_form(test_request: Request):
    form = Form(
        fields={
            "test": Field(name="test", values=["test", b"test2"]),
            "file": FileField(
                name="file",
                content=b'console.log("Hello, World!")',
                filename="script.js",
            ),
        }
    )
    test_request.set_form(form)
    assert test_request._form == form
    assert (await test_request.form()) == form


def test_request_set_form_error(test_request: Request):
    with pytest.raises(TypeError):
        test_request.set_form("Hello, World!")
