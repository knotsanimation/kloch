from typing import Optional
from typing import Type

import kloch.launchers
from kloch.launchers import BaseLauncher
from kloch.launchers import BaseLauncherSerialized


def get_available_launchers_classes() -> list[Type[BaseLauncher]]:
    """
    Get all list of available launcher classes that are registred.
    """
    return kloch.launchers.LAUNCHERS.copy()


def get_launcher_class(name: str) -> Optional[Type[BaseLauncher]]:
    """
    Get the launcher class which match the given unique name.
    """
    for sub_class in get_available_launchers_classes():
        if sub_class.name == name:
            return sub_class
    return None


def get_available_launchers_serialized_classes() -> list[Type[BaseLauncherSerialized]]:
    """
    Get all list of available serialized launcher classes that are registred.
    """
    return kloch.launchers.LAUNCHERS_SERIALIZED.copy()


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
