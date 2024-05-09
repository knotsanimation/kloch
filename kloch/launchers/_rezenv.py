import dataclasses
import logging
import os
import subprocess
from pathlib import Path
from typing import Annotated
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

    requires: Annotated[
        dict[str, str],
        "mapping of rez `package name`: `package version`",
    ] = dataclasses.field(default_factory=dict)

    params: Annotated[
        list[str],
        "list of command line arguments passed to rez-env.",
        "",
        "Check the `rez documentation <https://rez.readthedocs.io/en/stable/commands/rez-env.html>`_.",
    ] = dataclasses.field(default_factory=list)

    config: Annotated[
        dict[...],
        "content of a valid yaml rez config that is created on the fly before the rez-env.",
    ] = dataclasses.field(default_factory=dict)

    required_fields: ClassVar[list[str]] = []

    def execute(self, tmpdir: Path, command: Optional[list[str]] = None):
        """
        Start a rez environment by calling rez-env in a subprocess.

        If asked, a rez config is created on the fly before starting rez-env.
        """
        requires = [
            f"{pkg_name}-{pkg_version}"
            for pkg_name, pkg_version in self.requires.items()
        ]

        command = self.command + (command or [])
        command = ["--"] + command if command else []
        full_command = ["rez-env"] + self.params + requires + command

        envvars = dict(os.environ)
        environ = self.get_resolved_environ()
        envvars.update(environ)

        if self.config:
            config_path = tmpdir / "rezconfig.yml"

            LOGGER.debug(f"writing config_path={config_path}")
            with config_path.open("w", encoding="utf-8") as config_file:
                yaml.dump(self.config, config_file)

            env_config_path = envvars.get("REZ_CONFIG_FILE", "").split(os.pathsep)
            env_config_path.append(str(config_path))
            envvars["REZ_CONFIG_FILE"] = os.pathsep.join(env_config_path)

        LOGGER.debug(
            f"executing interactive shell with command={full_command} and env={envvars}"
        )
        result = subprocess.run(full_command, shell=True, env=envvars)

        return result.returncode

    @classmethod
    def name(cls):
        return "rezenv"

    @classmethod
    def summary(cls) -> str:
        return "Start an interactive rez shell using the ``rez-env`` command."

    @classmethod
    def doc(cls) -> list[str]:
        return ["The implementation will call ``rez-env`` in a python subprocess [3]_."]
