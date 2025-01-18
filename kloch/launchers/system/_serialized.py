import dataclasses
import logging

from kloch.launchers import BaseLauncherSerialized
from kloch.launchers import BaseLauncherFields
from ._dataclass import SystemLauncher

LOGGER = logging.getLogger(__name__)


@dataclasses.dataclass(frozen=True)
class SystemLauncherFields(BaseLauncherFields):

    command_as_str: bool = dataclasses.field(
        default="command_as_str",
        metadata={
            "description": (
                "If True a str is passed to ``subprocess.run``, else a list is passed. "
                "This can be useful in the context of setting ``shell=True`` or not on UNIX platforms."
            ),
            "required": False,
        },
    )

    subprocess_kwargs: dict = dataclasses.field(
        default="subprocess_kwargs",
        metadata={
            "description": (
                "Mapping of kwargs to pass to the internal ``subprocess.run`` call."
            ),
            "required": False,
        },
    )

    expand_first_arg: bool = dataclasses.field(
        default="expand_first_arg",
        metadata={
            "description": (
                "If True the first argument of the passed command will be expanded "
                "using ``shutil.which`` to find its executable file on disk. Will "
                "raise if no path is found.\n\n"
                "Useful for avoiding using ``shell=True`` in ``subprocess_kwargs``."
            ),
            "required": False,
        },
    )


class SystemLauncherSerialized(BaseLauncherSerialized):
    source = SystemLauncher

    identifier = SystemLauncher.name

    fields = SystemLauncherFields

    summary = (
        "A simple launcher executing the given command in the default system console."
    )
    description = summary + (
        "\n\n"
        "The launcher will just set the given environment variables for the session,"
        "execute the command, then exit. Which make it useless without a command specified."
        "\n\n"
        "The launcher use ``subprocess.run`` to execute the command."
    )

    def validate(self):
        subprocesskw = self.fields.subprocess_kwargs
        if subprocesskw in self:
            assert isinstance(
                self[subprocesskw], dict
            ), f"'{subprocesskw}': must be a dict."
        super().validate()

    # we override for type-hint
    def unserialize(self) -> SystemLauncher:
        # noinspection PyTypeChecker
        return super().unserialize()
