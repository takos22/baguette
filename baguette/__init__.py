"""
Baguette
========

Asynchronous web framework.
"""

from typing import NamedTuple

VersionInfo = NamedTuple(
    "VersionInfo", major=int, minor=int, micro=int, releaselevel=str, serial=int
)

version_info = VersionInfo(
    major=0, minor=0, micro=4, releaselevel="alpha", serial=0
)

__title__ = "baguette"
__author__ = "takos22"
__version__ = "0.0.4a"

__all__ = [
    "Baguette",
    "Headers",
    "Response",
    "HTMLResponse",
    "PlainTextResponse",
    "JSONResponse",
    "EmptyResponse",
    "Request",
    "View",
]

from . import testing
from .app import Baguette
from .headers import Headers
from .request import Request
from .responses import (
    EmptyResponse,
    HTMLResponse,
    JSONResponse,
    PlainTextResponse,
    Response,
)
from .view import View
