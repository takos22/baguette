import re

import pytest

from baguette.converters import FloatConverter, IntegerConverter
from baguette.router import Route


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


# TODO: test Router
