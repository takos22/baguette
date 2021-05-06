import pytest

from baguette.forms import Field, FileField


@pytest.mark.parametrize(
    ["values", "expected_value"],
    [
        [[], None],
        [["test"], "test"],
        [[b"test"], "test"],
        [["test", "test2"], "test"],
        [[b"test", "test2"], "test"],
        [["test", b"test2"], "test"],
        [[b"test", b"test2"], "test"],
    ],
)
def test_field(values, expected_value):
    field = Field("test", values)
    assert field.value == expected_value


@pytest.mark.parametrize(
    ["content", "expected_text"],
    [
        ["", ""],
        [b"", ""],
        ["test", "test"],
        [b"test", "test"],
        [chr(129), chr(129)],
        [chr(129).encode("utf-8"), chr(129).encode("utf-8")],
    ],
)
def test_file_field(content, expected_text):
    field = FileField("test", content, encoding="ascii")
    assert field.text == expected_text
