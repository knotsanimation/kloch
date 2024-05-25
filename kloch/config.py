"""
A simple configuration system for the Kloch runtime.
"""

import dataclasses
import logging
import os
from pathlib import Path
from typing import Dict
from typing import List
from typing import Union

import yaml

LOGGER = logging.getLogger(__name__)

KLOCH_CONFIG_PREFIX = "KLOCH_CONFIG"

KLOCH_CONFIG_ENV_VAR = f"{KLOCH_CONFIG_PREFIX}_PATH"
"""
Environment variable that must specify a file path to an existing configuration file.
"""


@dataclasses.dataclass
class KlochConfig:
    """
    Configure kloch using a simple key/value pair dataclass system.
    """

    cli_logging_format: str = dataclasses.field(
        default="{levelname: <7} | {asctime} [{name}] {message}",
        metadata={
            "documentation": (
                "Formatting to use for all logged messages. See python logging module documentation.\n"
                "The tokens must use the ``{`` style."
            ),
            "environ": f"{KLOCH_CONFIG_PREFIX}_cli_logging_format".upper(),
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
            "environ": f"{KLOCH_CONFIG_PREFIX}_cli_logging_default_level".upper(),
            "environ_cast": str,
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
        environ = os.getenv(KLOCH_CONFIG_ENV_VAR)

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


def get_config() -> KlochConfig:
    """
    Get the current kloch configuration extracted from the environment.

    A default configuration is generated if no configuration file is specified.

    Returns:
        a new config instance
    """
    return KlochConfig.from_environment()
