import cgi
import os
import pathlib
import typing

from .httpexceptions import NotFound
from .types import FilePath


def get_encoding_from_content_type(content_type):
    """Returns encodings from given Content-Type Header."""

    if not content_type:
        return None

    content_type, params = cgi.parse_header(content_type)

    if "charset" in params:
        return params["charset"].strip("'\"")

    if "text" in content_type:
        return "ISO-8859-1"


def get_encoding_from_headers(headers):
    """Returns encodings from given HTTP Headers."""

    content_type = headers.get("content-type")

    return get_encoding_from_content_type(content_type)


def file_path_to_path(*paths: FilePath) -> pathlib.Path:
    """Convert a list of paths into a pathlib.Path."""

    safe_paths: typing.List[typing.Union[str, os.PathLike]] = []
    for path in paths:
        if isinstance(path, bytes):
            safe_paths.append(path.decode())
        else:
            safe_paths.append(path)

    return pathlib.Path(*safe_paths)


def safe_join(directory: FilePath, *paths: FilePath) -> pathlib.Path:
    """Safely join the paths to the known directory to return a full path.

    Raises
    ------
        ~baguette.httpexceptions.NotFound
            If the full path does not share a commonprefix with the directory.
    """
    try:
        safe_path = file_path_to_path(directory).resolve(strict=True)
        full_path = file_path_to_path(directory, *paths).resolve(strict=True)
    except FileNotFoundError:
        raise NotFound()
    try:
        full_path.relative_to(safe_path)
    except ValueError:
        raise NotFound()
    return full_path


def split_on_first(text: str, sep: str) -> typing.Tuple[str, str]:
    point = text.find(sep)
    if point == -1:
        return text, text[:0]  # return bytes or str
    return text[:point], text[point + len(sep) :]  # noqa: E203


def import_from_string(string: str):
    module = __import__(string.split(".")[0])
    for name in string.split(".")[1:]:
        module = getattr(module, name)
    return module


def address_to_str(address: typing.Tuple[str, int]) -> str:
    """Converts a ``(host, port)`` tuple into a ``host:port`` string."""
    return "{}:{}".format(*address)
