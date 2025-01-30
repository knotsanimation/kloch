import dataclasses
import logging
import shutil
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

    command_as_str: bool = False

    subprocess_kwargs: dict = dataclasses.field(default_factory=dict)
    """
    Mapping of kwargs to pass to python's 'subprocess.run' call.
    """

    expand_first_arg: bool = False

    def execute(self, tmpdir: Path, command: Optional[List[str]] = None):
        """
        Just call subprocess.run.
        """
        _command = self.command + (command or [])

        if self.expand_first_arg:
            toexpand = _command.pop(0)
            env_path = self.environ.get("PATH")
            expanded = shutil.which(toexpand, path=env_path)
            if not expanded:
                raise FileNotFoundError(
                    f"Could not expand the '{toexpand}' argument; "
                    f"searched PATH variable '{env_path}'"
                )
            _command.insert(0, expanded)

        if self.command_as_str:
            _command = subprocess.list2cmdline(_command)

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
