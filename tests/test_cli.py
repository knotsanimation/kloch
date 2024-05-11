import re

import pytest

import kloch
import kloch.cli
import kloch.launchers


def test__getCli__subcommands():
    argv = [""]
    with pytest.raises(SystemExit):
        kloch.get_cli(argv=argv)

    argv = ["run", "_"]
    cli = kloch.get_cli(argv=argv)
    assert isinstance(cli, kloch.cli.RunParser)

    argv = ["list"]
    cli = kloch.get_cli(argv=argv)
    assert isinstance(cli, kloch.cli.ListParser)


def test__getCli__list(monkeypatch, data_dir, capsys):
    monkeypatch.setenv(kloch.KENV_PROFILE_PATH_ENV_VAR, str(data_dir))

    argv = ["list"]
    cli = kloch.get_cli(argv=argv)
    cli.execute()

    captured = capsys.readouterr()
    assert "Searching 1 locations" in captured.out

    profile_capture = re.search(r"Found (\d+) valid profiles", captured.out)
    assert profile_capture
    assert int(profile_capture.group(1)) >= 1


def test__getCli__list__filter(monkeypatch, data_dir, capsys):
    monkeypatch.setenv(kloch.KENV_PROFILE_PATH_ENV_VAR, str(data_dir))

    name_filter = ".*es:beta"
    argv = ["list", name_filter]
    cli = kloch.get_cli(argv=argv)
    cli.execute()

    captured = capsys.readouterr()
    assert "Searching 1 locations" in captured.out
    assert f"Filter <{name_filter}> specified" in captured.out
    assert "Found 1 valid profiles" in captured.out


def test__getCli__run(monkeypatch, data_dir):
    import subprocess

    class Results:
        command: list[str] = None
        env: dict[str, str] = None

    def patched_subprocess(command, shell, env, *args, **kwargs):
        Results.command = command
        Results.env = env
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setenv(kloch.KENV_PROFILE_PATH_ENV_VAR, str(data_dir))
    monkeypatch.setattr(subprocess, "run", patched_subprocess)

    argv = ["run", "lxm"]
    cli = kloch.get_cli(argv=argv)
    with pytest.raises(SystemExit):
        cli.execute()

    assert Results.command[0].startswith("rez-env")
    assert "python-3.9" in Results.command
    assert "--stats" in Results.command
    assert Results.env.get("LXMCUSTOM") == "1"


def test__getCli__run__command(monkeypatch, data_dir):
    import subprocess

    class Results:
        command: list[str] = None
        env: dict[str, str] = None

    def patched_subprocess(command, shell, env, *args, **kwargs):
        Results.command = command
        Results.env = env
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setenv(kloch.KENV_PROFILE_PATH_ENV_VAR, str(data_dir))
    monkeypatch.setattr(subprocess, "run", patched_subprocess)

    extra_command = ["echo", "a", "bunch", "of", "ÅÍÎÏ˝ÓÔÒÚÆ☃", "--debug"]
    argv = ["run", "system-test", "--"] + extra_command
    cli = kloch.get_cli(argv=argv)
    with pytest.raises(SystemExit):
        cli.execute()

    assert Results.command == ["paint.exe", "new"] + extra_command
    assert Results.env["HEH"] == "(╯°□°）╯︵ ┻━┻)"


def test__getCli__python(data_dir, capsys):
    argv = ["python", str(data_dir / "test-script-a.py")]
    cli = kloch.get_cli(argv=argv)
    with pytest.raises(SystemExit):
        cli.execute()

    result = capsys.readouterr()
    assert f"{kloch.__name__} test script working" in result.out
