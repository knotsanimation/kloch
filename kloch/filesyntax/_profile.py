"""
We define a simple config system that describe how to build a software environment using
different "software launchers".

The config system can handle the merging of 2 configs structure.
"""

import copy
import dataclasses
from typing import Any
from typing import Optional

from ._merging import refacto_dict
from ._merging import deepmerge_dicts
from ._merging import MergeRule
from kloch.launchers import get_launcher_class
from kloch.launchers import BaseLauncher


def _resolve_key_tokens(key: str) -> str:
    return key.removeprefix("+=").removeprefix("-=")


def _merge_tokenized_dict(base_dict: dict, over_dict: dict):
    def merge_rule(key: str):
        if key.startswith("+="):
            return MergeRule.append
        if key.startswith("-="):
            return MergeRule.remove
        return MergeRule.override

    new_content = deepmerge_dicts(
        over_content=over_dict,
        base_content=base_dict,
        key_resolve_callback=_resolve_key_tokens,
        merge_rule_callback=merge_rule,
    )
    return new_content


class LaunchersSerialized(dict[str, dict]):
    """
    A list of launchers instance serialized as a dict structure.

    The dict is expected to have the following root structure::

        {manager_name1: {...}, manager_name2: {...}, ...}

    The dict structure include tokens that need to be resolved. Those tokens are used
    to determine how to merge 2 instances together.
    """

    def __add__(
        self,
        other: "LaunchersSerialized",
    ) -> "LaunchersSerialized":
        """
        Returns:
            new instance with deepcopied structure.
        """
        if not isinstance(other, LaunchersSerialized):
            raise TypeError(
                f"Cannot concatenate object of type {type(other)} with {type(self)}"
            )

        new_content = _merge_tokenized_dict(over_dict=other, base_dict=self)
        return LaunchersSerialized(new_content)

    def get_with_base_merged(self) -> "LaunchersSerialized":
        """
        Get a copy of this instance with the ``.base`` launcher merged with the other launchers.

        Returns:
            new instance with deepcopied structure.
        """
        self_copy = copy.deepcopy(self)
        # extract the potential base that all launchers should inherit
        if not BaseLauncher.name() in self_copy:
            return self_copy

        base_manager_config = self_copy.pop(BaseLauncher.name())
        base_managers = LaunchersSerialized(
            {
                manager_name: copy.deepcopy(base_manager_config)
                for manager_name in self_copy
            }
        )
        return base_managers + self_copy

    def get_resolved(self) -> dict[str, dict]:
        """
        Get the dict structure with all tokens resolved.

        Without tokens, the returned object is not a LaunchersSerialized instance anymore.

        Returns:
            deepcopied dict structure.
        """

        def process_pair(key: str, value: str):
            new_key = _resolve_key_tokens(key)
            return new_key, value

        new_content = refacto_dict(
            src_dict=copy.deepcopy(self),
            callback=process_pair,
            recursive=True,
        )
        return new_content

    def unserialize(self) -> list[BaseLauncher]:
        """
        Unserialize the given dict structure to BaseLauncher instances.

        The list can't contain duplicated launchers subclasses.
        """
        launchers: list[BaseLauncher] = []

        serialized = self.get_with_base_merged()
        serialized = serialized.get_resolved()

        for launcher_name, launcher_config in serialized.items():
            launcher_class = get_launcher_class(launcher_name)
            if not launcher_class:
                raise ValueError(
                    f"No launcher class registred with name <{launcher_name}>"
                )
            launcher = launcher_class.from_dict(launcher_config)
            launchers.append(launcher)

        return launchers


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
    launchers: LaunchersSerialized

    @classmethod
    def from_dict(cls, serialized: dict) -> "EnvironmentProfile":
        """
        Generate a profile instance from a serialized dict object.

        No type checking is performed and the user is reponsible for the correct
        type being stored in the dict.
        """
        identifier: str = serialized["identifier"]
        version: str = serialized["version"]
        base: Optional["EnvironmentProfile"] = serialized.get("base", None)
        launchers: LaunchersSerialized = serialized["launchers"]

        return EnvironmentProfile(
            identifier=identifier,
            version=version,
            base=base,
            launchers=launchers,
        )

    def to_dict(self) -> dict[str, Any]:
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
