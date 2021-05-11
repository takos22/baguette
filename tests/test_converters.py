import pytest

from baguette.converters import (
    Converter,
    FloatConverter,
    IntegerConverter,
    PathConverter,
    StringConverter,
)

from .conftest import concreter


@pytest.mark.parametrize(
    ["converter", "string", "expected"],
    [
        # string converters
        [StringConverter(), "test", "test"],
        [StringConverter(length=4), "test", "test"],
        [StringConverter(allow_slash=True), "test/test", "test/test"],
        # path converters
        [PathConverter(), "test", "test"],
        [PathConverter(), "test/test", "test/test"],
        [PathConverter(allow_empty=True), "test", "test"],
        [PathConverter(allow_empty=True), "test/test", "test/test"],
        [PathConverter(allow_empty=True), "", ""],
        # integer converters
        [IntegerConverter(), "1", 1],
        [IntegerConverter(signed=True), "+1", 1],
        [IntegerConverter(signed=True), "-1", -1],
        [IntegerConverter(min=0), "1", 1],
        [IntegerConverter(min=1), "1", 1],
        [IntegerConverter(max=1), "1", 1],
        [IntegerConverter(max=2), "1", 1],
        # float converters
        [FloatConverter(), "1", 1.0],
        [FloatConverter(), "1.", 1.0],
        [FloatConverter(), "1.0", 1.0],
        [FloatConverter(), ".1", 0.1],
        [FloatConverter(), "0.1", 0.1],
        [FloatConverter(signed=True), "+1.0", 1.0],
        [FloatConverter(signed=True), "-1.0", -1.0],
        [FloatConverter(min=0), "1.0", 1.0],
        [FloatConverter(min=0.0), "1.0", 1.0],
        [FloatConverter(min=1), "1.0", 1.0],
        [FloatConverter(min=1.0), "1.0", 1.0],
        [FloatConverter(max=1), "1.0", 1.0],
        [FloatConverter(max=1.0), "1.0", 1.0],
        [FloatConverter(max=2), "1.0", 1.0],
        [FloatConverter(max=2.0), "1.0", 1.0],
        [FloatConverter(allow_infinity=True), "inf", float("inf")],
        [
            FloatConverter(signed=True, allow_infinity=True),
            "+inf",
            float("inf"),
        ],
        [
            FloatConverter(signed=True, allow_infinity=True),
            "-inf",
            float("-inf"),
        ],
        [FloatConverter(allow_nan=True), "nan", float("nan")],
    ],
)
def test_converter(converter: Converter, string: str, expected):
    assert converter.convert(string) == pytest.approx(expected, nan_ok=True)


@pytest.mark.parametrize(
    ["converter", "string"],
    [
        # string converters
        [StringConverter(), "test/test"],
        [StringConverter(length=1), "test"],
        # path converters
        [PathConverter(), ""],
        # integer converters
        [IntegerConverter(), "text"],
        [IntegerConverter(), "+1"],
        [IntegerConverter(), "-1"],
        [IntegerConverter(min=1), "0"],
        [IntegerConverter(max=1), "2"],
        # float converters
        [FloatConverter(), "text"],
        [FloatConverter(), "+1.0"],
        [FloatConverter(), "-1.0"],
        [FloatConverter(), "inf"],
        [FloatConverter(), "nan"],
        [FloatConverter(min=1.0), "0.0"],
        [FloatConverter(max=1.0), "2.0"],
    ],
)
def test_converter_error(converter, string):
    with pytest.raises(ValueError):
        converter.convert(string)


def test_abstract_converter():
    converter = concreter(Converter)()
    # run the code for coverage
    converter.REGEX
    converter.convert("test")
