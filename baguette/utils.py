import cgi
import os
import pathlib
import typing

from .httpexceptions import NotFound


def get_encoding_from_headers(headers):
    """Returns encodings from given HTTP Headers."""

    content_type = headers.get("content-type")

    if not content_type:
        return None

    content_type, params = cgi.parse_header(content_type)

    if "charset" in params:
        return params["charset"].strip("'\"")

    if "text" in content_type:
        return "ISO-8859-1"


FilePath = typing.Union[bytes, str, os.PathLike]


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
