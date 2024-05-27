import dataclasses
import importlib
import inspect
import logging
from typing import List
from typing import Tuple
from typing import Type
from typing import TypeVar

from kloch.launchers import BaseLauncher
from kloch.launchers import BaseLauncherSerialized

LOGGER = logging.getLogger(__name__)

T = TypeVar("T")


def load_plugin_launchers(
    module_names: List[str],
    subclass_type: Type[T],
) -> Tuple[List[Type[T]], List[str]]:
    """
    Retrieve the launcher subclasses from the given module names.

    Will raise if the module names are not existing modules.

    The output of this function is NOT cached.

    Args:
        module_names: list of importable python module names
        subclass_type: base class of the launchers to return

    Returns:
        a tuple of ["list of launchers subclass", "list of empty module name"]
    """
    launchers = []
    missed = []

    for module_name in module_names:
        LOGGER.debug(f"loading launcher plugin '{module_name}' ...")
        module = importlib.import_module(module_name)
        module_content = inspect.getmembers(module, inspect.isclass)
        module_launchers = [
            obj[1]
            for obj in module_content
            if issubclass(obj[1], subclass_type) and not obj[1] is subclass_type
        ]
        LOGGER.debug(f"found '{len(module_launchers)}' launchers: {module_launchers}")
        if not module_launchers:
            missed.append(module_name)
            continue

        launchers += module_launchers

    return launchers, missed


def _assert(condition: bool, message: str):
    if not condition:
        raise AssertionError(message)


def check_launcher_implementation(launcher: Type[BaseLauncher]):
    """
    Raise an AssertionError if the given launcher subclass is not properly implemented.

    Args:
        launcher: a BaseLauncher class/subclass to check
    """
    if launcher is not BaseLauncher:
        _assert(
            launcher.name != BaseLauncher.name,
            f"Implementation '{launcher.__name__}' forgot to override 'name' attribute.",
        )

    _assert(
        issubclass(launcher, BaseLauncher),
        f"Implementation '{launcher.__name__}' must be a direct subclass of '{BaseLauncher.__name__}'.",
    )


def check_launcher_serialized_implementation(launcher: Type[BaseLauncherSerialized]):
    """
    Raise an AssertionError if the given serialized launcher subclass is not properly implemented.

    Args:
        launcher: a BaseLauncherSerialized class/subclass to check
    """
    _assert(
        issubclass(launcher, BaseLauncherSerialized),
        f"Implementation '{launcher.__name__}' must be a direct subclass of '{BaseLauncherSerialized.__name__}'.",
    )

    def missing(field: str) -> str:
        return (
            f"Implementation '{launcher.__name__}' is missing the '{field}' attribute."
        )

    _assert(hasattr(launcher, "fields"), missing("fields"))
    _assert(hasattr(launcher, "source"), missing("source"))
    _assert(hasattr(launcher, "identifier"), missing("identifier"))
    _assert(hasattr(launcher, "summary"), missing("summary"))
    _assert(hasattr(launcher, "description"), missing("description"))

    def wrong_override(field: str) -> str:
        return f"Implementation '{launcher.__name__}' doesn't override the base '{field}' attribute."

    if launcher is not BaseLauncherSerialized:
        _assert(
            launcher.source is not BaseLauncherSerialized,
            wrong_override("source"),
        )
        _assert(
            launcher.fields is not BaseLauncherSerialized.fields,
            wrong_override("fields"),
        )
        _assert(
            launcher.summary is not BaseLauncherSerialized.summary,
            wrong_override("summary"),
        )
        _assert(
            launcher.description is not BaseLauncherSerialized.description,
            wrong_override("description"),
        )
        _assert(
            launcher.identifier is not BaseLauncherSerialized.identifier,
            wrong_override("identifier"),
        )

    fields_ser = dataclasses.fields(launcher.fields)
    fields_source = dataclasses.fields(launcher.source)

    _assert(
        len(fields_ser) >= len(fields_source),
        f"Implementation '{launcher.__name__}' must define as much or more fields than its source '{launcher.source}'",
    )

    for field_ser in fields_ser:
        _assert(
            "required" in field_ser.metadata,
            f"Implementation '{launcher.__name__}' field '{field_ser.name}' is missing a 'required' attribute in its metadata.",
        )
        _assert(
            "description" in field_ser.metadata,
            f"Implementation '{launcher.__name__}' field '{field_ser.name}' is missing a 'description' attribute in its metadata.",
        )


def check_launcher_plugins(launcher_plugins: List[str]):
    """
    Raise an exception if any of the launchers extracted from plugin system are invalid.

    Args:
        launcher_plugins: list of modules name to extract launcher from.
    """
    launchers, missed = load_plugin_launchers(
        launcher_plugins,
        BaseLauncher,
    )
    if missed:
        raise ImportError(
            f"The following modules did not define a '{BaseLauncher.__name__}' subclass object: {missed}"
        )

    for launcher in launchers:
        check_launcher_implementation(launcher)

    # serialized classes:

    launchers, missed = load_plugin_launchers(
        launcher_plugins,
        BaseLauncherSerialized,
    )
    if missed:
        raise ImportError(
            f"The following modules did not define a '{BaseLauncherSerialized.__name__}' subclass object: {missed}"
        )

    for launcher in launchers:
        check_launcher_serialized_implementation(launcher)
