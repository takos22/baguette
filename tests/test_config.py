import pytest

from baguette.config import Config


def test_config_create():
    config = Config(
        debug=True,
        static_directory="tests/static",
        templates_directory="tests/templates",
        error_response_type="html",
        error_include_description=False,
    )
    assert config.debug
    assert config.static_directory == "tests/static"
    assert config.templates_directory == "tests/templates"
    assert config.error_response_type == "html"
    assert config.error_include_description


def test_config_create_error():
    with pytest.raises(ValueError):
        Config(error_response_type="bad type")


def test_config_from_json():
    config = Config.from_json("tests/configs/config.json")
    assert config.debug
    assert config.static_directory == "tests/static"
    assert config.templates_directory == "tests/templates"
    assert config.error_response_type == "html"
    assert config.error_include_description


def test_config_from_json_error():
    with pytest.raises(ValueError):
        Config.from_json("tests/configs/bad_config.json")


def test_config_from_class():
    from tests.configs.config import Configuration

    config = Config.from_class(Configuration)
    assert config.debug
    assert config.static_directory == "tests/static"
    assert config.templates_directory == "tests/templates"
    assert config.error_response_type == "html"
    assert config.error_include_description


def test_config_from_class_string():
    config = Config.from_class("tests.configs.config.Configuration")
    assert config.debug
    assert config.static_directory == "tests/static"
    assert config.templates_directory == "tests/templates"
    assert config.error_response_type == "html"
    assert config.error_include_description


def test_config_from_module():
    from tests.configs import config_module

    config = Config.from_class(config_module)
    assert config.debug
    assert config.static_directory == "tests/static"
    assert config.templates_directory == "tests/templates"
    assert config.error_response_type == "html"
    assert config.error_include_description


def test_config_from_module_string():
    config = Config.from_class("tests.configs.config_module")
    assert config.debug
    assert config.static_directory == "tests/static"
    assert config.templates_directory == "tests/templates"
    assert config.error_response_type == "html"
    assert config.error_include_description
