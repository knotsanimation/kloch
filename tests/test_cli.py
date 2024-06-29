import re
from typing import Dict
from typing import List

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


def test__getCli__list__default(capsys):
    argv = ["list"]
    cli = kloch.get_cli(argv=argv)
    cli.execute()

    captured = capsys.readouterr()
    assert "Searching 0 locations" in captured.out


def test__getCli__list(monkeypatch, data_dir, capsys):
    monkeypatch.setenv(kloch.Environ.CONFIG_PROFILE_PATHS, str(data_dir))

    argv = ["list"]
    cli = kloch.get_cli(argv=argv)
    cli.execute()

    captured = capsys.readouterr()
    assert "Searching 1 locations" in captured.out

    profile_capture = re.search(r"Found (\d+) valid profiles", captured.out)
    assert profile_capture
    assert int(profile_capture.group(1)) >= 1


def test__getCli__list__filter(monkeypatch, data_dir, capsys):
    monkeypatch.setenv(kloch.Environ.CONFIG_PROFILE_PATHS, str(data_dir))

    name_filter = ".*es:beta"
    argv = ["list", name_filter]
    cli = kloch.get_cli(argv=argv)
    cli.execute()

    captured = capsys.readouterr()
    assert "Searching 1 locations" in captured.out
    assert f"Filter <{name_filter}> specified" in captured.out
    assert "Found 1 valid profiles" in captured.out


def test__getCli__list__profile_paths(data_dir, capsys):
    argv = ["list", "--profile_paths", str(data_dir)]
    cli = kloch.get_cli(argv=argv)
    cli.execute()

    captured = capsys.readouterr()
    assert "Searching 1 locations" in captured.out

    profile_capture = re.search(r"Found (\d+) valid profiles", captured.out)
    assert profile_capture
    assert int(profile_capture.group(1)) >= 1


def test__getCli__run(monkeypatch, data_dir):
    import subprocess

    class Results:
        command: List[str] = None
        env: Dict[str, str] = None

    def patched_subprocess(command, env, *args, **kwargs):
        Results.command = command
        Results.env = env
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setenv(kloch.Environ.CONFIG_PROFILE_PATHS, str(data_dir))
    monkeypatch.setattr(subprocess, "run", patched_subprocess)

    argv = ["run", "lxm"]
    cli = kloch.get_cli(argv=argv)
    with pytest.raises(SystemExit):
        cli.execute()

    assert Results.command[0].rstrip(".exe").endswith("python")
    assert "test-script-a.py" in Results.command[1]
    assert Results.env.get("LXMCUSTOM") == "1"


def test__getCli__run__command(monkeypatch, data_dir):
    import subprocess

    class Results:
        command: List[str] = None
        env: Dict[str, str] = None

    def patched_subprocess(command, shell, env, *args, **kwargs):
        Results.command = command
        Results.env = env
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setenv(kloch.Environ.CONFIG_PROFILE_PATHS, str(data_dir))
    monkeypatch.setattr(subprocess, "run", patched_subprocess)

    extra_command = ["echo", "a", "bunch", "of", "ÅÍÎÏ˝ÓÔÒÚÆ☃", "--debug"]
    argv = ["run", "system-test", "--"] + extra_command
    cli = kloch.get_cli(argv=argv)
    with pytest.raises(SystemExit):
        cli.execute()

    assert Results.command == ["paint.exe", "new"] + extra_command
    assert Results.env["HEH"] == "(╯°□°）╯︵ ┻━┻)"


def test__getCli__python(data_dir, capsys):
    argv = ["python", str(data_dir / "test-script-a.py"), "some args ?", "test !"]
    cli = kloch.get_cli(argv=argv)
    with pytest.raises(SystemExit):
        cli.execute()

    result = capsys.readouterr()
    assert f"{kloch.__name__} test script working" in result.out


def test__getCli__python__implicit(data_dir, capsys):
    script_path = data_dir / "test-script-a.py"
    argv = [str(script_path), "some args ?", "test !"]
    cli = kloch.get_cli(argv=argv)
    with pytest.raises(SystemExit):
        cli.execute()

    result = capsys.readouterr()
    assert f"{kloch.__name__} test script working" in result.out
    assert result.out.endswith(f"{str(argv)}\n")


def test__getCli__plugins__undefined(data_dir, capsys):
    argv = ["plugins"]
    cli = kloch.get_cli(argv=argv)
    with pytest.raises(SystemExit):
        cli.execute()

    result = capsys.readouterr()
    assert "found" not in result.out


def test__getCli__plugins(monkeypatch, data_dir, capsys):
    plugin_path = data_dir / "plugins-behr"
    monkeypatch.syspath_prepend(plugin_path)
    plugin_path = data_dir / "plugins-tyfa"
    monkeypatch.syspath_prepend(plugin_path)
    monkeypatch.setenv(
        kloch.KlochConfig.get_field("launcher_plugins").metadata["environ"],
        "kloch_behr,kloch_tyfa",
    )

    argv = ["plugins"]
    cli = kloch.get_cli(argv=argv)
    with pytest.raises(SystemExit):
        cli.execute()

    result = capsys.readouterr()
    assert "found 2" in result.out
    assert str(plugin_path) in result.out


def test__getCli__plugins__arg__launcher_plugin(monkeypatch, data_dir, capsys):
    plugin_path = data_dir / "plugins-behr"
    monkeypatch.syspath_prepend(plugin_path)
    plugin_path = data_dir / "plugins-tyfa"
    monkeypatch.syspath_prepend(plugin_path)

    argv = ["plugins", "--launcher_plugins", "kloch_behr", "kloch_tyfa"]
    cli = kloch.get_cli(argv=argv)
    with pytest.raises(SystemExit):
        cli.execute()

    result = capsys.readouterr()
    assert "found 2" in result.out
    assert str(plugin_path) in result.out
