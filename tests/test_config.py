import dataclasses
import logging

import pytest

import kloch.config


def test__KlochConfig():
    # ensure it doesn't raise errors
    kloch.config.KlochConfig()

    config = kloch.config.KlochConfig(cli_logging_default_level="DEBUG")
    assert config.cli_logging_default_level == logging.DEBUG
    config = kloch.config.KlochConfig(cli_logging_default_level=logging.DEBUG)
    assert config.cli_logging_default_level == "DEBUG"


def test__KlochConfig__from_environment(monkeypatch, data_dir):
    config = kloch.config.KlochConfig.from_environment()
    assert config is None

    config_path = data_dir / "config-blaj.yml"
    monkeypatch.setenv(kloch.config.KLOCH_CONFIG_ENV_VAR, str(config_path))
    config = kloch.config.KlochConfig.from_environment()
    assert config
    assert config.cli_logging_default_level == logging.WARNING
    assert config.cli_logging_format == "{levelname: <7}: {message}"


def test__KlochConfig__from_file(data_dir):
    config_path = data_dir / "config-molg.yml"
    with pytest.raises(TypeError) as error:
        config = kloch.config.KlochConfig.from_file(file_path=config_path)
        assert "NON_VALID_KEY" in error


def test__KlochConfig__documentation():
    for field in dataclasses.fields(kloch.config.KlochConfig):
        assert field.metadata.get("documentation")
