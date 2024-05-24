import os
import subprocess

import pytest

import kloch
from kloch.launchers import BaseLauncherSerialized
from kloch.launchers import PythonLauncherSerialized
from kloch.launchers import PythonLauncher


def test__PythonLauncher(tmp_path, data_dir, capfd):
    script_path = data_dir / "test-script-a.py"
    launcher = PythonLauncher(
        command=["first arg"],
        python_file=str(script_path),
        environ=os.environ.copy(),
    )
    expected_argv = [str(script_path), "first arg", "second arg"]

    launcher.execute(command=["second arg"], tmpdir=tmp_path)
    result = capfd.readouterr()
    assert f"{kloch.__name__} test script working" in result.out
    # XXX: test might fail on unix due to the \r ?
    assert result.out.endswith(f"{str(expected_argv)}\r\n")


def test__PythonLauncherSerialized(data_dir, monkeypatch):
    src_dict = {
        "command": ["first arg", "second arg"],
    }
    instance = PythonLauncherSerialized(src_dict)
    with pytest.raises(AssertionError):
        instance.validate()

    script_path = data_dir / "test-script-a.py"

    src_dict = {
        "python_file": script_path,
    }
    instance = PythonLauncherSerialized(src_dict)
    with pytest.raises(AssertionError):
        instance.validate()

    src_dict = {
        "python_file": str(script_path),
    }
    instance = PythonLauncherSerialized(src_dict)
    instance.validate()
    resolved = instance.resolved()
    assert resolved["python_file"] == str(script_path)

    monkeypatch.setenv("XXUNITTEST", str(data_dir))

    src_dict = {
        "python_file": "${XXUNITTEST}/test-script-a.py",
    }
    instance = PythonLauncherSerialized(src_dict)
    instance.validate()
    resolved = instance.resolved()
    assert resolved["python_file"] == str(script_path)

    launcher = instance.unserialize()
    assert isinstance(launcher, PythonLauncher)
    assert launcher.python_file == str(script_path)


def test__PythonLauncherSerialized__fields():
    base_fields = BaseLauncherSerialized.fields.iterate()
    python_fields = PythonLauncherSerialized.fields.iterate()
    assert len(python_fields) == len(base_fields) + 1
