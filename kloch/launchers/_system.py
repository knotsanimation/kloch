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
        command = self.command + (command or [])

        envvars = dict(os.environ)
        environ = self.get_resolved_environ()
        envvars.update(environ)

        LOGGER.debug(f"executing system command={command}")
        result = subprocess.run(command, shell=True, env=envvars)

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
