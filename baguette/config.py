import json

from .headers import Headers, make_headers
from .types import HeadersType
from .utils import import_from_string


class Config:
    """Baguette application configuration.

    Keyword Arguments
    -----------------
        debug : :class:`bool`
            Whether to run the application in debug mode.
            Default: ``False``.

        default_headers : :class:`list` of ``(str, str)`` tuples, \
        :class:`dict` or :class:`Headers`
            Default headers to include in every response.
            Default: No headers.

        static_url_path : :class:`str`
            URL path for the static file handler.
            Default: ``"static"``.

        static_directory : :class:`str`
            Path to the folder containing static files.
            Default: ``"static"``.

        templates_directory : :class:`str`
            Path to the folder containing the HTML templates.
            Default: ``"templates"``.

        error_response_type : :class:`str`
            Type of response to use in case of error.
            One of: ``"plain"``, ``"json"``, ``"html"``.
            Default: ``"plain"``.

        error_include_description : :class:`bool`
            Whether to include the error description in the response
            in case of error.
            If debug is ``True``, this will also be ``True``.
            Default: ``True``.


    Attributes
    ----------
        debug : :class:`bool`
            Whether the application is running in debug mode.

        default_headers : :class:`Headers`
            Default headers included in every response.

        static_url_path : :class:`str`
            URL path for the static file handler.

        static_directory : :class:`str`
            Path to the folder containing static files.

        templates_directory : :class:`str`
            Path to the folder containing the HTML templates.

        error_response_type : :class:`str`
            Type of response to use in case of error.
            One of: ``"plain"``, ``"json"``, ``"html"``

        error_include_description : :class:`bool`
            Whether the error description is included in the response
            in case of error.
            If debug is ``True``, this will also be ``True``.
    """

    def __init__(
        self,
        *,
        debug: bool = False,
        default_headers: HeadersType = None,
        static_url_path: str = "static",
        static_directory: str = "static",
        templates_directory: str = "static",
        error_response_type: str = "plain",
        error_include_description: bool = True,
    ):
        self.debug = debug
        self.default_headers: Headers = make_headers(default_headers)

        self.static_url_path = static_url_path
        self.static_directory = static_directory
        self.templates_directory = templates_directory

        if error_response_type not in ("plain", "json", "html"):
            raise ValueError(
                "Bad response type. Must be one of: 'plain', 'json', 'html'"
            )
        self.error_response_type = error_response_type
        self.error_include_description = error_include_description or self.debug

    @classmethod
    def from_json(cls, filename: str) -> "Config":
        """Loads the configuration from a JSON file.

        Arguments
        ---------
            filename : :class:`str`
                The file name of the JSON config file.

        Returns
        -------
            :class:`Config`
                The loaded configuration.
        """

        with open(filename) as config_file:
            config = json.load(config_file)

        if not isinstance(config, dict):
            raise ValueError(
                f"Configuration must be a dictionary. Got: {type(config)}"
            )

        return cls(**config)

    @classmethod
    def from_class(cls, class_or_module_name) -> "Config":
        """Loads the configuration from a python class.

        Arguments
        ---------
            class_or_module_name : class or :class:`str`
                The class to load the configuration.

        Returns
        -------
            :class:`Config`
                The loaded configuration.
        """

        if isinstance(class_or_module_name, str):
            config_class = import_from_string(class_or_module_name)
        else:
            config_class = class_or_module_name

        config = {}
        for attribute in (
            "debug",
            "default_headers",
            "static_url_path",
            "static_directory",
            "templates_directory",
            "error_response_type",
            "error_include_description",
        ):
            if hasattr(config_class, attribute):
                config[attribute] = getattr(config_class, attribute)
            elif hasattr(config_class, attribute.upper()):
                config[attribute] = getattr(config_class, attribute.upper())

        return cls(**config)
