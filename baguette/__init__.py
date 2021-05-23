"""
Baguette
========

Asynchronous web framework.
"""

from typing import NamedTuple

VersionInfo = NamedTuple(
    "VersionInfo", major=int, minor=int, micro=int, releaselevel=str, serial=int
)

version_info = VersionInfo(major=0, minor=3, micro=0, releaselevel="", serial=1)

__title__ = "baguette"
__author__ = "takos22"
__version__ = "0.3.1"

__all__ = [
    "Baguette",
    "Config",
    "Headers",
    "make_headers",
    "Middleware",
    "render",
    "Response",
    "HTMLResponse",
    "PlainTextResponse",
    "JSONResponse",
    "EmptyResponse",
    "RedirectResponse",
    "FileResponse",
    "make_response",
    "make_error_response",
    "redirect",
    "Request",
    "TestClient",
    "View",
]

from .app import Baguette
from .config import Config
from .headers import Headers, make_headers
from .middleware import Middleware
from .rendering import render
from .request import Request
from .responses import (
    EmptyResponse,
    FileResponse,
    HTMLResponse,
    JSONResponse,
    PlainTextResponse,
    RedirectResponse,
    Response,
    make_error_response,
    make_response,
    redirect,
)
from .testing import TestClient
from .view import View
