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
        # XXX: if packaged with nuitka, sys.executable is the built executable path,
        #   but we support this at the CLI level
        _command = [sys.executable, self.python_file]
        _command += self.command + (command or [])

        envvars = dict(os.environ)
        environ = self.get_resolved_environ()
        envvars.update(environ)

        LOGGER.debug(f"executing system command={_command} with environ={envvars}")
        result = subprocess.run(_command, shell=True, env=envvars)

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
