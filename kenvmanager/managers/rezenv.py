import dataclasses
import logging
import subprocess
from typing import Any
from typing import Optional

from ._base import PackageManagerProfileBase


LOGGER = logging.getLogger(__name__)


@dataclasses.dataclass
class RezEnvironmentProfile(PackageManagerProfileBase):
    """
    A datastructure that allow to create a rez environment.
    """

    requires: list[str]
    params: list[str]

    def execute(self, command: Optional[list[str]] = None):
        command = ["--"] + command if command else []
        full_command = ["rez-env"] + self.params + self.requires + command
        LOGGER.debug(f"executing interactive shell with command={full_command}")
        result = subprocess.run(full_command, shell=True)
        return result.returncode

    def to_dict(self) -> dict:
        return {
            "params": self.params,
            "requires": self.requires,
        }

    @classmethod
    def name(cls):
        return "rezenv"

    @classmethod
    def from_dict(cls, src_dict: dict[str, Any]) -> "RezEnvironmentProfile":
        rezroot = src_dict
        params = rezroot.get("params", [])
        package_requests = rezroot["requires"]
        return RezEnvironmentProfile(requires=package_requests, params=params)
