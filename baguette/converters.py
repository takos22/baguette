import abc
import math
import typing


class Converter(abc.ABC):
    @abc.abstractmethod
    def convert(self, string: str):
        ...


class StringConverter(Converter):
    def __init__(self, length: typing.Optional[int] = None):
        self.length = length

    def convert(self, string: str):
        if self.length is not None and len(string) != self.length:
            raise ValueError(
                f"Expected string of length {self.length}. Got {len(string)}"
            )

        return str(string)


class IntegerConverter(Converter):
    def __init__(
        self,
        base: int = 10,
        signed: bool = False,
        min: typing.Optional[int] = None,
        max: typing.Optional[int] = None,
    ):
        self.base = base
        self.signed = signed
        self.min = min
        self.max = max

    def convert(self, string: str):
        if not self.signed and (string.strip()[0] in "+-"):
            raise ValueError(
                "Expected unsigned integer. Got integer starting with "
                + string.strip()[0]
            )

        integer = int(string, base=self.base)

        if self.min is not None and integer < self.min:
            raise ValueError(f"Expected integer higher than {self.min}")

        if self.max is not None and integer > self.max:
            raise ValueError(f"Expected integer lower than {self.max}")

        return integer


class FloatConverter(Converter):
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
