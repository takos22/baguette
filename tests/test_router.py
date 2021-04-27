import re

import pytest

from baguette.converters import (
    FloatConverter,
    IntegerConverter,
    PathConverter,
    StringConverter,
)
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

    id_converter = route.converters["id"]
    assert isinstance(id_converter, IntegerConverter)

    assert route.regex == re.compile(r"\/test\/(?P<id>[\+-]?\d+)\/test\/?")
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

    route.path = "/test/<id:int>"
    route.defaults["id"] = 1
    route.build_regex()
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

    id_converter = route.converters["id"]
    assert isinstance(id_converter, FloatConverter)
    assert id_converter.signed is True
    assert id_converter.min == -10
    assert id_converter.max == pytest.approx(10.0)


def test_route3():
    async def handler(request, test: str):
        pass

    route = Route(
        path="/test/<test>/test",
        name="test",
        handler=handler,
        methods=["GET"],
    )
    assert route.handler_kwargs == ["request", "test"]
    assert route.handler_is_class is False

    id_converter = route.converters["test"]
    assert isinstance(id_converter, StringConverter)

    assert route.regex == re.compile(r"\/test\/(?P<test>[^\/]+)\/test\/?")
    assert route.match("/test/1/test")
    assert route.match("/test/test/test")
    assert not route.match("/test")
    assert not route.match("/test/1")
    assert not route.match("/test//test")

    assert route.convert("/test/test/test") == {"test": "test"}
    assert route.convert("/test/1/test") == {"test": "1"}
    with pytest.raises(ValueError):
        route.convert("/test")

    route.path = "/test/<test>"
    route.defaults["test"] = "test"
    route.build_regex()
    assert route.convert("/test") == {"test": "test"}


def test_route4():
    async def handler(path: str):
        pass

    route = Route(
        path="/test/<path:path>/test",
        name="path",
        handler=handler,
        methods=["GET"],
    )
    assert route.handler_kwargs == ["path"]
    assert route.handler_is_class is False

    path_converter = route.converters["path"]
    assert isinstance(path_converter, PathConverter)

    assert route.regex == re.compile(r"\/test\/(?P<path>.+)\/test\/?")
    assert route.match("/test/1/test")
    assert route.match("/test/test/test")
    assert route.match("/test/test/test/test")
    assert not route.match("/test")
    assert not route.match("/test/1")
    assert not route.match("/test//test")

    assert route.convert("/test/test/test") == {"path": "test"}
    assert route.convert("/test/test/test/test") == {"path": "test/test"}
    assert route.convert("/test/1/test") == {"path": "1"}
    with pytest.raises(ValueError):
        route.convert("/test")

    route.path = "/test/<path:path>"
    route.defaults["path"] = "test/test"
    route.build_regex()
    assert route.convert("/test") == {"path": "test/test"}


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
