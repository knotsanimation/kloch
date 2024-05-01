import re

import pytest

import kenvmanager
import kenvmanager.cli
import kenvmanager.managers


def test_getCli_subcommands():
    argv = [""]
    with pytest.raises(SystemExit):
        kenvmanager.getCli(argv=argv)

    argv = ["run", "_"]
    cli = kenvmanager.getCli(argv=argv)
    assert isinstance(cli, kenvmanager.cli.RunParser)

    argv = ["list"]
    cli = kenvmanager.getCli(argv=argv)
    assert isinstance(cli, kenvmanager.cli.ListParser)


def test_getCli_list(monkeypatch, data_dir, capsys):
    monkeypatch.setenv(kenvmanager.KENV_PROFILE_PATH_ENV_VAR, str(data_dir))

    argv = ["list"]
    cli = kenvmanager.getCli(argv=argv)
    cli.execute()

    captured = capsys.readouterr()
    assert "Searching 1 locations" in captured.out

    profile_capture = re.search(r"Found (\d+) valid profiles", captured.out)
    assert profile_capture
    assert int(profile_capture.group(1)) >= 1


def test_getCli_run(monkeypatch, data_dir):
    import subprocess

    result = []

    def patched_subprocess(*args, **kwargs):
        result.append(args[0])
        return subprocess.CompletedProcess([], 0)

    monkeypatch.setenv(kenvmanager.KENV_PROFILE_PATH_ENV_VAR, str(data_dir))
    monkeypatch.setattr(subprocess, "run", patched_subprocess)

    argv = ["run", "lxm"]
    cli = kenvmanager.getCli(argv=argv)
    with pytest.raises(SystemExit):
        cli.execute()

    assert result[0][0].startswith("rez-env")
