import os
import pytest
import sys

sys.path.insert(0, os.path.abspath(".."))

import baguette

@pytest.fixture(name="app")
async def app_test_client():
    app = baguette.Baguette()
    return baguette.testing.TestClient(app)
