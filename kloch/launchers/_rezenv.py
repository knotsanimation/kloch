import dataclasses
import logging
import os
import subprocess
from pathlib import Path
from typing import ClassVar
from typing import Optional

import yaml

from ._base import BaseLauncher


LOGGER = logging.getLogger(__name__)


@dataclasses.dataclass
class RezEnvLauncher(BaseLauncher):
    """
    Describe how to start a rez shell interactive session.
    """

    requires: dict[str, str] = dataclasses.field(default_factory=dict)

    params: list[str] = dataclasses.field(default_factory=list)

    config: dict = dataclasses.field(default_factory=dict)

    required_fields: ClassVar[list[str]] = []

    name = "rezenv"

    def execute(self, tmpdir: Path, command: Optional[list[str]] = None):
        """
        Start a rez environment by calling rez-env in a subprocess.

        If asked, a rez config is created on the fly before starting rez-env.
        """
        requires = [
            f"{pkg_name}-{pkg_version}"
            for pkg_name, pkg_version in self.requires.items()
        ]

        _command = self.command + (command or [])
        _command = ["--"] + command if command else []
        _command = ["rez-env"] + self.params + requires + _command

        environ = self.environ.copy()

        if self.config:
            config_path = tmpdir / "rezconfig.yml"

            LOGGER.debug(f"writing config_path={config_path}")
            with config_path.open("w", encoding="utf-8") as config_file:
                yaml.dump(self.config, config_file)

            env_config_path = environ.get("REZ_CONFIG_FILE", "").split(os.pathsep)
            env_config_path.append(str(config_path))
            environ["REZ_CONFIG_FILE"] = os.pathsep.join(env_config_path)

        LOGGER.debug(
            f"executing rez command={_command}; environ={environ}; cwd={self.cwd}"
        )
        result = subprocess.run(_command, shell=True, env=environ, cwd=self.cwd)

        return result.returncode
