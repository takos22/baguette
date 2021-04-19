import pytest

from baguette import Headers
from baguette.utils import get_encoding_from_headers


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
