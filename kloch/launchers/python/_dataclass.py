import dataclasses
import logging
import subprocess
import sys
from pathlib import Path
from typing import List
from typing import Optional

from kloch.launchers import BaseLauncher


LOGGER = logging.getLogger(__name__)


@dataclasses.dataclass
class PythonLauncher(BaseLauncher):
    """
    A launcher that execute the given python file with kloch's own interpreter.
    """

    python_file: str = None
    """
    Filesystem path to an existing python file.
    """

    required_fields = ["python_file"]

    name = "@python"

    def execute(self, tmpdir: Path, command: Optional[List[str]] = None):
        """
        Just call ``subprocess.run`` with ``sys.executable`` + the file path
        """
        # XXX: if packaged with nuitka, sys.executable is the built executable path,
        #   but we support this at the CLI level
        _command = [sys.executable, self.python_file]
        _command += self.command + (command or [])

        LOGGER.debug(
            f"executing python command={_command}; environ={self.environ}; cwd={self.cwd}"
        )
        result = subprocess.run(_command, env=self.environ, cwd=self.cwd)

        return result.returncode
