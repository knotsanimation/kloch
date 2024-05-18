import copy
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
    remove = enum.auto()


def refacto_dict(
    src_dict: dict,
    callback: Callable[[Any, Any], tuple[Any, Any]],
    recursive=True,
) -> dict:
    """
    Iterate through all key/value pairs of the given dict and execute the given callback
    at each step which return a new key/value pair for the output dict.

    Args:
        src_dict: dict obejct ot iterate
        callback: Callable expecting 2args: key, value and should return a tuple of new_key, new_value
        recursive: True to recursively process child dict

    Returns:
        a new dict instance
    """
    new_dict = {}
    for key, value in src_dict.items():
        if isinstance(value, dict) and recursive:
            value = refacto_dict(value, callback=callback, recursive=True)
        new_key, new_value = callback(key, value)
        new_dict[new_key] = new_value
    return new_dict


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
    merge_rule_callback = merge_rule_callback or (lambda k: MergeRule.override)
    key_resolve_callback = key_resolve_callback or (lambda k: k)

    for over_key, over_value in over_content.items():
        merge_rule = merge_rule_callback(over_key)

        # put base and over at same level by resolving both
        base_keys_resolved = {
            key_resolve_callback(bk): bk for bk, _ in base_content.items()
        }
        over_key_resolved = key_resolve_callback(over_key)

        base_key: Optional[str] = base_keys_resolved.get(over_key_resolved, None)
        base_value: Optional[Any] = base_content[base_key] if base_key else None

        if merge_rule == merge_rule.remove:
            if base_key:
                del new_content[base_key]
            continue

        if merge_rule == merge_rule.override:
            if base_key:
                del new_content[base_key]
            new_content[over_key] = over_value
            continue

        # reaching here implies `merge_rule.append`

        if isinstance(over_value, dict) and base_value:
            new_value = deepmerge_dicts(
                over_value,
                base_content=base_value,
                merge_rule_callback=merge_rule_callback,
                key_resolve_callback=key_resolve_callback,
            )

        elif isinstance(over_value, list) and base_value:
            new_value = [] + base_value + over_value

        else:
            new_value = copy.deepcopy(over_value)

        if base_key:
            # we have merged `base` value with `over` so we can remove it safely
            del new_content[base_key]
        new_content[over_key] = new_value
        continue

    return new_content
