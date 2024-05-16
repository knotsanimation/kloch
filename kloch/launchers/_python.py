import dataclasses
import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import Annotated
from typing import Optional

from ._base import BaseLauncher


LOGGER = logging.getLogger(__name__)


@dataclasses.dataclass
class PythonLauncher(BaseLauncher):
    """
    A launcher that execute the given python file with kloch's own interpreter.
    """

    python_file: Annotated[
        str,
        "Filesystem path to an existing python file.",
        "The path will have environment variables expanded with ``os.expandvars`` [1]_.",
        "The path is turned absolute and normalized. [4]_",
    ] = dataclasses.field(default_factory=str)

    # we override only for the type hint
    command: Annotated[
        list[str],
        "Arbitrary list of command line arguments passed to the python file.",
    ] = dataclasses.field(default_factory=list)

    required_fields = ["python_file"]

    def execute(self, tmpdir: Path, command: Optional[list[str]] = None):
        """
        Just call ``subprocess.run`` with ``sys.executable`` + the file path
        """

        python_file = Path(os.path.expandvars(self.python_file)).absolute().resolve()

        # XXX: if packaged with nuitka, sys.executable is the built executable path,
        #   but we support this at the CLI level
        _command = [sys.executable, str(python_file)]
        _command += self.command + (command or [])

        LOGGER.debug(
            f"executing python command={_command}; environ={self.environ}; cwd={self.cwd}"
        )
        result = subprocess.run(_command, shell=True, env=self.environ, cwd=self.cwd)

        return result.returncode

    @classmethod
    def name(cls):
        # we add a @ in case the user want to add its own python launcher.
        return "@python"

    @classmethod
    def summary(cls) -> str:
        return "A launcher that execute the given python file with kloch's own interpreter."

    @classmethod
    def doc(cls) -> list[str]:
        return [
            "Execute the given python file with kloch internal python interpreter.",
            "",
            "All ``command`` keys are passed as args to the python script.",
        ]
