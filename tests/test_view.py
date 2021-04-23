import pytest

from baguette.app import Baguette
from baguette.httpexceptions import MethodNotAllowed
from baguette.responses import make_response
from baguette.view import View


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

    view = TestView(Baguette())
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

    return TestView(Baguette())


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
        ["NONEXISTENT", False],
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
