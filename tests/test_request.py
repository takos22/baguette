import json

import pytest

from baguette.app import Baguette
from baguette.httpexceptions import BadRequest
from baguette.request import Request

from .conftest import Receive


def test_request_create(http_scope):
    request = Request(Baguette(), http_scope, Receive())
    assert request.http_version == "1.1"
    assert request.asgi_version == "3.0"
    assert request.headers["server"] == "baguette"
    assert request.headers["content-type"] == "text/plain; charset=utf-8"
    assert request.encoding == "utf-8"
    assert request.method == "GET"
    assert request.scheme == "http"
    assert request.root_path == ""
    assert request.path == "/"
    assert request.querystring == {"a": ["b"]}
    assert request.server == ("127.0.0.1", 8000)
    assert request.client == ("127.0.0.1", 9000)


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
