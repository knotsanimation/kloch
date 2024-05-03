import dataclasses
import logging
import os
import subprocess
from pathlib import Path
from typing import ClassVar
from typing import Optional

import yaml

from ._base import PackageManagerBase


LOGGER = logging.getLogger(__name__)


@dataclasses.dataclass
class RezEnvManager(PackageManagerBase):
    """
    A dataclass specifying how to create a rez environment.
    """

    requires: dict[str, str] = dataclasses.field(default_factory=dict)
    params: list[str] = dataclasses.field(default_factory=list)
    config: dict = dataclasses.field(default_factory=dict)

    required_fields: ClassVar[list[str]] = ["requires"]

    def execute(self, tmpdir: Path, command: Optional[list[str]] = None):
        """
        Start a rez environment by calling rez-env in a subprocess.

        If asked, a rez config is created on the fly before starting rez-env.
        """
        requires = [
            f"{pkg_name}-{pkg_version}"
            for pkg_name, pkg_version in self.requires.items()
        ]
        command = ["--"] + command if command else []
        full_command = ["rez-env"] + self.params + requires + command

        envvars = dict(os.environ)
        environ = self.get_resolved_environ()
        envvars.update(environ)

        if self.config:
            config_path = tmpdir / "rezconfig.yml"

            LOGGER.debug(f"writing config_path={config_path}")
            with config_path.open("w") as config_file:
                yaml.dump(self.config, config_file)

            env_config_path = envvars.get("REZ_CONFIG_FILE", "").split(os.pathsep)
            env_config_path.append(str(config_path))
            envvars["REZ_CONFIG_FILE"] = os.pathsep.join(env_config_path)

        LOGGER.debug(f"executing interactive shell with command={full_command}")
        result = subprocess.run(full_command, shell=True, env=envvars)

        return result.returncode

    @classmethod
    def name(cls):
        return "rezenv"
