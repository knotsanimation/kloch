import copy
from typing import Dict
from typing import List
from typing import Type

from kloch import MergeableDict
from ._context import LauncherContext
from ._context import unserialize_context_expression
from ._context import resolve_context_expression
from kloch.launchers import BaseLauncherSerialized


class LauncherSerializedList(List[BaseLauncherSerialized]):
    def to_dict(self) -> Dict[str, Dict]:
        """
        Convert the list to a builtin dict structure (noc ustom class used).

        Useful for serialization or to convert to a :any:`LauncherSerializedDict` instance.
        """
        return {launcher.identifier: dict(launcher) for launcher in self}

    def with_base_merged(self) -> "LauncherSerializedList":
        """
        Get a copy of this instance with the ``.base`` launcher merged with the other launchers.

        (This implies the returned instance does NOT have a ``.base`` key anymore)

        Returns:
            new instance with deepcopied structure.
        """
        self_copy: LauncherSerializedList = copy.deepcopy(self)

        # extract the potential base that all launchers should inherit
        for launcher in self_copy:
            if launcher.__class__ is BaseLauncherSerialized:
                base_launcher = launcher
                self_copy.remove(base_launcher)
                break
        else:
            return self_copy

        return LauncherSerializedList(
            [copy.deepcopy(base_launcher) + launcher for launcher in self_copy]
        )


# revert to `MergeableDict[str, Dict]` when python-3.7 support dropped
class LauncherSerializedDict(MergeableDict):
    """
    A list of launchers instance serialized as a dict structure.

    The dict is expected to have the following root structure::

        {"manager_name1": {...}, "manager_name2": {...}, ...}

    The dict structure include tokens that need to be resolved and indicate
    how to merge 2 :obj:`LauncherSerializedDict` instances together.
    See :any:`MergeableDict` for the full documentation on tokens.
    """

    def get_filtered_context(
        self, context: LauncherContext
    ) -> "LauncherSerializedDict":
        """
        Remove all launchers that doesn't match the given context.

        Returns:
             a new deepcopied instance with possibly lesser keys.
        """
        newdict = copy.deepcopy(self)
        for launcher_identifier in self.keys():
            launcher_context = unserialize_context_expression(launcher_identifier)
            if launcher_context != context:
                del newdict[launcher_identifier]

        return newdict

    def with_context_resolved(self) -> "LauncherSerializedDict":
        """
        Merge all the same launchers with different contexts to a single launcher.
        """
        toconcatenate: List[LauncherSerializedDict] = []
        for launcher_identifier in self.keys():
            resolved = resolve_context_expression(launcher_identifier)
            newdict = LauncherSerializedDict(
                {resolved: copy.deepcopy(self[launcher_identifier])}
            )
            toconcatenate.append(newdict)

        if len(toconcatenate) == 0:
            return copy.deepcopy(self)
        elif len(toconcatenate) == 1:
            return toconcatenate[0]

        return sum(toconcatenate[1:], toconcatenate[0])

    def to_serialized_list(
        self,
        launcher_classes: List[Type[BaseLauncherSerialized]],
    ) -> LauncherSerializedList:
        """
        Convert the dict structure to a list of :any:`BaseLauncherSerialized` instances.

        Args:
            launcher_classes:
                list of launchers classes that can be possibly stored in this serialized dict.

        Raises:
            ValueError: If a launcher is serialized in this instance but is unknown.

        Returns:
            deepcopied dict structure as list of instances.
        """
        _launcher_classes = {
            launcher.identifier: launcher for launcher in launcher_classes
        }
        launchers = []
        for identifier, launcher_config in self.items():
            _identifier = self.resolve_key_tokens(identifier)
            # it's not supposed to have context expression at this stage but we safe-proof it
            _identifier = resolve_context_expression(_identifier)
            launcher_class = _launcher_classes.get(_identifier)
            if not launcher_class:
                raise ValueError(
                    f"No serialized-launcher with identifier '{_identifier}' found."
                    f"Available launchers are '{', '.join(_launcher_classes.keys())}'"
                )
            launcher = launcher_class(copy.deepcopy(launcher_config))
            launchers.append(launcher)

        return LauncherSerializedList(launchers)
