from typing import List
from typing import Optional
from typing import Type
from typing import Union

import kloch.launchers
from kloch.launchers import BaseLauncher
from kloch.launchers import BaseLauncherSerialized
from ._plugins import load_plugin_launchers


def get_available_launchers_classes(
    launcher_plugins: List[str] = None,
) -> List[Type[BaseLauncher]]:
    """
    Get all list of available launcher classes that are registred.

    Args:
        launcher_plugins: list of python module names to load plugin launcher from.
    """
    launcher_plugins = (
        kloch.get_config().launcher_plugins
        if launcher_plugins is None
        else launcher_plugins
    )
    plugins, _ = load_plugin_launchers(launcher_plugins, BaseLauncher)
    # noinspection PyProtectedMember
    launchers = kloch.launchers._BUILTINS_LAUNCHERS.copy() + plugins
    # remove duplicates
    return [
        launcher
        for index, launcher in enumerate(launchers)
        if launcher not in launchers[:index]
    ]


def get_launcher_class(name: str) -> Optional[Type[BaseLauncher]]:
    """
    Get the launcher class which match the given unique name.
    """
    for sub_class in get_available_launchers_classes():
        if sub_class.name == name:
            return sub_class
    return None


def get_available_launchers_serialized_classes(
    launcher_plugins: List[str] = None,
) -> List[Type[BaseLauncherSerialized]]:
    """
    Get all list of available serialized launcher classes that are registred.

    Args:
        launcher_plugins: list of python module names to load plugin launcher from.
    """
    launcher_plugins = (
        kloch.get_config().launcher_plugins
        if launcher_plugins is None
        else launcher_plugins
    )
    plugins, _ = load_plugin_launchers(launcher_plugins, BaseLauncherSerialized)
    # noinspection PyProtectedMember
    launchers = kloch.launchers._BUILTINS_LAUNCHERS_SERIALIZED.copy() + plugins
    # remove duplicates
    return [
        launcher
        for index, launcher in enumerate(launchers)
        if launcher not in launchers[:index]
    ]


def get_launcher_serialized_class(
    identifier: str,
) -> Optional[Type[BaseLauncherSerialized]]:
    """
    Get the serialized launcher class which match the given identifier.
    """
    for sub_class in get_available_launchers_serialized_classes():
        if sub_class.identifier == identifier:
            return sub_class
    return None


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
