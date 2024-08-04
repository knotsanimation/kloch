import copy
import enum
import logging
from typing import Any
from typing import Callable
from typing import Dict
from typing import Optional
from typing import Tuple
from typing import TypeVar

LOGGER = logging.getLogger(__name__)


class MergeRule(enum.IntEnum):
    """
    Define how 2 python objects should be merged together.
    """

    override = enum.auto()
    append = enum.auto()
    remove = enum.auto()
    ifnotexists = enum.auto()


def refacto_dict(
    src_dict: Dict,
    callback: Callable[[Any, Any], Tuple[Any, Any]],
    recursive=True,
) -> Dict:
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
    over_content: Dict[str, Any],
    base_content: Dict,
    merge_rule_callback: Optional[Callable[[str], MergeRule]] = None,
    key_resolve_callback: Optional[Callable[[str], str]] = None,
) -> Dict[str, Any]:
    """
    Recursively merge the 2 given dict "over one another".

    Intended to work best with dict having the same key/value structure.

    The merging rules are defined by the given callbacks. If no callback is provided
    the default rule is to override.

    The following object types supports the ``append`` rule:

    - `list`: with a ``.extend()`` behavior
    - `dict`: deepmerged recursively

    For any other type, the `over`'s value override the `base`'s value.
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

        if merge_rule == merge_rule.ifnotexists:
            if base_key:
                new_content[base_key] = base_value
            else:
                new_content[over_key] = over_value
            continue

        # reaching here implies `merge_rule.append`

        if isinstance(over_value, dict) and isinstance(base_value, dict):
            new_value = deepmerge_dicts(
                over_value,
                base_content=base_value,
                merge_rule_callback=merge_rule_callback,
                key_resolve_callback=key_resolve_callback,
            )

        elif isinstance(over_value, list) and isinstance(base_value, list):
            new_value = [] + base_value + over_value

        else:
            new_value = copy.deepcopy(over_value)

        if base_key:
            # we have merged `base` value with `over` so we can remove it safely
            del new_content[base_key]
        new_content[over_key] = new_value
        continue

    return new_content


def _remove_prefix(text: str, prefix: str) -> str:
    if text.startswith(prefix):
        return text[len(prefix) :]
    return text


T = TypeVar("T", bound="MergeableDict")


class MergeableDict(dict):
    """
    A dict that can be deep-merged with another dict.

    The merging algorithm is defined in :obj:`deepmerge_dicts`.

    You can define the merging granularity on a per-key basis by adding token prefix
    to your keys.

    Available tokens are found in :obj:`MergeableDict.tokens`.

    Example:

        .. exec_code::
            :caption_output: results:
            :language_output: python

            from kloch import MergeableDict
            dict_1 = MergeableDict({"+=config": {"cache": True, "level": 3, "port": "A46"}})
            dict_2 = MergeableDict({"+=config": {"cache": False, "-=level": 3}})
            print(dict_1 + dict_2)

    """

    class tokens:
        append = "+="
        remove = "-="
        override = "=="
        ifnotexists = "!="

    def __add__(self: T, other: T) -> T:
        """
        Merge the 2 dict structure together with ``other`` merged over ``self``.

        The returned class type is of the left member of the + operation.

        Returns:
            new instance with deepcopied structure.
        """
        if not isinstance(other, MergeableDict):
            raise TypeError(
                f"Cannot concatenate object of type {type(other)} with {type(self)}"
            )

        new_content = deepmerge_dicts(
            over_content=other,
            base_content=self,
            key_resolve_callback=self.resolve_key_tokens,
            merge_rule_callback=self.get_merge_rule,
        )
        return self.__class__(new_content)

    @classmethod
    def resolve_key_tokens(cls, key: str) -> str:
        """
        Ensure the given key has all potential tokens removed.
        """
        resolved = key
        for token in [
            cls.tokens.append,
            cls.tokens.remove,
            cls.tokens.override,
            cls.tokens.ifnotexists,
        ]:
            resolved = _remove_prefix(resolved, token)
        return resolved

    @classmethod
    def get_merge_rule(cls, key: str) -> MergeRule:
        """
        Extract the :obj:`MergeRule` for the given key based on its potential token.
        """
        if key.startswith(cls.tokens.append):
            return MergeRule.append
        if key.startswith(cls.tokens.remove):
            return MergeRule.remove
        if key.startswith(cls.tokens.override):
            return MergeRule.override
        if key.startswith(cls.tokens.ifnotexists):
            return MergeRule.ifnotexists
        return MergeRule.append

    def get(self, key, default=None, ignore_tokens: bool = False):
        """
        Args:
            key: key's value to retrieve
            default: value to return if key is not in the dict
            ignore_tokens:
                if True, both key and self are used with a resolved variant (without tokens).
                For example ``.get("config",ignore_tokens=True)`` would still return
                ``{...}`` if ``self=={"+=config":{...}}``.
        """

        new_key = key
        if ignore_tokens:
            new_key = self.resolve_key_tokens(key)
            resolved_mapping = {
                self.resolve_key_tokens(child_key): child_key for child_key in self
            }
            if new_key in resolved_mapping:
                new_key = resolved_mapping[new_key]
            else:
                new_key = key

        return super().get(new_key, default)

    def resolved(self) -> Dict:
        """
        Get the dict structure with all tokens resolved.

        Without tokens, the returned object become a regular dict instance.

        Returns:
            deepcopied dict structure.
        """

        def process_pair(key: str, value: str):
            new_key = self.resolve_key_tokens(key)
            return new_key, value

        new_content = refacto_dict(
            src_dict=copy.deepcopy(self),
            callback=process_pair,
            recursive=True,
        )
        return dict(new_content)
