import pathlib

import pytest

from baguette.headers import Headers
from baguette.httpexceptions import NotFound
from baguette.utils import (
    file_path_to_path,
    get_encoding_from_headers,
    safe_join,
    split_on_first,
)


@pytest.mark.parametrize(
    ["headers", "encoding"],
    [
        [Headers(), None],
        [Headers(("content-type", "text/plain")), "ISO-8859-1"],
        [Headers(("content-type", "text/plain; charset=utf-8")), "utf-8"],
        [Headers(("content-type", "text/plain; charset='utf-8'")), "utf-8"],
        [Headers(("content-type", 'text/plain; charset="utf-8"')), "utf-8"],
    ],
)
def test_get_encoding_from_headers(headers, encoding):
    assert get_encoding_from_headers(headers) == encoding


@pytest.mark.parametrize(
    "paths",
    [
        ["test/test/test"],
        ["test", "test/test"],
        [b"test/test/test"],
        ["test", b"test/test"],
        [b"test", b"test/test"],
        [pathlib.Path("test/test/test")],
        [pathlib.Path("test"), pathlib.Path("test/test")],
    ],
)
def test_file_path_to_path(paths):
    path = file_path_to_path(*paths)
    assert path == pathlib.Path("test/test/test")


@pytest.mark.parametrize(
    ["directory", "paths"],
    [
        ["static", ["css/style.css"]],
        ["static", ["css", "style.css"]],
    ],
)
def test_safe_join(directory, paths):
    path = safe_join(directory, *paths)
    assert path == pathlib.Path("static/css/style.css").resolve()


def test_safe_join_error():
    with pytest.raises(NotFound):
        safe_join("nonexistent", "css/style.css")
    with pytest.raises(NotFound):
        safe_join("static", "nonexistent")
    with pytest.raises(NotFound):
        safe_join("static", "..")


@pytest.mark.parametrize(
    ["text", "sep", "expected"],
    [
        ["test", ":", ("test", "")],
        ["test:test", ":", ("test", "test")],
        ["test:test:test", ":", ("test", "test:test")],
        [b"test", b":", (b"test", b"")],
        [b"test:test", b":", (b"test", b"test")],
        [b"test:test:test", b":", (b"test", b"test:test")],
    ],
)
def test_split_on_first(text, sep, expected):
    assert split_on_first(text, sep) == expected
