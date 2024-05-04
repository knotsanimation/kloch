"""
We define a simple config system that describe how to build a software environment using
different package managers.

The config system can handle the merging of 2 configs structure.
"""

import copy
import dataclasses
from typing import Any
from typing import Optional

from ._merging import refacto_dict
from ._merging import deepmerge_dicts
from ._merging import MergeRule
from kenvmanager.launchers import get_launcher_class
from kenvmanager.launchers import BaseLauncher


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


class PackageManagersSerialized(dict[str, dict]):
    """
    A list of PackageManager serialized as a dict structure.

    The dict is expected to have the following root structure::

        {manager_name1: {...}, manager_name2: {...}, ...}

    The dict structure include tokens that need to be resolved. Those tokens are used
    to determine how to merge 2 instances together.
    """

    def __add__(
        self,
        other: "PackageManagersSerialized",
    ) -> "PackageManagersSerialized":
        """
        Returns:
            new instance with deepcopied structure.
        """
        if not isinstance(other, PackageManagersSerialized):
            raise TypeError(
                f"Cannot concatenate object of type {type(other)} with {type(self)}"
            )

        new_content = _merge_tokenized_dict(over_dict=other, base_dict=self)
        return PackageManagersSerialized(new_content)

    def get_with_base_merged(self) -> "PackageManagersSerialized":
        """
        Get a copy of this instance with the .base manager merged with the other managers.

        Returns:
            new instance with deepcopied structure.
        """
        self_copy = copy.deepcopy(self)
        # extract the potential base that all managers should inherit
        if not BaseLauncher.name() in self_copy:
            return self_copy

        base_manager_config = self_copy.pop(BaseLauncher.name())
        base_managers = PackageManagersSerialized(
            {
                manager_name: copy.deepcopy(base_manager_config)
                for manager_name in self_copy
            }
        )
        return base_managers + self_copy

    def get_resolved(self) -> dict[str, dict]:
        """
        Get the dict structure with all tokens resolved.

        Without tokens, the returned object is not a PackageManagersProfile instance anymore.

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
        Unserialize the given dict structure to PackageManager instances.

        The list can't contain duplicated package managers subclasses.
        """
        managers: list[BaseLauncher] = []

        serialized = self.get_with_base_merged()
        serialized = serialized.get_resolved()

        for manager_name, manager_config in serialized.items():
            manager_class = get_launcher_class(manager_name)
            if not manager_class:
                raise ValueError(
                    f"No manager class registred with the name <{manager_name}>"
                )
            manager = manager_class.from_dict(manager_config)
            managers.append(manager)

        return managers


@dataclasses.dataclass
class EnvironmentProfile:
    """
    An environment is a collection of parameters to launch a package manager.

    Environment can inherit each other by specifying a `base` attribute. The inheritance
    only merge the package managers parameters of the 2.
    """

    identifier: str
    version: str
    base: Optional["EnvironmentProfile"]
    managers: PackageManagersSerialized

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
        managers: PackageManagersSerialized = serialized["managers"]

        return EnvironmentProfile(
            identifier=identifier,
            version=version,
            base=base,
            managers=managers,
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

        serialized["managers"] = copy.deepcopy(self.managers)
        return serialized

    def get_merged_profile(self):
        """
        Resolve the inheritance the profile might have over another profile.

        Returns:
            a new instance.
        """
        managers = self.managers
        if self.base:
            managers = self.base.get_merged_profile().managers + managers

        return EnvironmentProfile(
            identifier=self.identifier,
            version=self.version,
            base=None,
            managers=managers,
        )
