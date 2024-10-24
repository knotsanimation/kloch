import dataclasses
import importlib
import inspect
import logging
from typing import Dict
from typing import Generic
from typing import List
from typing import Type
from typing import TypeVar

from kloch.launchers import BaseLauncher
from kloch.launchers import BaseLauncherSerialized

LOGGER = logging.getLogger(__name__)

T = TypeVar("T")


@dataclasses.dataclass
class LoadedPluginsLaunchers(Generic[T]):
    launchers: List[T]
    """
    List of external plugins that have been loaded
    """

    missed: Dict[str, str]
    """
    Given plugins that couldn't be loaded as mapping of {"module name": "error message"}
    """

    given: List[str]
    """
    Original list of modules name the plugins were extracted from.
    """


def load_plugin_launchers(
    module_names: List[str],
    subclass_type: Type[T],
) -> LoadedPluginsLaunchers[Type[T]]:
    """
    Retrieve the launcher subclasses from the given module names.

    Import error are silenced and stored in the returned object.

    Args:
        module_names: list of importable python module names
        subclass_type: base class of the launchers to return

    Returns:
        An instance of plugins loaded
    """
    plugins = []
    missed = {}

    for module_name in module_names:
        try:
            module = importlib.import_module(module_name)
        except (ModuleNotFoundError, ImportError) as error:
            missed[module_name] = str(error)
            continue

        module_content = inspect.getmembers(module, inspect.isclass)
        module_launchers = [
            obj[1]
            for obj in module_content
            if issubclass(obj[1], subclass_type) and not obj[1] is subclass_type
        ]
        if not module_launchers:
            missed[module_name] = (
                f"Module doesn't have any subclass of '{subclass_type}'"
            )
            continue

        for launcher in module_launchers:
            if launcher in plugins:
                LOGGER.warning(
                    f"Got duplicated plugin '{launcher}' from module '{module_name}': skipping"
                )
                continue
            plugins.append(launcher)

    return LoadedPluginsLaunchers(
        launchers=plugins,
        missed=missed,
        given=module_names.copy(),
    )


def _assert(condition: bool, message: str):
    if not condition:
        raise AssertionError(message)


def _check_launcher_implementation(launcher: Type[BaseLauncher]):
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


def _check_launcher_serialized_implementation(launcher: Type[BaseLauncherSerialized]):
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


class PluginModuleError(Exception):
    pass


class PluginImplementationError(Exception):
    pass


def check_launcher_plugins(
    plugins: LoadedPluginsLaunchers[Type[BaseLauncherSerialized]],
) -> List[Exception]:
    """
    Return any issue/error the given launcher may have.

    This function is not supposed to raise if a launcher is invalid.

    Args:
        plugins: collection of plugin launcher loaded from external modules.

    Returns:
        list of errors found in given loaded plugins, empty if no errors.
    """
    errors: List[Exception] = []
    if plugins.missed:
        for module, error in plugins.missed.items():
            error = PluginModuleError(f"Module '{module}' was not loaded: {error}")
            errors.append(error)

    for launcher in plugins.launchers:
        try:
            _check_launcher_serialized_implementation(launcher)
        except AssertionError as error:
            error = PluginImplementationError(str(error))
            errors.append(error)

    launchers = [launcher.source for launcher in plugins.launchers]

    try:
        for launcher in launchers:
            _check_launcher_implementation(launcher)
    except AssertionError as error:
        error = PluginImplementationError(str(error))
        errors.append(error)

    return errors
