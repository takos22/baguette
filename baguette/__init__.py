"""
Baguette
========

Asynchronous web framework.
"""

from typing import NamedTuple

VersionInfo = NamedTuple(
    "VersionInfo", major=int, minor=int, micro=int, releaselevel=str, serial=int
)

version_info = VersionInfo(major=0, minor=1, micro=4, releaselevel="", serial=0)

__title__ = "baguette"
__author__ = "takos22"
__version__ = "0.1.4"

__all__ = [
    "Baguette",
    "Headers",
    "make_headers",
    "Response",
    "HTMLResponse",
    "PlainTextResponse",
    "JSONResponse",
    "EmptyResponse",
    "make_response",
    "Request",
    "View",
]

from . import testing
from .app import Baguette
from .headers import Headers, make_headers
from .request import Request
from .responses import (
    EmptyResponse,
    HTMLResponse,
    JSONResponse,
    PlainTextResponse,
    Response,
    make_response,
)
from .view import View
