import dataclasses
import logging
import subprocess
from pathlib import Path
from typing import List
from typing import Optional

from kloch.launchers import BaseLauncher


LOGGER = logging.getLogger(__name__)


@dataclasses.dataclass
class SystemLauncher(BaseLauncher):
    """
    A minimal launcher that just start a subprocess with the given command.
    """

    name = "system"

    def execute(self, tmpdir: Path, command: Optional[List[str]] = None):
        """
        Just call subprocess.run.
        """
        _command = self.command + (command or [])

        LOGGER.debug(
            f"executing system command={_command}; environ={self.environ}; cwd={self.cwd}"
        )
        result = subprocess.run(_command, shell=True, env=self.environ, cwd=self.cwd)

        return result.returncode
