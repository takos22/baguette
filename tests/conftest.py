import pytest

import baguette

@pytest.fixture(name="app")
async def app_test_client():
    app = baguette.Baguette()
    return baguette.testing.TestClient(app)
