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

    name = ".system"

    subprocess_kwargs: dict = dataclasses.field(default_factory=dict)
    """
    Mapping of kwargs to pass to python's 'subprocess.run' call.
    """

    def execute(self, tmpdir: Path, command: Optional[List[str]] = None):
        """
        Just call subprocess.run.
        """
        _command = self.command + (command or [])

        LOGGER.debug(
            f"subprocess.run({_command}, env={self.environ}, cwd={self.cwd}, **{self.subprocess_kwargs})"
        )
        result = subprocess.run(
            _command,
            env=self.environ,
            cwd=self.cwd,
            **self.subprocess_kwargs,
        )

        return result.returncode
