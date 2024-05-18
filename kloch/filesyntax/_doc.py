"""
To reduce human mistakes and automatize documentation building,
we enforce the writting of launcher documentation in this module.
"""

import dataclasses
import logging
from typing import Optional
from typing import Type

import kloch.launchers

LOGGER = logging.getLogger(__name__)


class LauncherDoc:
    launcher: Type[kloch.launchers.BaseLauncher]
    description: str
    summary: str
    fields: dict[str, str]

    @classmethod
    def iterate(cls):
        return LauncherDoc.__subclasses__()

    @classmethod
    def get_launcher_doc(
        cls,
        launcher: Type[kloch.launchers.BaseLauncher],
    ) -> Optional[Type["LauncherDoc"]]:
        for doc in LauncherDoc.iterate():
            if doc.launcher is launcher:
                return doc
        return None


"""
In the following subclasses, one must describe how the environment profile
author must write launchers. Anything specifed is specific to the syntax
of the environment profile reader and NOT of the syntax of the launcher API.


However the launcher APi is used to validate that all launchers fields are documented.
"""


class BaseLauncherDoc(LauncherDoc):
    launcher = kloch.launchers.BaseLauncher
    description = "This launcher is never launched and is simply merged with other launchers defined in the profile."
    summary = (
        "An abstract launcher that whose purpose is to be merged with other launchers."
    )
    fields = {
        "environ": (
            """
mapping of environment variable to set before starting the environment.

The value can either be a regular string or a list of string.
The list of string has each item joined using the system path separator [2]_.

- All values have environment variables expanded with ``os.expandvars`` [1]_.   
  You can escape the expansion by doubling the ``$`` like ``$$``
- All values are turned absolute and normalized [4]_ if they are existing paths.
"""
        ),
        "command": (
            """
Arbitrary list of command line arguments to call at the end of the launcher execution.
"""
        ),
        "cwd": (
            """
Filesystem path to an existing directory to use as "current working directory".

- The path will have environment variables expanded with ``os.expandvars`` [1]_. 
  You can escape the expansion by doubling the ``$`` like ``$$``.
  You can also use variables defined in the ``environ`` key.
- The path is turned absolute and normalized [4]_.
"""
        ),
    }


class SystemLauncherDoc(LauncherDoc):
    launcher = kloch.launchers.SystemLauncher
    summary = (
        "A simple launcher executing the given command in the default system console."
    )
    description = "Useless without a command specified. The launcher will just set the given environment variables for the session, execute the command, then exit."
    fields = BaseLauncherDoc.fields.copy()


class PythonLauncherDoc(LauncherDoc):
    launcher = kloch.launchers.PythonLauncher
    summary = (
        "A launcher that execute the given python file with kloch's own interpreter."
    )
    description = (
        "Execute the given python file with kloch internal python interpreter.\n\n"
        "All ``command`` keys are passed as args to the python script."
    )
    fields = BaseLauncherDoc.fields.copy()
    fields.update(
        {
            "python_file": (
                """
Filesystem path to an existing python file.
The path will have environment variables expanded with ``os.expandvars`` [1]_.
The path is turned absolute and normalized. [4]_
"""
            ),
            # we override base documentation
            "command": "Arbitrary list of command line arguments passed to the python file.",
        }
    )


class RezEnvLauncherDoc(LauncherDoc):
    launcher = kloch.launchers.RezEnvLauncher
    description = """
We generate a rez interactive shell from a list of package requirements.
The request if first resolved as a `.rxt` file using ``rez-env --output``
and then launched with ``rez-env --input``.

The launcher will use a subprocess to start rez-env [3]_.
"""
    summary = "Start an interactive rez shell using the ``rez-env`` command."
    fields = BaseLauncherDoc.fields.copy()
    fields.update(
        {
            "config": "content of a valid yaml rez config that is created on the fly before the rez-env.",
            "params": """
list of command line arguments passed to rez-env.

Check the `rez documentation <https://rez.readthedocs.io/en/stable/commands/rez-env.html>`_.
""",
            "requires": "mapping of rez `package name`: `package version`",
        }
    )


def validate_documentation():
    # ensure developer didn't missed to add documentation before adding a new subclass
    result = len(LauncherDoc.iterate())
    expected = len(kloch.launchers.get_available_launchers_classes())
    assert result == expected, f"{result} != {expected}"
    # ensure developer didn't missed to add documentation for each dataclass field
    for launcher_doc in LauncherDoc.iterate():
        assert len(launcher_doc.fields) >= len(
            dataclasses.fields(launcher_doc.launcher)
        )
