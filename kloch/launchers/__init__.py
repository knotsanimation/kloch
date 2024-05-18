from ._base import BaseLauncher
from ._base import get_available_launchers_classes
from ._base import get_launcher_class

# need to be imported to be discoverable
from ._rezenv import RezEnvLauncher
from ._system import SystemLauncher
from ._python import PythonLauncher

# ensure the subclasses have properly overridden class attributes
# (this is because there is no way of having abstract attribute with abc module)
for launcher in get_available_launchers_classes():
    if launcher is not BaseLauncher:
        assert launcher.name != BaseLauncher.name
