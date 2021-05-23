import cgi
import os
import pathlib
import typing

from .httpexceptions import NotFound
from .types import FilePath, StrOrBytes


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


def to_bytes(str_or_bytes: StrOrBytes, encoding="utf-8") -> bytes:
    """Makes sure that the argument is a :class:`bytes`.

    Arguments
    ---------
        str_or_bytes : :class:`str` or :class:`bytes`
            The argument to convert to a :class:`bytes`.

        encoding : Optional :class:`str`
            The string encoding.
            Default: ``"utf-8"``

    Returns
    -------
        :class:`bytes`
            The converted argument.

    Raises
    ------
        TypeError
            The argument isn't a :class:`str` or a :class:`bytes`.
    """

    if not isinstance(str_or_bytes, (str, bytes)):
        raise TypeError(
            "str_or_bytes must be of type str or bytes. Got: "
            + str_or_bytes.__class__.__name__
        )
    return (
        str_or_bytes.encode(encoding=encoding)
        if isinstance(str_or_bytes, str)
        else str_or_bytes
    )


def to_str(str_or_bytes: StrOrBytes, encoding="utf-8") -> str:
    """Makes sure that the argument is a :class:`str`.

    Arguments
    ---------
        str_or_bytes : :class:`str` or :class:`bytes`
            The argument to convert to a :class:`bytes`.

        encoding : Optional :class:`str`
            The bytes encoding.
            Default: ``"utf-8"``

    Returns
    -------
        :class:`str`
            The converted argument.

    Raises
    ------
        TypeError
            The argument isn't a :class:`str` or a :class:`bytes`.
    """

    if not isinstance(str_or_bytes, (str, bytes)):
        raise TypeError(
            "str_or_bytes must be of type str or bytes. Got: "
            + str_or_bytes.__class__.__name__
        )
    return (
        str_or_bytes.decode(encoding=encoding)
        if isinstance(str_or_bytes, bytes)
        else str_or_bytes
    )
