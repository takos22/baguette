import pytest
from baguette.testing import TestClient


@pytest.mark.asyncio
async def test_app(app: TestClient):
    response = await app.request("GET", "/")
    assert response.body == "Hello, world!".encode("utf-8")
