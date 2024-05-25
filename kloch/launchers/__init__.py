"""
Entities that serialize a function call made to execute a software.
"""

from .base import BaseLauncher
from .base import BaseLauncherSerialized
from .base import BaseLauncherFields

from .rezenv import RezEnvLauncher
from .rezenv import RezEnvLauncherSerialized
from .system import SystemLauncher
from .system import SystemLauncherSerialized
from .python import PythonLauncher
from .python import PythonLauncherSerialized

from ._get import get_available_launchers_classes
from ._get import get_launcher_class
from ._get import get_available_launchers_serialized_classes
from ._get import get_launcher_serialized_class

from ._serialized import LauncherSerializedDict
from ._serialized import LauncherSerializedList

LAUNCHERS = [
    BaseLauncher,
    RezEnvLauncher,
    SystemLauncher,
    PythonLauncher,
]
"""
List of launchers class implementation, including the base one.
"""

LAUNCHERS_SERIALIZED = [
    BaseLauncherSerialized,
    RezEnvLauncherSerialized,
    SystemLauncherSerialized,
    PythonLauncherSerialized,
]
"""
List of serialized launchers class implementation, including the base one.
"""
