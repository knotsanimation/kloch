import dataclasses
from pathlib import Path
from typing import List
from typing import Optional

from kloch.launchers import BaseLauncher
from kloch.launchers import BaseLauncherSerialized
from kloch.launchers import BaseLauncherFields

# intentional import
from kloch.launchers import PythonLauncher


@dataclasses.dataclass
class TyfaLauncher(BaseLauncher):

    name = "tyfa"

    def execute(
        self,
        tmpdir: Path,
        command: Optional[List[str]] = None,
    ):  # pragma: no cover
        pass


@dataclasses.dataclass(frozen=True)
class TyfaLauncherFields(BaseLauncherFields):
    pass


class TyfaLauncherSerialized(BaseLauncherSerialized):
    source = TyfaLauncher

    identifier = TyfaLauncher.name

    fields = TyfaLauncherFields

    summary = "Whatever"
    description = "Follow me on GitHub ! https://github.com/MrLixm"

    def validate(self):  # pragma: no cover
        super().validate()

    # we override for type-hint
    def unserialize(self) -> TyfaLauncher:  # pragma: no cover
        # noinspection PyTypeChecker
        return super().unserialize()
