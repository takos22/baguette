import pytest

from baguette.app import Baguette
from baguette.httpexceptions import NotImplemented

from ..conftest import create_test_request


@pytest.mark.asyncio
@pytest.mark.parametrize(
    [
        "path",
        "method",
        "body",
        "expected_response_body",
        "expected_response_status_code",
    ],
    [
        ["/", "POST", "", "Method Not Allowed", 405],
        ["/user/-1", "GET", "", "Bad Request", 400],
        ["/user/text", "GET", "", "Not Found", 404],
        ["/notimplemented", "GET", "", "Not Implemented", 501],
        ["/error", "GET", "", "Internal Server Error", 500],
        ["/nonexistent", "GET", "", "Not Found", 404],
    ],
)
async def test_error_middleware(
    path: str,
    method: str,
    body: str,
    expected_response_body: str,
    expected_response_status_code: int,
):
    app = Baguette(error_include_description=False)

    @app.route("/")
    async def index(request):
        return await request.body()

    @app.route("/user/<user_id:int>")
    async def user(user_id: int):
        return str(user_id)

    @app.route("/notimplemented")
    async def notimplemented():
        raise NotImplemented()  # noqa: F901

    @app.route("/error")
    async def error():
        raise Exception()

    request = create_test_request(path=path, method=method, body=body)
    response = await app.handle_request(request)
    assert response.body == expected_response_body
    assert response.status_code == expected_response_status_code
