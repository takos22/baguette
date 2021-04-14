"""
Baguette
========

Asynchronous web framework.
"""

from typing import NamedTuple

VersionInfo = NamedTuple(
    "VersionInfo", major=int, minor=int, micro=int, releaselevel=str, serial=int
)

version_info = VersionInfo(major=0, minor=0, micro=2, releaselevel="", serial=0)

__title__ = "baguette"
__author__ = "takos22"
__version__ = "0.0.2"

__all__ = ["Baguette", "View"]

from .app import Baguette
from .view import View
