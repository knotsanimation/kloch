"""
A simple configuration system for the Kloch runtime.
"""

import dataclasses
import logging
import os
from pathlib import Path
from typing import Dict
from typing import Optional
from typing import Union

import yaml

LOGGER = logging.getLogger(__name__)

KLOCH_CONFIG_ENV_VAR = "KLOCH_CONFIG_PATH"
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
            )
        },
    )

    cli_logging_default_level: Union[int, str] = dataclasses.field(
        default="INFO",
        metadata={
            "documentation": (
                "Logging level to use if None have been specified.\n"
                "Can be an int or a level name as string as long as it is understandable"
                " by ``logging.getLevelName``."
            )
        },
    )

    def __post_init__(self):
        self.cli_logging_default_level = logging.getLevelName(
            self.cli_logging_default_level
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
    def from_environment(cls) -> Optional["KlochConfig"]:
        """
        Generate an instance from a serialized file specified in an environment variable.
        """
        environ = os.getenv(KLOCH_CONFIG_ENV_VAR)
        if not environ:
            return None
        return cls.from_file(Path(environ))


def get_config() -> KlochConfig:
    """
    Get the current kloch configuration extracted from the environment.

    A default configuration is generated if no configuration file is specified.

    Returns:
        a new config instance
    """
    config = KlochConfig.from_environment()
    return config or KlochConfig()
