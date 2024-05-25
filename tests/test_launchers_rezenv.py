import os
import subprocess
from typing import Dict
from typing import List

import pytest

from kloch.launchers import RezEnvLauncher
from kloch.launchers import RezEnvLauncherSerialized


def test__RezEnvLauncher(monkeypatch, tmp_path):
    class Results:
        command: List[str] = None
        env: Dict[str, str] = None

    def patched_subprocess(command, shell, env, *args, **kwargs):
        Results.env = env
        Results.command = command
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr(subprocess, "run", patched_subprocess)

    launcher = RezEnvLauncher(
        requires={"maya": "2023", "houdini": "20.2"},
        params=["--verbose"],
        config={},
        environ=os.environ.copy(),
    )

    launcher.execute(tmpdir=tmp_path, command=["maya"])

    assert Results.command[0].startswith("rez-env")
    assert Results.command[-1] == "maya"
    assert "maya-2023" in Results.command
    assert "--verbose" in Results.command


def test__RezEnvLauncherSerialized(data_dir, monkeypatch):
    src_dict = {}
    instance = RezEnvLauncherSerialized(src_dict)
    instance.validate()

    src_dict = {
        "requires": {"python": "3.9", "maya": "2023+"},
        "config": str(data_dir),
    }
    instance = RezEnvLauncherSerialized(src_dict)
    with pytest.raises(AssertionError) as error:
        instance.validate()
        assert "must be a dict" in error

    src_dict = {
        "requires": {"python": "3.9", "maya": "2023+"},
    }
    instance = RezEnvLauncherSerialized(src_dict)
    instance.validate()
    assert instance["requires"] == {"python": "3.9", "maya": "2023+"}
