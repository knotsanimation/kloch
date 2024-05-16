import dataclasses
import logging
import os
import subprocess
from pathlib import Path
from typing import Optional

from ._base import BaseLauncher


LOGGER = logging.getLogger(__name__)


@dataclasses.dataclass
class SystemLauncher(BaseLauncher):
    """
    A minimal launcher that just start a subprocess with the given command.
    """

    def execute(self, tmpdir: Path, command: Optional[list[str]] = None):
        """
        Just call subprocess.run.
        """
        _command = self.command + (command or [])

        LOGGER.debug(
            f"executing system command={_command}; environ={self.environ}; cwd={self.cwd}"
        )
        result = subprocess.run(_command, shell=True, env=self.environ, cwd=self.cwd)

        return result.returncode

    @classmethod
    def name(cls):
        return "system"

    @classmethod
    def summary(cls) -> str:
        return "A simple launcher executing the given command in the default system console."

    @classmethod
    def doc(cls) -> list[str]:
        return [
            "Useless without a command specified.",
            "The launcher will just set the given environment variables for the session, execute the command, then exit.",
        ]
