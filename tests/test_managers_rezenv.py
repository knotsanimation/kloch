import os
import subprocess

import pytest

import kenvmanager.managers


def test_RezEnvManager_required_fields():
    asdict = {"params": ["--verbose"]}

    with pytest.raises(ValueError) as error:
        manager = kenvmanager.managers.RezEnvManager.from_dict(asdict)
        assert "required field" in error


def test_RezEnvManager_environ(monkeypatch, tmp_path):
    manager = kenvmanager.managers.RezEnvManager(
        requires={"maya": "2023", "houdini": "20.2"},
        params=["--verbose"],
        config={},
        environ={
            "PATH": ["$PATH", "D:\\some\\path"],
            "NOTRESOLVED": "foo;$$PATH;D:\\some\\path",
            "NUMBER": 1,
            "ANOTHERONE": "$__TEST__",
        },
    )

    class Results:
        command: list[str] = None
        env: dict[str, str] = None

    def patched_subprocess(command, shell, env, *args, **kwargs):
        Results.env = env
        Results.command = command
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setenv("__TEST__", "SUCCESS")
    monkeypatch.setattr(subprocess, "run", patched_subprocess)

    manager.execute(tmpdir=tmp_path)

    assert Results.env["PATH"] != "$PATH;D:\\some\\path"
    assert len(Results.env["PATH"]) > len("D:\\some\\path") + 2
    assert Results.env["PATH"].endswith(f"{os.pathsep}D:\\some\\path")

    assert Results.env["NOTRESOLVED"] == "foo;$PATH;D:\\some\\path"
    assert Results.env["NUMBER"] == "1"
    assert Results.env["ANOTHERONE"] == "SUCCESS"
