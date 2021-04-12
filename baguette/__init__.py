"""
Baguette
~~~~~~~~

Asynchronous web framework based on Uvicorn.
"""

from typing import NamedTuple

VersionInfo = NamedTuple(
    "VersionInfo", major=int, minor=int, micro=int, releaselevel=str, serial=int
)

version_info = VersionInfo(major=0, minor=0, micro=1, releaselevel="", serial=0)

__title__ = "baguette"
__author__ = "takos22"
__version__ = "0.0.1"

__all__ = ["App"]

from .app import App
