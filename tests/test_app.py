import pytest

from baguette import testing


@pytest.mark.asyncio
async def test_404(app: testing.TestClient):
    response = await app.request("GET", "/nonexistent")
    assert response.status_code == 404
    assert response.text == "Not Found"


@pytest.mark.asyncio
async def test_index(app: testing.TestClient):
    response = await app.request("GET", "/")
    assert response.status_code == 200
    assert response.text == "Hello, world!"


@pytest.mark.asyncio
async def test_index_405(app: testing.TestClient):
    response = await app.request("POST", "/")
    assert response.status_code == 405
    assert response.text == "Method Not Allowed"
