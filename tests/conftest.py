import pytest

import baguette


@pytest.fixture(name="app")
async def app_test_client():
    app = baguette.Baguette()

    @app.route("/")
    async def index(request):
        return "Hello, world!"

    return baguette.testing.TestClient(app)
