import dataclasses
from pathlib import Path
from typing import Optional

import pytest

import kloch
import kloch.launchers

PROFILE_DELTA_ENVIRON = {
    "KNOTS_SKYNET_PATH": "N:",
    "KNOTS_LOCAL_INSTALL_PATH": r"$LOCALAPPDATA\knots",
    "KNOTS_LOCAL_REZ_INSTALL_PATH": r"$KNOTS_LOCAL_INSTALL_PATH\rez",
    "KNOTS_LOCAL_REZ_SCRIPTS_PATH": r"$KNOTS_LOCAL_REZ_INSTALL_PATH\Scripts\rez",
    "REZ_VERSION": "2.114.1",
    "REZ_PYTHON_VERSION": "3.10.11",
    "UNINSTALL_LOG_PATH": r"$KNOTS_LOCAL_INSTALL_PATH\user-rez-uninstall.log",
}


def test_profile_delta(data_dir):
    profile_path = data_dir / "profile-delta.yml"
    profile = kloch.read_profile_from_file(profile_path, profile_locations=[data_dir])
    assert profile.base.identifier == "knots"
    assert len(profile.launchers) == 2
    profile = profile.get_merged_profile()
    assert len(profile.launchers) == 3
    launchers = profile.launchers.get_with_base_merged()
    assert len(launchers) == 2
    launchers = launchers.unserialize()
    assert isinstance(launchers[0], kloch.launchers.RezEnvLauncher)
    assert isinstance(launchers[1], kloch.launchers.SystemLauncher)
    assert launchers[1].environ == PROFILE_DELTA_ENVIRON


def test_launcher_required_fields():
    @dataclasses.dataclass
    class TestLauncher(kloch.launchers.BaseLauncher):
        params: list[str] = dataclasses.field(default_factory=list)

        required_fields = ["environ"]

        @classmethod
        def name(cls) -> str:
            return ""

        @classmethod
        def summary(cls) -> str:
            return ""

        @classmethod
        def doc(cls) -> list[str]:
            return [""]

        def execute(self, tmpdir: Path, command: Optional[list[str]] = None) -> int:
            pass

    asdict = {"params": ["--verbose"]}

    with pytest.raises(ValueError) as error:
        launcher = TestLauncher.from_dict(asdict)
        assert "required field" in error

    asdict = {"params": ["--verbose"], "environ": {"PATH": "foo"}}
    launcher = TestLauncher.from_dict(asdict)
    assert launcher.environ == {"PATH": "foo"}