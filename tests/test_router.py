import re

import pytest

from baguette.converters import FloatConverter, IntegerConverter
from baguette.httpexceptions import MethodNotAllowed, NotFound
from baguette.router import Route, Router


def test_route():
    async def handler(request, id: int):
        pass

    route = Route(
        path="/test/<id:int>/test",
        name="test",
        handler=handler,
        methods=["GET"],
    )
    assert route.handler_kwargs == ["request", "id"]
    assert route.handler_is_class is False

    id_converter = route.converters[1]
    assert id_converter[0] == "id"
    assert isinstance(id_converter[1], IntegerConverter)

    assert route.regex == re.compile(r"\/test\/[\+-]?\d+\/test")
    assert route.match("/test/1/test")
    assert not route.match("/test")
    assert not route.match("/test/1")
    assert not route.match("/test//test")
    assert not route.match("/test/test/test")

    assert route.convert("/test/1/test") == {"id": 1}
    with pytest.raises(ValueError):
        route.convert("/test")
    with pytest.raises(ValueError):
        route.convert("/test/test/test")
    route.defaults["id"] = 1
    assert route.convert("/test") == {"id": 1}


def test_route2():
    async def handler(request):
        pass

    with pytest.raises(ValueError):
        Route(
            path="/test/<id:test>/test",
            name="test",
            handler=handler,
            methods=["GET"],
        )

    with pytest.raises(TypeError):
        Route(
            path="/test/<id:str(test=test)>/test",
            name="test",
            handler=handler,
            methods=["GET"],
        )

    route = Route(
        path="/test/<id:float(signed=True, min=-10, max=10.0)>/test",
        name="test",
        handler=handler,
        methods=["GET"],
    )
    assert route.handler_kwargs == ["request"]
    assert route.handler_is_class is False

    id_converter = route.converters[1]
    assert id_converter[0] == "id"
    assert isinstance(id_converter[1], FloatConverter)
    assert id_converter[1].signed is True
    assert id_converter[1].min == -10
    assert id_converter[1].max == pytest.approx(10.0)


def test_router():
    async def handler(request):
        pass

    index = Route(
        path="/",
        name="index",
        handler=handler,
        methods=["GET"],
    )
    router = Router(routes=[index])
    assert len(router.routes) == 1

    home = router.add_route(
        path="/home",
        name="home",
        handler=handler,
        methods=["GET", "HEAD"],
    )
    assert len(router.routes) == 2

    user_get = router.add_route(
        path="/user/<user_id:int(min=1)>",
        name="home",
        handler=handler,
        methods=["GET"],
    )
    assert len(router.routes) == 3

    user_delete = router.add_route(
        path="/user/<user_id:int(min=1)>",
        name="home",
        handler=handler,
        methods=["DELETE"],
    )
    assert len(router.routes) == 4

    with pytest.raises(NotFound):
        router.get("/nonexistent", "GET")

    assert router.get("/", "GET") == index
    with pytest.raises(MethodNotAllowed):
        router.get("/", "POST")

    assert router.get("/home", "GET") == home
    assert router.get("/home", "HEAD") == home
    with pytest.raises(MethodNotAllowed):
        router.get("/home", "POST")

    assert router.get("/user/1", "GET") == user_get
    assert router.get("/user/1", "DELETE") == user_delete
    with pytest.raises(MethodNotAllowed):
        router.get("/user/1", "POST")
