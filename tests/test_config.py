import dataclasses
import logging
from pathlib import Path

import pytest

import kloch.config


def test__KlochConfig():
    # ensure it doesn't raise errors
    kloch.config.KlochConfig()

    config = kloch.config.KlochConfig(cli_logging_default_level="DEBUG")
    assert config.cli_logging_default_level == "DEBUG"
    config = kloch.config.KlochConfig(cli_logging_default_level=logging.DEBUG)
    assert config.cli_logging_default_level == logging.DEBUG

    field = kloch.config.KlochConfig.get_field("cli_logging_default_level")
    assert field.name == "cli_logging_default_level"


def test__KlochConfig__from_environment(monkeypatch, data_dir):
    config = kloch.config.KlochConfig.from_environment()
    assert config == kloch.config.KlochConfig()

    config_path = data_dir / "config-blaj.yml"
    monkeypatch.setenv(kloch.Environ.CONFIG_PATH, str(config_path))
    config = kloch.config.KlochConfig.from_environment()
    assert config.cli_logging_default_level == "WARNING"
    assert config.cli_logging_format == "{levelname: <7}: {message}"
    assert len(config.cli_logging_paths) == 2
    assert isinstance(config.cli_logging_paths[0], Path)
    assert isinstance(config.cli_session_dir, Path)
    assert str(config.cli_session_dir) == str(config_path.parent / ".session")
    assert str(config.cli_logging_paths[0]) == str(
        config_path.parent / "tmp" / "kloch.log"
    )

    monkeypatch.setenv("KLOCH_CONFIG_CLI_LOGGING_DEFAULT_LEVEL", "ERROR")
    config = kloch.config.KlochConfig.from_environment()
    assert config.cli_logging_default_level == "ERROR"
    assert config.cli_logging_format == "{levelname: <7}: {message}"


def test__KlochConfig__from_file__expandvar(monkeypatch, data_dir, tmp_path: Path):
    monkeypatch.setenv("FOOBAR", str(tmp_path))
    monkeypatch.setenv("THIRDIR", str(tmp_path / "third"))

    config_path = data_dir / "config-fuel.yml"
    config = kloch.config.KlochConfig.from_file(file_path=config_path)
    assert len(config.cli_logging_paths) == 2
    assert config.cli_logging_paths[0] == tmp_path / "kloch.log"
    assert config.cli_logging_paths[1] == config_path.parent / Path(
        "$FOOBAR/tmp/kloch2.log"
    )
    assert config.cli_session_dir == Path(tmp_path / "third" / ".session")


def test__KlochConfig__from_file__error(data_dir):
    config_path = data_dir / "config-molg.yml"
    with pytest.raises(TypeError) as error:
        config = kloch.config.KlochConfig.from_file(file_path=config_path)
    assert "NON_VALID_KEY" in str(error.value)


def test__KlochConfig__documentation():
    for field in dataclasses.fields(kloch.config.KlochConfig):
        assert field.metadata.get("documentation")
        config_cast = field.metadata.get("config_cast")
        assert config_cast
        # check the caster accept 2 arguments
        try:
            config_cast({}, Path())
        except TypeError:
            pass
        assert field.metadata.get("environ")
        assert field.metadata.get("environ_cast")
