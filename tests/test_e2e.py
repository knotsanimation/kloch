"""
"end to end" test: as close as possible to real usage conditions

TODO probably need to complexify the data even more
"""

import os
import subprocess
import sys

import kloch


def test_e2e_case1(data_dir, monkeypatch, tmp_path):
    """
    Use environ to define kloch config
    """
    test_data_dir = data_dir / "e2e-1"
    plugin_path = data_dir / "plugins-behr"
    cwd_dir = tmp_path / "cwd"
    cwd_dir.mkdir()
    session_dir = tmp_path / "session"

    environ = os.environ.copy()
    pythonpath = os.environ.get("PYTHONPATH")
    if pythonpath:
        environ["PYTHONPATH"] = f"{pythonpath}{os.pathsep}{plugin_path}"
    else:
        environ["PYTHONPATH"] = f"{plugin_path}"
    environ[kloch.Environ.CONFIG_PROFILE_ROOTS] = str(test_data_dir)
    environ[kloch.Environ.CONFIG_LAUNCHER_PLUGINS] = "kloch_behr"
    environ[kloch.Environ.CONFIG_CLI_SESSION_PATH] = str(session_dir)

    command = [
        sys.executable,
        "-m",
        "kloch",
        "plugins",
        "--debug",
    ]
    result = subprocess.run(command, cwd=cwd_dir, env=environ)
    assert not result.returncode
    assert not list(cwd_dir.glob("*"))

    command = [
        sys.executable,
        "-m",
        "kloch",
        "run",
        "prod",
        "--debug",
        "--",
        "testcommand",
    ]
    result = subprocess.run(command, cwd=cwd_dir, env=environ)
    assert not result.returncode
    assert not list(cwd_dir.glob("*"))

    profile_path = test_data_dir / "profile.prod.yml"

    command = [
        sys.executable,
        "-m",
        "kloch",
        "run",
        str(profile_path),
        "--debug",
        "--",
        "testcommand",
    ]
    result = subprocess.run(command, cwd=cwd_dir, env=environ)
    assert not result.returncode


def test_e2e_case2(data_dir, monkeypatch, tmp_path):
    """
    Use a config file
    """
    test_data_dir = data_dir / "e2e-1"
    plugin_path = data_dir / "plugins-behr"
    cwd_dir = tmp_path / "cwd"
    cwd_dir.mkdir()
    session_dir = tmp_path / "session"

    environ = os.environ.copy()
    pythonpath = os.environ.get("PYTHONPATH")
    if pythonpath:
        environ["PYTHONPATH"] = f"{pythonpath}{os.pathsep}{plugin_path}"
    else:
        environ["PYTHONPATH"] = f"{plugin_path}"
    environ[kloch.Environ.CONFIG_PATH] = str(test_data_dir / "config.yml")
    environ["KLOCHTEST_LOG_PATH"] = str(session_dir / ".log")
    environ["KLOCHTEST_SESSION_PATH"] = str(session_dir)

    command = [
        sys.executable,
        "-m",
        "kloch",
        "plugins",
        "--debug",
    ]
    result = subprocess.run(command, cwd=cwd_dir, env=environ)
    assert not result.returncode
    assert not list(cwd_dir.glob("*"))

    command = [
        sys.executable,
        "-m",
        "kloch",
        "run",
        "prod",
        "--debug",
        "--",
        "testcommand",
    ]
    result = subprocess.run(command, cwd=cwd_dir, env=environ)
    assert not result.returncode
    assert not list(cwd_dir.glob("*"))


def test_e2e_case3(data_dir, monkeypatch, tmp_path):
    """
    Use environ to define kloch config and test profile prodml
    """
    test_data_dir = data_dir / "e2e-1"
    plugin_path = data_dir / "plugins-behr"
    cwd_dir = tmp_path / "cwd"
    cwd_dir.mkdir()
    session_dir = tmp_path / "session"

    environ = os.environ.copy()
    pythonpath = os.environ.get("PYTHONPATH")
    if pythonpath:
        environ["PYTHONPATH"] = f"{pythonpath}{os.pathsep}{plugin_path}"
    else:
        environ["PYTHONPATH"] = f"{plugin_path}"
    environ[kloch.Environ.CONFIG_PROFILE_ROOTS] = str(test_data_dir)
    environ[kloch.Environ.CONFIG_LAUNCHER_PLUGINS] = "kloch_behr"
    environ[kloch.Environ.CONFIG_CLI_SESSION_PATH] = str(session_dir)

    command = [
        sys.executable,
        "-m",
        "kloch",
        "run",
        "prodml",
        "--debug",
        "--launcher",
        "system",
        "--",
        "test_e2e_case3",
    ]
    result = subprocess.run(
        command,
        cwd=cwd_dir,
        env=environ,
        capture_output=True,
        text=True,
    )
    print(result.stdout)
    print(result.stderr, file=sys.stderr)
    assert not result.returncode
    assert result.stdout.strip("\n").endswith("hello from test_e2e_case3")
