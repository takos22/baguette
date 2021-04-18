import pytest

import baguette


@pytest.fixture(name="app")
async def app_test_client():
    from .app import app

    return baguette.testing.TestClient(app)
