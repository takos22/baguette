"""
Baguette
========

Asynchronous web framework.
"""

from typing import NamedTuple

VersionInfo = NamedTuple(
    "VersionInfo", major=int, minor=int, micro=int, releaselevel=str, serial=int
)

version_info = VersionInfo(major=0, minor=1, micro=6, releaselevel="", serial=0)

__title__ = "baguette"
__author__ = "takos22"
__version__ = "0.1.6"

__all__ = [
    "Baguette",
    "Headers",
    "make_headers",
    "Response",
    "HTMLResponse",
    "PlainTextResponse",
    "JSONResponse",
    "EmptyResponse",
    "FileResponse",
    "make_response",
    "make_error_response",
    "Request",
    "View",
]

from . import testing
from .app import Baguette
from .headers import Headers, make_headers
from .request import Request
from .responses import (
    EmptyResponse,
    FileResponse,
    HTMLResponse,
    JSONResponse,
    PlainTextResponse,
    Response,
    make_error_response,
    make_response,
)
from .view import View
