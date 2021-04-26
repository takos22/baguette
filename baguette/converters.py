import abc
import math
import typing


class Converter(abc.ABC):
    @abc.abstractproperty
    def REGEX(self) -> str:
        ...

    @abc.abstractmethod
    def convert(self, string: str):
        ...


class StringConverter(Converter):
    REGEX = r"[^\/]+"

    def __init__(
        self,
        length: typing.Optional[int] = None,
        allow_slash: bool = False,
    ):
        self.length = length
        self.allow_slash = allow_slash
        if self.allow_slash:
            self.REGEX = r".+"

    def convert(self, string: str):
        if self.length is not None and len(string) != self.length:
            raise ValueError(
                f"Expected string of length {self.length}. Got {len(string)}"
            )

        if not self.allow_slash and "/" in string:
            raise ValueError(f"Expected string without '/'. Got {string!r}")

        return str(string)


class PathConverter(Converter):
    REGEX = r".+"

    def __init__(self):
        pass

    def convert(self, string: str):
        return string


class IntegerConverter(Converter):
    REGEX = r"[\+-]?\d+"

    def __init__(
        self,
        signed: bool = False,
        min: typing.Optional[int] = None,
        max: typing.Optional[int] = None,
    ):
        self.signed = signed
        self.min = min
        self.max = max

    def convert(self, string: str):
        if not self.signed and (string.strip()[0] in "+-"):
            raise ValueError(
                "Expected unsigned integer. Got integer starting with "
                + string.strip()[0]
            )

        integer = int(string)

        if self.min is not None and integer < self.min:
            raise ValueError(f"Expected integer higher than {self.min}")

        if self.max is not None and integer > self.max:
            raise ValueError(f"Expected integer lower than {self.max}")

        return integer


class FloatConverter(Converter):
    REGEX = r"[\+-]?\d*\.?\d*"

    def __init__(
        self,
        signed: bool = False,
        min: typing.Optional[float] = None,
        max: typing.Optional[float] = None,
        allow_infinity: bool = False,
        allow_nan: bool = False,
    ):
        self.signed = signed
        self.min = min
        self.max = max
        self.allow_infinity = allow_infinity
        self.allow_nan = allow_nan

    def convert(self, string: str):
        if not self.signed and (string.strip()[0] in "+-"):
            raise ValueError(
                "Expected unsigned float. Got float starting with "
                + string.strip()[0]
            )

        number = float(string)

        if self.min is not None and number < self.min:
            raise ValueError(f"Expected float higher than {self.min}")

        if self.max is not None and number > self.max:
            raise ValueError(f"Expected float lower than {self.max}")

        if not self.allow_infinity and math.isinf(number):
            raise ValueError(f"Expected a non-infinity value. Got {number}")

        if not self.allow_nan and math.isnan(number):
            raise ValueError(f"Expected a non-NaN value. Got {number}")

        return number
