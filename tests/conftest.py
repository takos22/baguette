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
