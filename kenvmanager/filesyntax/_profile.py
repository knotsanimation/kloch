"""
We define a simple config system that can handle the merging of 2 configs.

The config allow to describe how to build a software environment using a
package manager.
"""
import copy
import dataclasses
from typing import Any
from typing import Optional

from ._merging import deepmerge_dicts
from ._merging import MergeRule
from kenvmanager.managers import get_package_manager_profile_class
from kenvmanager.managers import PackageManagerProfileBase


@dataclasses.dataclass
class EnvironmentProfileFileSyntax:
    identifier: str
    version: str
    base: Optional["EnvironmentProfileFileSyntax"]
    content: dict[str, dict]

    @classmethod
    def from_dict(cls, serialized: dict) -> "EnvironmentProfileFileSyntax":
        """
        Generate a profile instance from a serialized dict object.
        """
        identifier = serialized["identifier"]
        version = serialized["version"]
        base = serialized.get("base", None)
        content = serialized["content"]

        return EnvironmentProfileFileSyntax(
            identifier=identifier,
            version=version,
            base=base,
            content=content,
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

        serialized["content"] = copy.deepcopy(self.content)
        return serialized

    def get_resolved_content(self) -> dict[str, dict]:
        """
        Get the profile dict content with token resolved and merged with the specified base profile.
        """

        def key_resolve(key: str):
            return key.removeprefix("+=")

        def merge_rule(key: str):
            return MergeRule.append if key.startswith("+=") else MergeRule.override

        base_profile = self.base
        base_content = base_profile.get_resolved_content() if base_profile else {}
        new_content = deepmerge_dicts(
            over_content=self.content,
            base_content=base_content,
            key_resolve_callback=key_resolve,
            merge_rule_callback=merge_rule,
        )
        return new_content

    def get_manager_profiles(self) -> list[PackageManagerProfileBase]:
        managers: list[PackageManagerProfileBase] = []
        content = self.get_resolved_content()
        for manager_name, manager_config in content.items():
            manager_class = get_package_manager_profile_class(manager_name)
            if not manager_class:
                raise ValueError(
                    f"No manager class registred with the name {manager_name}"
                )
            manager = manager_class.from_dict(manager_config)
            managers.append(manager)

        return managers
