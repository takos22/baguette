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
    """Converter for string URL parameters.

    Arguments
    ---------
        length : Optional :class:`int`
            Required length of the string.
            Default: ``None``

        allow_slash : Optional :class:`bool`
            Allow slashes in the string.
            Default: ``False``

    Attributes
    ----------
        length : Optional :class:`int`
            Required length of the string.

        allow_slash : :class:`bool`
            Allow slashes in the string.

        REGEX : :class:`str`
            Regex for the route :meth:`~baguette.router.Route.build_regex`.
    """

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
        """Converts the string of the URL parameter and validates the value.

        Arguments
        ---------
            string : :class:`str`
                URL parameter to convert.

        Returns
        -------
            :class:`str`
                Converted URL parameter.

        Raises
        ------
            ValueError
                :attr:`length` is specified and the URL parameter has a
                different length than :attr:`length`.

            ValueError
                :attr:`allow_slash` is ``False`` and the URL parameter
                contains slashes.
        """

        if self.length is not None and len(string) != self.length:
            raise ValueError(
                f"Expected string of length {self.length}. Got {len(string)}"
            )

        if not self.allow_slash and "/" in string:
            raise ValueError(f"Expected string without '/'. Got {string!r}")

        return str(string)


class PathConverter(Converter):
    """Converter for string URL parameters.

    Arguments
    ---------
        allow_empty : Optional :class:`bool`
            Whether to allow empty paths.
            Default: ``False``

    Attributes
    ----------
        allow_empty : :class:`bool`
            Whether to allow empty paths.

        REGEX : :class:`str`
            Regex for the route :meth:`~baguette.router.Route.build_regex`.
    """

    REGEX = r".+"

    def __init__(self, allow_empty: bool = False):
        self.allow_empty = allow_empty
        if self.allow_empty:
            self.REGEX = r".*"

    def convert(self, string: str):
        """Converts the string of the URL parameter and validates the value.

        Arguments
        ---------
            string : :class:`str`
                URL parameter to convert.

        Returns
        -------
            :class:`str`
                Converted URL parameter.

        Raises
        ------
            ValueError
                :attr:`allow_empty` is ``True`` and the path is empty.
        """

        if not self.allow_empty and string == "":
            raise ValueError("Path cannot be empty")

        return string.strip("/")


class IntegerConverter(Converter):
    """Converter for integer URL parameters.

    Arguments
    ---------
        signed : Optional :class:`bool`
            Whether to accept integers starting with ``+`` or ``-``.
            Default: ``False``

        min : Optional :class:`int`
            Minimum value of the integer.
            Default: ``None``

        max : Optional :class:`int`
            Maximum value of the integer.
            Default: ``None``

    Attributes
    ----------
        signed : :class:`bool`
            Whether to accept integers starting with ``+`` or ``-``.

        min : Optional :class:`int`
            Minimum value of the integer.

        max : Optional :class:`int`
            Maximum value of the integer.

        REGEX : :class:`str`
            Regex for the route :meth:`~baguette.router.Route.build_regex`.
    """

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
        """Converts the string of the URL parameter and validates the value.

        Arguments
        ---------
            string : :class:`str`
                URL parameter to convert.

        Returns
        -------
            :class:`int`
                Converted URL parameter.

        Raises
        ------
            ValueError
                :attr:`signed` is ``False`` and the URL parameter starts
                with ``+`` or ``-``.

            ValueError
                Couldn't convert the URL parameter to an integer.

            ValueError
                :attr:`min` is specified and the URL parameter
                is lower then :attr:`min`.

            ValueError
                :attr:`max` is specified and the URL parameter
                is higher then :attr:`max`.
        """

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
    """Converter for float URL parameters.

    Arguments
    ---------
        signed : Optional :class:`bool`
            Whether to accept floats starting with ``+`` or ``-``.
            Default: ``False``

        min : Optional :class:`float`
            Minimum value of the float.
            Default: ``None``

        max : Optional :class:`float`
            Maximum value of the float.
            Default: ``None``

        allow_infinity : Optional :class:`bool`
            Whether to accept floats that are ``inf`` or ``-inf``.
            Default: ``False``

        allow_nan : Optional :class:`bool`
            Whether to accept floats that are ``NaN``.
            Default: ``False``

    Attributes
    ----------
        signed : :class:`bool`
            Whether to accept floats starting with ``+`` or ``-``.

        min : Optional :class:`float`
            Minimum value of the float.

        max : Optional :class:`float`
            Maximum value of the float.

        allow_infinity : :class:`bool`
            Whether to accept floats that are ``inf`` or ``-inf``.

        allow_nan : :class:`bool`
            Whether to accept floats that are ``NaN``.

        REGEX : :class:`str`
            Regex for the route :meth:`~baguette.router.Route.build_regex`.
    """

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
        """Converts the string of the URL parameter and validates the value.

        Arguments
        ---------
            string : :class:`str`
                URL parameter to convert.

        Returns
        -------
            :class:`float`
                Converted URL parameter.

        Raises
        ------
            ValueError
                :attr:`signed` is ``False`` and the URL parameter starts
                with ``+`` or ``-``.

            ValueError
                Couldn't convert the URL parameter to an float.

            ValueError
                :attr:`min` is specified and the URL parameter
                is lower then :attr:`min`.

            ValueError
                :attr:`max` is specified and the URL parameter
                is higher then :attr:`max`.

            ValueError
                :attr:`allow_infinity` is ``False`` and the URL parameter
                is ``inf`` or ``-inf``.

            ValueError
                :attr:`allow_nan` is ``False`` and the URL parameter
                is ``nan``.
        """

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
