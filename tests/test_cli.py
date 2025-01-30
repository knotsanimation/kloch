import os
import re
import sys
from pathlib import Path
from typing import Dict
from typing import List
from typing import Union

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
    monkeypatch.setenv(kloch.Environ.CONFIG_PROFILE_ROOTS, str(data_dir))

    argv = ["list"]
    cli = kloch.get_cli(argv=argv)
    cli.execute()

    captured = capsys.readouterr()
    assert "Searching 1 locations" in captured.out

    profile_capture = re.search(r"Found (\d+) valid profiles", captured.out)
    assert profile_capture
    assert int(profile_capture.group(1)) >= 1


def test__getCli__list__filter(monkeypatch, data_dir, capsys):
    monkeypatch.setenv(kloch.Environ.CONFIG_PROFILE_ROOTS, str(data_dir))

    name_filter = ".*es:beta"
    argv = ["list", name_filter]
    cli = kloch.get_cli(argv=argv)
    cli.execute()

    captured = capsys.readouterr()
    assert "Searching 1 locations" in captured.out
    assert f"Filter <{name_filter}> specified" in captured.out
    assert "Found 1 valid profiles" in captured.out


def test__getCli__list__profile_paths(data_dir, capsys):
    argv = ["list", "--profile_roots", str(data_dir)]
    cli = kloch.get_cli(argv=argv)
    cli.execute()

    captured = capsys.readouterr()
    assert "Searching 1 locations" in captured.out

    profile_capture = re.search(r"Found (\d+) valid profiles", captured.out)
    assert profile_capture
    assert int(profile_capture.group(1)) >= 1


def test__getCli__run__lxm(monkeypatch, data_dir):
    import subprocess

    class Results:
        command: List[str] = None
        env: Dict[str, str] = None

    def patched_subprocess(command, env, *args, **kwargs):
        Results.command = command
        Results.env = env
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setenv(kloch.Environ.CONFIG_PROFILE_ROOTS, str(data_dir))
    monkeypatch.setattr(subprocess, "run", patched_subprocess)

    argv = ["run", "lxm"]
    cli = kloch.get_cli(argv=argv)
    with pytest.raises(SystemExit):
        cli.execute()

    assert Results.command[0].rstrip(".exe").endswith("python")
    assert "test-script-a.py" in Results.command[1]
    assert Results.env.get("LXMCUSTOM") == "1"


def test__getCli__run__lxm__aspath(monkeypatch, data_dir):
    import subprocess

    def patched_subprocess(command, env, *args, **kwargs):
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr(subprocess, "run", patched_subprocess)

    profile_path = data_dir / "profile.lxm.yml"

    argv = ["run", str(profile_path)]
    cli = kloch.get_cli(argv=argv)
    with pytest.raises(SystemExit) as error:
        cli.execute()
    assert not error.value.code

    profile_path = data_dir / "profile.YEEEEEEHAWWW.yml"

    argv = ["run", str(profile_path)]
    cli = kloch.get_cli(argv=argv)
    with pytest.raises(SystemExit) as error:
        cli.execute()
    assert error.value.code == 1


def test__getCli__run__system_test__command(monkeypatch, data_dir):
    import subprocess

    class Results:
        command: Union[List[str], str] = None
        env: Dict[str, str] = None

    def patched_subprocess(command, env, *args, **kwargs):
        Results.command = command
        Results.env = env
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setenv(kloch.Environ.CONFIG_PROFILE_ROOTS, str(data_dir))
    monkeypatch.setattr(subprocess, "run", patched_subprocess)

    # // test case 1

    extra_command = ["echo", "a", "bunch", "of", "ÅÍÎÏ˝ÓÔÒÚÆ☃", "--debug"]
    argv = ["run", "system-test", "--"] + extra_command
    cli = kloch.get_cli(argv=argv)
    with pytest.raises(SystemExit):
        cli.execute()

    assert isinstance(Results.command, list)
    expected = ["paint.exe", "new"] + extra_command
    assert Results.command == expected
    assert Results.env["HEH"] == "(╯°□°）╯︵ ┻━┻)"

    # // test case 2: command_as_str

    extra_command = ["echo", "a", "bunch", "of", "ÅÍÎÏ˝ÓÔÒÚÆ☃", "--debug"]
    argv = ["run", "system-test-asstr", "--"] + extra_command
    cli = kloch.get_cli(argv=argv)
    with pytest.raises(SystemExit):
        cli.execute()

    assert isinstance(Results.command, str)
    expected = subprocess.list2cmdline(["paint.exe", "new"] + extra_command)
    assert Results.command == expected

    # // test case 3: expand_first_arg

    new_env_path = (
        os.path.dirname(sys.executable) + os.pathsep + os.environ.get("PATH", "")
    )
    monkeypatch.setenv("PATH", new_env_path)

    argv = ["run", "system-expand"]
    cli = kloch.get_cli(argv=argv)
    with pytest.raises(SystemExit):
        cli.execute()

    assert isinstance(Results.command, list)
    result = Path(Results.command[0])
    result = result.with_suffix(result.suffix.lower())
    expected = Path(sys.executable)
    assert result == expected


def test__getCli__run__mult_launcher__error(monkeypatch, data_dir, capsys):
    monkeypatch.setenv(kloch.Environ.CONFIG_PROFILE_ROOTS, str(data_dir))

    argv = ["run", "mult-launchers"]
    cli = kloch.get_cli(argv=argv)
    with pytest.raises(SystemExit, match="111"):
        cli.execute()

    argv = ["run", "mult-launchers", "--launcher", "BABABOEI!!"]
    cli = kloch.get_cli(argv=argv)
    with pytest.raises(SystemExit, match="112"):
        cli.execute()


def test__getCli__run__mult_launcher(monkeypatch, data_dir, capfd):
    monkeypatch.setenv(kloch.Environ.CONFIG_PROFILE_ROOTS, str(data_dir))
    # needed to resolve 'python_file: test-script-a.py' in profile
    monkeypatch.chdir(data_dir)
    argv = ["run", "mult-launchers", "--launcher", ".python"]
    cli = kloch.get_cli(argv=argv)
    with pytest.raises(SystemExit, match="0"):
        cli.execute()

    result = capfd.readouterr()
    assert f"test script working" in result.out


def test__getCli__run__priorities_success(monkeypatch, data_dir, capfd):
    monkeypatch.setenv(kloch.Environ.CONFIG_PROFILE_ROOTS, str(data_dir))
    # needed to resolve 'python_file: test-script-a.py' in profile
    monkeypatch.chdir(data_dir)
    argv = ["run", "priorities-success"]
    cli = kloch.get_cli(argv=argv)
    with pytest.raises(SystemExit, match="0"):
        cli.execute()

    result = capfd.readouterr()
    assert f"success_prio_test" in result.out


def test__getCli__run__priorities_success__python(monkeypatch, data_dir, capfd):
    monkeypatch.setenv(kloch.Environ.CONFIG_PROFILE_ROOTS, str(data_dir))
    # needed to resolve 'python_file: test-script-a.py' in profile
    monkeypatch.chdir(data_dir)
    argv = ["run", "priorities-success", "--launcher", ".python"]
    cli = kloch.get_cli(argv=argv)
    with pytest.raises(SystemExit, match="0"):
        cli.execute()

    result = capfd.readouterr()
    assert f"{kloch.__name__} test script working" in result.out


def test__getCli__run__priorities_fail(monkeypatch, data_dir, capfd):
    monkeypatch.setenv(kloch.Environ.CONFIG_PROFILE_ROOTS, str(data_dir))
    # needed to resolve 'python_file: test-script-a.py' in profile
    monkeypatch.chdir(data_dir)
    argv = ["run", "priorities-fail"]
    cli = kloch.get_cli(argv=argv)
    with pytest.raises(SystemExit, match="111"):
        cli.execute()


def test__getCli__run__nolauncher(monkeypatch, data_dir, capfd):
    monkeypatch.setenv(kloch.Environ.CONFIG_PROFILE_ROOTS, str(data_dir))
    # needed to resolve 'python_file: test-script-a.py' in profile
    monkeypatch.chdir(data_dir)
    argv = ["run", "nolauncher"]
    cli = kloch.get_cli(argv=argv)
    with pytest.raises(SystemExit, match="113"):
        cli.execute()


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


def test__run_cli__logging(monkeypatch, tmp_path):
    log_path = tmp_path / "logs" / "kloch.log"
    monkeypatch.setenv(kloch.Environ.CONFIG_CLI_LOGGING_PATHS, str(log_path))
    assert not log_path.exists()
    with pytest.raises(SystemExit):
        kloch.cli.run_cli(argv=["list"])
    assert log_path.exists()

    assert f"starting {kloch.__name__} v{kloch.__version__}" in log_path.read_text(
        encoding="utf-8"
    )
