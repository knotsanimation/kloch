import dataclasses
import logging
import os
from pathlib import Path
from typing import Dict
from typing import List

from kloch.launchers import BaseLauncherSerialized
from kloch.launchers import BaseLauncherFields
from ._dataclass import PythonLauncher

LOGGER = logging.getLogger(__name__)


# noinspection PyTypeChecker
@dataclasses.dataclass(frozen=True)
class PythonLauncherFields(BaseLauncherFields):
    python_file: str = dataclasses.field(
        default="python_file",
        metadata={
            "description": (
                "Filesystem path to an existing python file.\n"
                "The path will have environment variables expanded with ``os.expandvars`` [1]_.\n"
                "The path is turned absolute and normalized. [4]_\n"
            ),
            "required": True,
        },
    )
    # we override just for the metadata attribute
    # noinspection PyDataclass
    command: List[str] = dataclasses.field(
        default=BaseLauncherFields.command,
        metadata={
            "description": "Arbitrary list of command line arguments passed to the python file.",
            "required": False,
        },
    )


class PythonLauncherSerialized(BaseLauncherSerialized):
    source = PythonLauncher

    identifier = PythonLauncher.name

    fields = PythonLauncherFields

    summary = (
        "A launcher that execute the given python file with kloch's own interpreter."
    )
    description = (
        "Execute the given python file with kloch internal python interpreter.\n"
        "\n"
        "All ``command`` keys are passed as args to the python script."
    )

    def validate(self):
        super().validate()
        python_file = self.fields.python_file
        assert python_file in self, f"'{python_file}': missing or empty attribute."
        assert isinstance(self[python_file], str), f"'{python_file}': must be a str."

    def resolved(self) -> Dict:
        resolved = super().resolved()
        python_file = self.fields.python_file

        old_python_file = self[python_file]
        new_python_file = Path(os.path.expandvars(old_python_file)).absolute().resolve()
        resolved[python_file] = str(new_python_file)

        return resolved

    # we override for type-hint
    def unserialize(self) -> PythonLauncher:
        # noinspection PyTypeChecker
        return super().unserialize()
