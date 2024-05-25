import copy
from typing import Dict
from typing import List

from kloch import MergeableDict
from kloch.launchers import get_launcher_serialized_class
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

    def to_serialized_list(self) -> LauncherSerializedList:
        """
        Convert the dict structure to a list of :any:`BaseLauncherSerialized` instances.

        Returns:
            deepcopied dict structure as list of instances.
        """
        launchers = []
        for identifier, launcher_config in self.items():
            _identifier = self.resolve_key_tokens(identifier)
            launcher_class = get_launcher_serialized_class(_identifier)
            if not launcher_class:
                raise ValueError(
                    f"No Serialized Launcher with identifier '{_identifier}' found."
                )
            launcher = launcher_class(copy.deepcopy(launcher_config))
            launchers.append(launcher)

        return LauncherSerializedList(launchers)
