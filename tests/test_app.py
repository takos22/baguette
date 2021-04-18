import pytest

from baguette import testing


@pytest.mark.asyncio
async def test_app(app: testing.TestClient):
    response = await app.request("GET", "/")
    assert response.body == "Hello, world!".encode("utf-8")
