import threading

import pytest
import requests

from baguette.app import Baguette
from baguette.headers import Headers
from baguette.httpexceptions import NotImplemented
from baguette.responses import EmptyResponse, PlainTextResponse
from baguette.router import Router
from baguette.view import View

from .conftest import Receive, Send, create_http_scope, create_test_request


def test_create_app():
    app = Baguette()
    assert app.debug is False
    assert isinstance(app.router, Router)
    assert isinstance(app.default_headers, Headers)
    assert app.error_response_type == "plain"
    assert app.error_include_description is True

    app = Baguette(
        debug=True,
        default_headers={"server": "baguette"},
        error_response_type="json",
        error_include_description=False,
    )
    assert app.debug is True
    assert isinstance(app.router, Router)
    assert isinstance(app.default_headers, Headers)
    assert app.default_headers["server"] == "baguette"
    assert app.error_response_type == "json"
    assert app.error_include_description is True  # True because debug=True

    with pytest.raises(ValueError):
        Baguette(error_response_type="nonexistent")


def setup1(app):
    @app.route("/")
    async def index(request):
        return await request.body()

    return index


def setup2(app):
    async def home():
        return "home"

    app.add_route(path="/home", handler=home, methods=["GET"])

    return home


def setup3(app):
    @app.route(
        "/profile/<user_id:int>",
        name="profile",
        defaults={"user_id": 0},
    )
    class ProfileView(View):
        async def get(user_id: int):
            return str(user_id)

        async def delete(user_id: int):
            return EmptyResponse()

    return ProfileView


@pytest.mark.parametrize(
    ["setup", "expected_attributes"],
    [
        [
            setup1,
            {
                "path": "/",
                "name": "index",
                "methods": ["GET", "HEAD"],
                "defaults": {},
                "handler_kwargs": ["request"],
                "handler_is_class": False,
            },
        ],
        [
            setup2,
            {
                "path": "/home",
                "name": "home",
                "methods": ["GET"],
                "defaults": {},
                "handler_kwargs": [],
                "handler_is_class": False,
            },
        ],
        [
            setup3,
            {
                "path": "/profile/<user_id:int>",
                "name": "profile",
                "methods": ["GET", "DELETE"],
                "defaults": {"user_id": 0},
                "handler_kwargs": ["request"],
                "handler_is_class": True,
            },
        ],
    ],
)
def test_app_route(setup, expected_attributes: dict):
    app = Baguette()

    handler = setup(app)

    assert len(app.router.routes) == 1
    router = app.router.routes.pop()

    if router.handler_is_class:
        assert isinstance(router.handler, handler)
    else:
        assert router.handler == handler

    for name, value in expected_attributes.items():
        assert getattr(router, name) == value


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
        ["/", "GET", "Hello, World!", "Hello, World!", 200],
        ["/", "POST", "", "Method Not Allowed", 405],
        ["/user/1", "GET", "", "1", 200],
        ["/user/-1", "GET", "", "Bad Request", 400],
        ["/user/text", "GET", "", "Not Found", 404],
        ["/notimplemented", "GET", "", "Not Implemented", 501],
        ["/nonexistent", "GET", "", "Not Found", 404],
    ],
)
async def test_app_handle_request(
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

    request = create_test_request(path=path, method=method, body=body)
    response = await app.handle_request(request)
    assert response.text == expected_response_body
    assert response.status_code == expected_response_status_code


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ["scope", "receive", "expected_sent_values"],
    [
        [
            create_http_scope(),
            Receive(
                [
                    {
                        "type": "http.request.body",
                        "body": b"Hello, ",
                        "more_body": True,
                    },
                    {
                        "type": "http.request.body",
                        "body": b"World!",
                    },
                ]
            ),
            [
                {
                    "type": "http.response.start",
                    "status": 200,
                    "headers": [
                        [b"content-type", b"text/plain; charset=utf-8"]
                    ],
                },
                {
                    "type": "http.response.body",
                    "body": b"Hello, World!",
                },
            ],
        ],
        [
            {"type": "lifespan"},
            Receive(
                [
                    {"type": "lifespan.startup"},
                    {"type": "lifespan.shutdown"},
                ]
            ),
            [
                {"type": "lifespan.startup.complete"},
                {"type": "lifespan.shutdown.complete"},
            ],
        ],
    ],
)
async def test_app_call(scope, receive: Receive, expected_sent_values: list):
    app = Baguette()

    @app.route("/")
    async def index(request):
        return PlainTextResponse(await request.body())

    send = Send()
    await app(scope, receive, send)

    assert len(expected_sent_values) == len(send.values)
    for message in send.values:
        assert message == expected_sent_values.pop(0)


@pytest.mark.asyncio
async def test_app_call_lifespan_error():
    class BadLifespanApp(Baguette):
        async def startup(self):
            raise Exception()

        async def shutdown(self):
            raise Exception()

    app = BadLifespanApp()

    scope = {"type": "lifespan"}
    receive = Receive(
        [
            {"type": "lifespan.startup"},
            {"type": "lifespan.shutdown"},
        ]
    )
    expected_sent_values = [
        {"type": "lifespan.startup.failed", "message": ""},
        {"type": "lifespan.shutdown.failed", "message": ""},
    ]
    send = Send()

    await app(scope, receive, send)

    assert len(expected_sent_values) == len(send.values)
    for message in send.values:
        assert message == expected_sent_values.pop(0)


@pytest.mark.asyncio
async def test_app_call_error():
    app = Baguette()

    scope = {"type": "nonexistent"}
    receive = Receive()
    send = Send()

    with pytest.raises(NotImplementedError):
        await app(scope, receive, send)


def test_app_run():
    app = Baguette()

    running = threading.Event()

    async def set_running():
        running.set()

    def do_request():
        if not running.wait(10.0):
            raise TimeoutError("App hasn't started after 10s")

        requests.get("http://127.0.0.1:8000")

    request_thread = threading.Thread(target=do_request)
    request_thread.start()

    app.run(
        host="127.0.0.1",
        port=8000,
        debug=True,
        limit_max_requests=1,  # end after one request
        callback_notify=set_running,
        timeout_notify=1,  # set the running event every second
    )

    request_thread.join()
