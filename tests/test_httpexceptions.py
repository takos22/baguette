import typing

import pytest

from baguette import responses
from baguette.httpexceptions import (
    BadGateway,
    BadRequest,
    Conflict,
    ExpectationFailed,
    FailedDependency,
    Forbidden,
    GatewayTimeout,
    Gone,
    HTTPException,
    HTTPVersionNotSupported,
    IMATeapot,
    InsufficientStorage,
    InternalServerError,
    LengthRequired,
    Locked,
    LoopDetected,
    MethodNotAllowed,
    MisdirectedRequest,
    NetworkAuthenticationRequired,
    NotAcceptable,
    NotExtended,
    NotFound,
    NotImplemented,
    PaymentRequired,
    PreconditionFailed,
    PreconditionRequired,
    ProxyAuthenticationRequired,
    RequestedRangeNotSatisfiable,
    RequestEntityTooLarge,
    RequestHeaderFieldsTooLarge,
    RequestTimeout,
    RequestURITooLong,
    ServiceUnavailable,
    TooEarly,
    TooManyRequests,
    Unauthorized,
    UnavailableForLegalReasons,
    UnprocessableEntity,
    UnsupportedMediaType,
    UpgradeRequired,
    VariantAlsoNegotiates,
)


@pytest.mark.parametrize(
    ["cls", "status_code", "name", "description"],
    [
        [
            BadRequest,
            400,
            "Bad Request",
            "Bad request syntax or unsupported method",
        ],
        [
            Unauthorized,
            401,
            "Unauthorized",
            "No permission -- see authorization schemes",
        ],
        [
            PaymentRequired,
            402,
            "Payment Required",
            "No payment -- see charging schemes",
        ],
        [
            Forbidden,
            403,
            "Forbidden",
            "Request forbidden -- authorization will not help",
        ],
        [NotFound, 404, "Not Found", "Nothing matches the given URI"],
        [
            MethodNotAllowed,
            405,
            "Method Not Allowed",
            "Specified method is invalid for this resource",
        ],
        [
            NotAcceptable,
            406,
            "Not Acceptable",
            "URI not available in preferred format",
        ],
        [
            ProxyAuthenticationRequired,
            407,
            "Proxy Authentication Required",
            "You must authenticate with this proxy before proceeding",
        ],
        [
            RequestTimeout,
            408,
            "Request Timeout",
            "Request timed out; try again later",
        ],
        [Conflict, 409, "Conflict", "Request conflict"],
        [
            Gone,
            410,
            "Gone",
            "URI no longer exists and has been permanently removed",
        ],
        [
            LengthRequired,
            411,
            "Length Required",
            "Client must specify Content-Length",
        ],
        [
            PreconditionFailed,
            412,
            "Precondition Failed",
            "Precondition in headers is false",
        ],
        [
            RequestEntityTooLarge,
            413,
            "Request Entity Too Large",
            "Entity is too large",
        ],
        [RequestURITooLong, 414, "Request-URI Too Long", "URI is too long"],
        [
            UnsupportedMediaType,
            415,
            "Unsupported Media Type",
            "Entity body in unsupported format",
        ],
        [
            RequestedRangeNotSatisfiable,
            416,
            "Requested Range Not Satisfiable",
            "Cannot satisfy request range",
        ],
        [
            ExpectationFailed,
            417,
            "Expectation Failed",
            "Expect condition could not be satisfied",
        ],
        [
            IMATeapot,
            418,
            "I'm a Teapot",
            "Server refuses to brew coffee because it is a teapot.",
        ],
        [
            MisdirectedRequest,
            421,
            "Misdirected Request",
            "Server is not able to produce a response",
        ],
        [UnprocessableEntity, 422, "Unprocessable Entity", ""],
        [Locked, 423, "Locked", ""],
        [FailedDependency, 424, "Failed Dependency", ""],
        [
            TooEarly,
            425,
            "Too Early",
            (
                "Server is unwilling to risk processing a request "
                "that might be replayed"
            ),
        ],
        [UpgradeRequired, 426, "Upgrade Required", ""],
        [
            PreconditionRequired,
            428,
            "Precondition Required",
            "The origin server requires the request to be conditional",
        ],
        [
            TooManyRequests,
            429,
            "Too Many Requests",
            (
                "The user has sent too many requests in a "
                'given amount of time ("rate limiting")'
            ),
        ],
        [
            RequestHeaderFieldsTooLarge,
            431,
            "Request Header Fields Too Large",
            (
                "The server is unwilling to process the request "
                "because its header fields are too large"
            ),
        ],
        [
            UnavailableForLegalReasons,
            451,
            "Unavailable For Legal Reasons",
            (
                "The server is denying access to the resource "
                "as a consequence of a legal demand"
            ),
        ],
        [
            InternalServerError,
            500,
            "Internal Server Error",
            "Server got itself in trouble",
        ],
        [
            NotImplemented,
            501,
            "Not Implemented",
            "Server does not support this operation",
        ],
        [
            BadGateway,
            502,
            "Bad Gateway",
            "Invalid responses from another server/proxy",
        ],
        [
            ServiceUnavailable,
            503,
            "Service Unavailable",
            "The server cannot process the request due to a high load",
        ],
        [
            GatewayTimeout,
            504,
            "Gateway Timeout",
            "The gateway server did not receive a timely response",
        ],
        [
            HTTPVersionNotSupported,
            505,
            "HTTP Version Not Supported",
            "Cannot fulfill request",
        ],
        [VariantAlsoNegotiates, 506, "Variant Also Negotiates", ""],
        [InsufficientStorage, 507, "Insufficient Storage", ""],
        [LoopDetected, 508, "Loop Detected", ""],
        [NotExtended, 510, "Not Extended", ""],
        [
            NetworkAuthenticationRequired,
            511,
            "Network Authentication Required",
            "The client needs to authenticate to gain network access",
        ],
    ],
)
def test_errors(
    cls: typing.Type[HTTPException],
    status_code: int,
    name: str,
    description: str,
):
    error = cls()
    assert error.status_code == status_code
    assert error.name == name
    assert error.description == description


@pytest.mark.parametrize(
    ["type_", "response_type"],
    [
        ["plain", responses.PlainTextResponse],
        ["json", responses.JSONResponse],
        ["html", responses.HTMLResponse],
    ],
)
def test_error_response(
    type_: str, response_type: typing.Type[responses.Response]
):
    error = HTTPException(400)
    response = error.response(
        type_=type_, traceback="Traceback (most recent call last):\n..."
    )
    assert isinstance(response, response_type)


def test_error_response_error():
    error = HTTPException(400)
    with pytest.raises(ValueError):
        error.response(type_="nonexistent")


def test_error_repr():
    error = HTTPException(400)
    assert repr(error).startswith("HTTP Exception: ")
    assert int(repr(error).split()[2]) == error.status_code
    assert " ".join(repr(error).split()[3:]).split(": ")[0] == error.name
