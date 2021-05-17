import pytest

from baguette.app import Baguette
from baguette.responses import Response

from ..conftest import create_test_request


@pytest.mark.asyncio
@pytest.mark.parametrize(
    [
        "headers",
        "expected_headers",
    ],
    [
        [{}, {"server": "baguette"}],
        [
            {"content-type": "text/plain"},
            {"content-type": "text/plain", "server": "baguette"},
        ],
    ],
)
async def test_default_headers_middleware(headers, expected_headers):
    app = Baguette(default_headers={"server": "baguette"})

    @app.route("/")
    async def index(request):
        return Response(body="", headers=request.headers)

    request = create_test_request(headers=headers)
    response = await app.handle_request(request)
    assert len(response.headers) == len(expected_headers)
    for name, value in expected_headers.items():
        assert response.headers[name] == value
