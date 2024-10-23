from typing import List
from typing import Optional
from typing import Type
from typing import TypeVar
from typing import Union

import kloch.launchers
from kloch.launchers import BaseLauncher
from kloch.launchers import BaseLauncherSerialized
from ._plugins import LoadedPluginsLaunchers


T = TypeVar("T")


def _collect_launchers(
    natives: List[Type[T]],
    plugins: Optional[LoadedPluginsLaunchers[Type[T]]] = None,
) -> List[Type[T]]:
    """
    Combine given launchers to flat list of unique objects.
    """
    plugins = plugins.launchers if plugins else []
    launchers = natives + plugins
    # remove duplicates but preserve order
    return [
        launcher
        for index, launcher in enumerate(launchers)
        if launcher not in launchers[:index]
    ]


def get_available_launchers_classes(
    plugins: Optional[LoadedPluginsLaunchers[Type[BaseLauncher]]] = None,
) -> List[Type[BaseLauncher]]:
    """
    Collect all the launchers classes available.

    This is simply the given plugin launchers + builtin launchers.

    Args:
        plugins: collection of launcher loaded from plugins.
    """
    # noinspection PyProtectedMember
    return _collect_launchers(
        natives=kloch.launchers._BUILTINS_LAUNCHERS.copy(),
        plugins=plugins,
    )


def get_available_launchers_serialized_classes(
    plugins: Optional[LoadedPluginsLaunchers[Type[BaseLauncherSerialized]]] = None,
) -> List[Type[BaseLauncherSerialized]]:
    """
    Collect all the serialized launchers classes available.

    This is simply the given plugin launchers + builtin launchers.

    Args:
        plugins: collection of launcher loaded from plugins
    """
    # noinspection PyProtectedMember
    return _collect_launchers(
        natives=kloch.launchers._BUILTINS_LAUNCHERS_SERIALIZED.copy(),
        plugins=plugins,
    )


# noinspection PyProtectedMember
def is_launcher_plugin(
    launcher: Union[Type[BaseLauncher], Type[BaseLauncherSerialized]]
) -> bool:
    """
    Return True if the given launcher is an external plugin else False if builtin.
    """
    if launcher in kloch.launchers._BUILTINS_LAUNCHERS:
        return False
    return launcher not in kloch.launchers._BUILTINS_LAUNCHERS_SERIALIZED
