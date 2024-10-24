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
    A profile is a collection of parameters required to start a pre-defined launcher.

    This can be seen as the context/environment necessary to run a launcher thus its
    full name 'Environment Profile' that we abbreviate to profile for convenience.

    Profiles can inherit each other by specifying a `inherit` attribute. The inheritance
    only merge the content of the ``launchers`` attribute between 2 profiles.
    """

    identifier: str
    version: str
    inherit: Optional["EnvironmentProfile"]
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
        inherit: Optional["EnvironmentProfile"] = serialized.get("inherit", None)
        launchers: LauncherSerializedDict = serialized["launchers"]

        return EnvironmentProfile(
            identifier=identifier,
            version=version,
            inherit=inherit,
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
        if self.inherit:
            serialized["inherit"] = self.inherit

        serialized["launchers"] = copy.deepcopy(self.launchers)
        return serialized

    def get_merged_profile(self):
        """
        Resolve the inheritance the profile might have over another profile.

        Returns:
            a new instance.
        """
        launchers = self.launchers
        if self.inherit:
            launchers = self.inherit.get_merged_profile().launchers + launchers

        return EnvironmentProfile(
            identifier=self.identifier,
            version=self.version,
            inherit=None,
            launchers=launchers,
        )
