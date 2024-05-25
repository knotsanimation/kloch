import dataclasses
import logging

from kloch.launchers import BaseLauncherSerialized
from kloch.launchers import BaseLauncherFields
from ._dataclass import SystemLauncher

LOGGER = logging.getLogger(__name__)


@dataclasses.dataclass(frozen=True)
class SystemLauncherFields(BaseLauncherFields):
    pass


class SystemLauncherSerialized(BaseLauncherSerialized):
    source = SystemLauncher

    identifier = SystemLauncher.name

    fields = SystemLauncherFields

    summary = (
        "A simple launcher executing the given command in the default system console."
    )
    description = (
        "Useless without a command specified. The launcher will just set "
        "the given environment variables for the session, execute the command, then exit."
    )

    def validate(self):
        super().validate()

    # we override for type-hint
    def unserialize(self) -> SystemLauncher:
        # noinspection PyTypeChecker
        return super().unserialize()
