import pytest

from baguette import View, make_response
from baguette.httpexceptions import MethodNotAllowed

from .app import app


@pytest.mark.asyncio
async def test_view_create():
    class TestView(View):
        async def get(self, request):
            return "GET"

        async def post(self, request):
            return "POST"

        async def put(self, request):
            return "PUT"

        async def delete(self, request):
            return "DELETE"

        async def nonexistent_method(self, request):
            return "NONEXISTENT"

    view = TestView(app)
    assert view.methods == ["GET", "POST", "PUT", "DELETE"]
    assert await view.get(None) == "GET"
    assert await view.post(None) == "POST"
    assert await view.put(None) == "PUT"
    assert await view.delete(None) == "DELETE"
    assert await view.nonexistent_method(None) == "NONEXISTENT"


@pytest.fixture(name="view")
def create_view():
    class TestView(View):
        async def get(self, request):
            return "GET"

        async def post(self, request):
            return "POST"

        async def put(self, request):
            return "PUT"

        async def delete(self, request):
            return "DELETE"

    return TestView(app)


@pytest.mark.asyncio
async def test_view_call(view, test_request):
    result = await view(test_request)
    response = make_response(result)
    assert response.status_code == 200
    assert response.text == "GET"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ["method", "method_allowed"],
    [
        ["GET", True],
        ["POST", True],
        ["PUT", True],
        ["DELETE", True],
        ["PATCH", False],
        ["NONEXISTANT", False],
    ],
)
async def test_view_dispatch(view, test_request, method, method_allowed):
    test_request.method = method

    if method_allowed:
        result = await view.dispatch(test_request)
        response = make_response(result)

        assert response.status_code == 200
        assert response.text == method
    else:
        with pytest.raises(MethodNotAllowed):
            await view.dispatch(test_request)
