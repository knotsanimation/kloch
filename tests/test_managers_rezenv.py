import os
import subprocess

import kenvmanager.managers


def test_RezEnvManager_environ(monkeypatch, tmp_path):
    manager = kenvmanager.managers.RezEnvManager(
        requires={"maya": "2023", "houdini": "20.2"},
        params=["--verbose"],
        config={},
        environ={
            "PATH": ["$PATH", "D:\\some\\path"],
            "NOTRESOLVED": "$PATH;D:\\some\\path",
            "NUMBER": 1,
        },
    )

    class Results:
        command: list[str] = None
        env: dict[str, str] = None

    def patched_subprocess(command, shell, env, *args, **kwargs):
        Results.env = env
        Results.command = command
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr(subprocess, "run", patched_subprocess)

    manager.execute(tmpdir=tmp_path)

    assert Results.env["PATH"] != "$PATH;D:\\some\\path"
    assert len(Results.env["PATH"]) > len("D:\\some\\path") + 2
    assert Results.env["PATH"].endswith(f"{os.pathsep}D:\\some\\path")

    assert Results.env["NOTRESOLVED"] == "$PATH;D:\\some\\path"
    assert Results.env["NUMBER"] == "1"