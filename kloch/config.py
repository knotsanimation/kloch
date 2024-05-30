"""
A simple configuration system for the Kloch runtime.
"""

import dataclasses
import logging
import os
from pathlib import Path
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

import yaml

from kloch.constants import Environ

LOGGER = logging.getLogger(__name__)


def _cast_list(src_str: str) -> List[str]:
    return src_str.split(",")


def _cast_path_list(src_str: str) -> List[Path]:
    return [Path(path) for path in src_str.split(os.pathsep)]


@dataclasses.dataclass
class KlochConfig:
    """
    Configure kloch using a simple key/value pair dataclass system.
    """

    launcher_plugins: List[str] = dataclasses.field(
        default_factory=list,
        metadata={
            "documentation": (
                "A list of importable python module names containing new launchers to support.\n\n"
                "If specified in environment variable, this must be a comma-separated list of str like ``module1,module2,module3``"
            ),
            "environ": Environ.KLOCH_CONFIG_LAUNCHER_PLUGINS,
            "environ_cast": _cast_list,
        },
    )

    cli_logging_paths: List[Path] = dataclasses.field(
        default_factory=list,
        metadata={
            "documentation": (
                "Filesystem path to one or multiple log file that might exists.\n"
                "If specified all the logging will be wrote to those files.\n\n"
                "If specified from the environment, it must a list of path separated "
                "by the default system path separator (windows = ``;``, linux = ``:``)"
            ),
            "environ": Environ.KLOCH_CONFIG_CLI_LOGGING_PATHS,
            "environ_cast": _cast_path_list,
        },
    )

    cli_logging_format: str = dataclasses.field(
        default="{levelname: <7} | {asctime} [{name}] {message}",
        metadata={
            "documentation": (
                "Formatting to use for all logged messages. See python logging module documentation.\n"
                "The tokens must use the ``{`` style."
            ),
            "environ": Environ.KLOCH_CONFIG_CLI_LOGGING_FORMAT,
            "environ_cast": str,
        },
    )

    cli_logging_default_level: Union[int, str] = dataclasses.field(
        default="INFO",
        metadata={
            "documentation": (
                "Logging level to use if None have been specified.\n"
                "Can be an int or a level name as string as long as it is understandable"
                " by ``logging.getLevelName``."
            ),
            "environ": Environ.KLOCH_CONFIG_CLI_LOGGING_DEFAULT_LEVEL,
            "environ_cast": str,
        },
    )

    profile_paths: List[Path] = dataclasses.field(
        default_factory=list,
        metadata={
            "documentation": (
                "Filesystem path to one or multiple directory that might exists.\n"
                "The directories contain profile valid to be discoverable.\n\n"
                "If specified from the environment, it must a list of path separated "
                "by the default system path separator (windows = ``;``, linux = ``:``)"
            ),
            "environ": Environ.KLOCH_CONFIG_PROFILE_PATHS,
            "environ_cast": _cast_path_list,
        },
    )

    @classmethod
    def from_file(cls, file_path: Path) -> "KlochConfig":
        """
        Generate an instance from a serialized file.
        """
        with file_path.open("r", encoding="utf-8") as file:
            asdict: Dict = yaml.safe_load(file)
        return cls(**asdict)

    @classmethod
    def from_environment(cls) -> "KlochConfig":
        """
        Generate an instance from a serialized file specified in an environment variable.
        """
        environ = os.getenv(Environ.KLOCH_CONFIG_ENV_VAR)

        asdict = {}
        if environ:
            base = cls.from_file(Path(environ))
            asdict = dataclasses.asdict(base)

        for field in dataclasses.fields(cls):
            env_var_name = field.metadata["environ"]
            env_var_value = os.getenv(env_var_name)
            if env_var_value is not None:
                value = field.metadata["environ_cast"](env_var_value)
                asdict[field.name] = value

        return cls(**asdict)

    @classmethod
    def get_field(cls, field_name: str) -> Optional[dataclasses.Field]:
        """
        Return the dataclass field that match the given name else None.
        """
        fields = dataclasses.fields(cls)
        field = [field for field in fields if field.name == field_name]
        return field[0] if field else None


def get_config() -> KlochConfig:
    """
    Get the current kloch configuration extracted from the environment.

    A default configuration is generated if no configuration file is specified.

    Returns:
        a new config instance
    """
    return KlochConfig.from_environment()
