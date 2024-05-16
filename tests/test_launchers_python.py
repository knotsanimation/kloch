import subprocess

import kloch.launchers


def test__PythonLauncher(tmp_path, data_dir, capfd):
    script_path = data_dir / "test-script-a.py"
    launcher = kloch.launchers.PythonLauncher(
        command=["first arg"],
        python_file=str(script_path),
        environ={
            "PATH": ["$PATH", "D:\\some\\path"],
        },
    )
    expected_argv = [str(script_path), "first arg", "second arg"]

    launcher.execute(command=["second arg"], tmpdir=tmp_path)
    result = capfd.readouterr()
    assert f"{kloch.__name__} test script working" in result.out
    # XXX: test might fail on unix due to the \r ?
    assert result.out.endswith(f"{str(expected_argv)}\r\n")


def test__PythonLauncher_resolving_envvar(tmp_path, data_dir, monkeypatch):
    class Results:
        command: list[str] = None
        env: dict[str, str] = None

    def patched_subprocess(command, shell, env, *args, **kwargs):
        Results.env = env
        Results.command = command
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setenv("SCRIPTROOT", str(data_dir))
    monkeypatch.setattr(subprocess, "run", patched_subprocess)

    script_path = "${SCRIPTROOT}/test-script-a.py"
    launcher = kloch.launchers.PythonLauncher(
        python_file=script_path,
    )
    expected_path = data_dir / "test-script-a.py"
    launcher.execute(tmpdir=tmp_path)
    assert Results.command[-1] == str(expected_path)


def test__PythonLauncher_resolving_cwd(tmp_path, data_dir, monkeypatch):
    class Results:
        command: list[str] = None
        env: dict[str, str] = None

    def patched_subprocess(command, shell, env, *args, **kwargs):
        Results.env = env
        Results.command = command
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.chdir(str(data_dir))
    monkeypatch.setattr(subprocess, "run", patched_subprocess)

    script_path = "./test-script-a.py"
    launcher = kloch.launchers.PythonLauncher(
        python_file=script_path,
    )
    expected_path = data_dir / "test-script-a.py"
    launcher.execute(tmpdir=tmp_path)
    assert Results.command[-1] == str(expected_path)
