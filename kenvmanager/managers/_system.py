import dataclasses
import logging
import os
import subprocess
from pathlib import Path
from typing import Optional

from ._base import PackageManagerBase


LOGGER = logging.getLogger(__name__)


@dataclasses.dataclass
class SystemManager(PackageManagerBase):
    """
    A minimal manager that just start a subprocess.
    """

    def execute(self, tmpdir: Path, command: Optional[list[str]] = None):
        """
        Just call subprocess.run.
        """
        envvars = dict(os.environ)
        environ = self.get_resolved_environ()
        envvars.update(environ)

        LOGGER.debug(f"executing system command={command}")
        result = subprocess.run(command or [], shell=True, env=envvars)

        return result.returncode

    @classmethod
    def name(cls):
        return "system"

    @classmethod
    def summary(cls) -> str:
        return "A simple manager executing the given command in the default system console."

    @classmethod
    def doc(cls) -> list[str]:
        return [
            "Intended to be used with a command.",
            "The manager will just set the given environment variables, execute the command, then exit.",
        ]
