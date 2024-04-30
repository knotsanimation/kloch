import copy
import dataclasses
import enum
import logging
from typing import Any
from typing import Callable
from typing import Optional

LOGGER = logging.getLogger(__name__)


class MergeRule(enum.IntEnum):
    """
    Define how 2 python objects should be merged together.
    """

    override = enum.auto()
    append = enum.auto()


def deepmerge_dicts(
    over_content: dict[str, Any],
    base_content: dict,
    merge_rule_callback: Optional[Callable[[str], MergeRule]] = None,
    key_resolve_callback: Optional[Callable[[str], str]] = None,
) -> dict[str, Any]:
    """
    Merge the 2 given dict assuming they have the same hierarchy.

    The merging rules are defined by the given callbacks. If no callback is provided
    the default rule is to override.
    """
    new_content = copy.deepcopy(base_content)

    for over_key, over_value in over_content.items():
        merge_rule = (
            merge_rule_callback(over_key) if merge_rule_callback else MergeRule.override
        )
        over_key = key_resolve_callback(over_key) if key_resolve_callback else over_key
        base_value = base_content.get(over_key, None)

        if isinstance(over_value, dict):
            base_value = base_value or {} if merge_rule == merge_rule.append else {}
            new_value = deepmerge_dicts(
                over_value,
                base_content=base_value,
                merge_rule_callback=merge_rule_callback,
                key_resolve_callback=key_resolve_callback,
            )

        elif (
            merge_rule == merge_rule.append
            and isinstance(over_value, list)
            and base_value
        ):
            new_value = [] + base_value + over_value

        else:
            new_value = copy.deepcopy(over_value)

        new_content[over_key] = new_value

    return new_content
