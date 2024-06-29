import dataclasses
from pathlib import Path
from typing import List
from typing import Optional

from kloch.launchers import BaseLauncher
from kloch.launchers import BaseLauncherSerialized
from kloch.launchers import BaseLauncherFields


@dataclasses.dataclass
class BehrLauncher(BaseLauncher):

    name = "behr"

    def execute(
        self,
        tmpdir: Path,
        command: Optional[List[str]] = None,
    ):  # pragma: no cover
        pass


@dataclasses.dataclass(frozen=True)
class BehrLauncherFields(BaseLauncherFields):
    pass


class BehrLauncherSerialized(BaseLauncherSerialized):
    source = BehrLauncher

    identifier = BehrLauncher.name

    fields = BehrLauncherFields

    summary = "Whatever"
    description = "Follow me on Mastodon ! https://mastodon.gamedev.place/@liamcollod"

    def validate(self):  # pragma: no cover
        super().validate()

    # we override for type-hint
    def unserialize(self) -> BehrLauncher:  # pragma: no cover
        # noinspection PyTypeChecker
        return super().unserialize()
