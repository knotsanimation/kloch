import dataclasses
import logging
import os
import subprocess
from pathlib import Path
from typing import Any
from typing import Optional
from typing import Union

import yaml

from ._base import PackageManagerBase


LOGGER = logging.getLogger(__name__)


@dataclasses.dataclass
class RezEnvManager(PackageManagerBase):
    """
    A dataclass specifying how to create a rez environment.
    """

    requires: dict[str, str]
    params: list[str]
    config: dict
    environ: dict[str, Union[str, list[str]]] = dataclasses.field(default_factory=dict)

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
        for user_var, user_var_value in self.environ.items():
            if isinstance(user_var_value, list):
                user_var_value = [os.path.expandvars(arg) for arg in user_var_value]
                user_var_value = os.pathsep.join(user_var_value)
            envvars[user_var] = str(user_var_value)

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

    def to_dict(self) -> dict:
        return {
            "params": self.params,
            "requires": self.requires,
            "config": self.config,
            "environ": self.environ,
        }

    @classmethod
    def name(cls):
        return "rezenv"

    @classmethod
    def from_dict(cls, src_dict: dict[str, Any]) -> "RezEnvManager":
        rezroot = src_dict
        params = rezroot.get("params", [])
        package_requests = rezroot["requires"]
        config = rezroot.get("config", {})
        environ = rezroot.get("environ", {})
        return RezEnvManager(
            requires=package_requests,
            params=params,
            config=config,
            environ=environ,
        )
