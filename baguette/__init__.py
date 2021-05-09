"""
Baguette
========

Asynchronous web framework.
"""

from typing import NamedTuple

VersionInfo = NamedTuple(
    "VersionInfo", major=int, minor=int, micro=int, releaselevel=str, serial=int
)

version_info = VersionInfo(major=0, minor=2, micro=0, releaselevel="", serial=0)

__title__ = "baguette"
__author__ = "takos22"
__version__ = "0.2.0"

__all__ = [
    "Baguette",
    "Headers",
    "make_headers",
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
    "View",
]

from . import testing
from .app import Baguette
from .headers import Headers, make_headers
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
from .view import View
