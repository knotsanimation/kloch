import dataclasses
import logging
import os
import subprocess
from pathlib import Path
from typing import Any
from typing import Optional

import yaml

from ._base import PackageManagerProfileBase


LOGGER = logging.getLogger(__name__)


@dataclasses.dataclass
class RezEnvironmentProfile(PackageManagerProfileBase):
    """
    A datastructure that allow to create a rez environment.
    """

    requires: list[str]
    params: list[str]
    config: dict

    def execute(self, tmpdir: Path, command: Optional[list[str]] = None):
        command = ["--"] + command if command else []
        full_command = ["rez-env"] + self.params + self.requires + command

        envvars = dict(os.environ)

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
        }

    @classmethod
    def name(cls):
        return "rezenv"

    @classmethod
    def from_dict(cls, src_dict: dict[str, Any]) -> "RezEnvironmentProfile":
        rezroot = src_dict
        params = rezroot.get("params", [])
        package_requests = rezroot["requires"]
        config = rezroot.get("config", {})
        return RezEnvironmentProfile(
            requires=package_requests,
            params=params,
            config=config,
        )
