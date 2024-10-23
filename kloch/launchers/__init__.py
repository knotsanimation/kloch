"""
Entities that serialize a function call made to execute a software.
"""

from .base import BaseLauncher
from .base import BaseLauncherSerialized
from .base import BaseLauncherFields


from .system import SystemLauncher
from .system import SystemLauncherSerialized
from .python import PythonLauncher
from .python import PythonLauncherSerialized

from ._plugins import check_launcher_plugins
from ._plugins import LoadedPluginsLaunchers
from ._plugins import load_plugin_launchers

from ._get import get_available_launchers_classes
from ._get import get_available_launchers_serialized_classes
from ._get import is_launcher_plugin

from ._serialized import LauncherSerializedDict
from ._serialized import LauncherSerializedList

_BUILTINS_LAUNCHERS = [
    BaseLauncher,
    SystemLauncher,
    PythonLauncher,
]
"""
List of launchers class implementation, including the base one.
"""

_BUILTINS_LAUNCHERS_SERIALIZED = [
    BaseLauncherSerialized,
    SystemLauncherSerialized,
    PythonLauncherSerialized,
]
"""
List of serialized launchers class implementation, including the base one.
"""
