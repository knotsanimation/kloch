"""
We define a simple config system that describe how to build a software environment using
different "software launchers".

The config system can handle the merging of 2 configs structure.
"""

import copy
import dataclasses
from typing import Any
from typing import Dict
from typing import Optional

from kloch.launchers import LauncherSerializedDict


@dataclasses.dataclass
class EnvironmentProfile:
    """
    An environment is a collection of parameters required to start a pre-defined launcher.

    Environment can inherit each other by specifying a `base` attribute. The inheritance
    only merge the ``launchers`` attribute of the 2.
    """

    identifier: str
    version: str
    base: Optional["EnvironmentProfile"]
    launchers: LauncherSerializedDict

    @classmethod
    def from_dict(cls, serialized: Dict) -> "EnvironmentProfile":
        """
        Generate a profile instance from a serialized dict object.

        No type checking is performed and the user is reponsible for the correct
        type being stored in the dict.
        """
        identifier: str = serialized["identifier"]
        version: str = serialized["version"]
        base: Optional["EnvironmentProfile"] = serialized.get("base", None)
        launchers: LauncherSerializedDict = serialized["launchers"]

        return EnvironmentProfile(
            identifier=identifier,
            version=version,
            base=base,
            launchers=launchers,
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert a profile instance to a serialized dict object.
        """
        serialized = {
            "identifier": self.identifier,
            "version": self.version,
        }
        if self.base:
            serialized["base"] = self.base

        serialized["launchers"] = copy.deepcopy(self.launchers)
        return serialized

    def get_merged_profile(self):
        """
        Resolve the inheritance the profile might have over another profile.

        Returns:
            a new instance.
        """
        launchers = self.launchers
        if self.base:
            launchers = self.base.get_merged_profile().launchers + launchers

        return EnvironmentProfile(
            identifier=self.identifier,
            version=self.version,
            base=None,
            launchers=launchers,
        )
