import dataclasses
import os
from typing import Dict
from typing import List

import pytest

from kloch.launchers import BaseLauncher
from kloch.launchers import BaseLauncherSerialized
from kloch.launchers.base._serialized import resolve_environ


def test__resolve_environ(monkeypatch):
    monkeypatch.setenv("__TEST__", "SUCCESS")

    src_environ = {
        "PATH": ["$PATH", "D:\\some\\path"],
        "NOTRESOLVED": "foo;$$PATH;D:\\some\\path",
        "NUMBER": 1,
        "ANOTHERONE": "$__TEST__",
        "SUCCESSIVE": "$NUMBER",
    }
    result = resolve_environ(src_environ)
    assert len(result) == len(src_environ)
    assert result["PATH"] != f"$PATH{os.pathsep}D:\\some\\path"
    assert len(result["PATH"]) > len("D:\\some\\path") + 2
    assert result["PATH"].endswith(f"{os.pathsep}D:\\some\\path")
    assert result["NOTRESOLVED"] == f"foo;$PATH;D:\\some\\path"
    assert result["NUMBER"] == "1"
    assert result["ANOTHERONE"] == "SUCCESS"
    assert result["SUCCESSIVE"] == "1"


def test__BaseLauncher__required_fields():
    @dataclasses.dataclass
    class TestLauncher(BaseLauncher):
        params: List[str] = dataclasses.field(default_factory=list)
        # any required field must have a default value of None
        environ: Dict[str, str] = None

        required_fields = ["environ"]

        def execute(self, tmpdir, command=None):  # pragma: no cover
            pass

    with pytest.raises(ValueError) as error:
        TestLauncher(params=["--verbose"])
    assert "required field" in str(error.value)

    launcher = TestLauncher(params=["--verbose"], environ={"PATH": "ghghghgh"})
    assert launcher.environ["PATH"] == "ghghghgh"

    del TestLauncher


def test__BaseLauncherSerialized(data_dir, monkeypatch):
    src_dict = {}
    instance = BaseLauncherSerialized(src_dict)
    instance.validate()
    resolved = instance.resolved()
    assert len(resolved) == 2
    assert BaseLauncherSerialized.fields.environ in resolved
    assert resolved[BaseLauncherSerialized.fields.merge_system_environ] is False

    monkeypatch.chdir(data_dir)

    src_dict = {
        "environ": {
            "PATH": ["$PATH", "D:\\some\\testdir"],
            "NUMBER": 1,
            "SUCCESSIVE": "$NUMBER",
        },
        "cwd": str(data_dir / "notexisting" / ".." / "$NUMBER"),
    }
    instance = BaseLauncherSerialized(src_dict)
    instance.validate()
    assert instance["environ"]["NUMBER"] == 1

    resolved = instance.resolved()
    assert resolved["environ"]["NUMBER"] == "1"
    assert resolved["environ"]["PATH"].endswith("testdir")
    assert resolved["cwd"] == str(data_dir / "1")

    launcher = instance.unserialize()
    assert isinstance(launcher, BaseLauncher)
    assert launcher.command == []
    assert launcher.cwd == str(data_dir / "1")
    assert launcher.environ["NUMBER"] == "1"

    src_dict = {"command": ["arg1", "arg", 2]}
    instance = BaseLauncherSerialized(src_dict)
    with pytest.raises(AssertionError) as error:
        instance.validate()
    assert "must be str" in str(error.value)

    src_dict = {"command": ["arg1", "arg"]}
    instance = BaseLauncherSerialized(src_dict)
    instance.validate()


def test__test__BaseLauncherSerialized__fields():
    fields = BaseLauncherSerialized.fields.iterate()
    assert isinstance(fields[0], dataclasses.Field)


def test__BaseLauncherSerialized__merge_system_environ(data_dir, monkeypatch):
    monkeypatch.setenv("__UNITTEST__", "SUCCESS")

    src_dict = {
        "environ": {
            "PATH": ["HELLOW", "$PATH", "D:\\some\\testdir"],
            "NUMBER": 1,
            "SUCCESSIVE": "$NUMBER",
        },
        "cwd": str(data_dir / "notexisting" / ".." / "$NUMBER"),
    }
    instance = BaseLauncherSerialized(src_dict)
    assert len(instance["environ"]) == 3
    resolved = instance.resolved()
    assert len(resolved["environ"]) > 3
    assert resolved["environ"]["PATH"].startswith("HELLOW")
    assert "__UNITTEST__" in resolved["environ"]

    instance[BaseLauncherSerialized.fields.merge_system_environ] = False
    resolved = instance.resolved()
    assert len(resolved["environ"]) == 3
