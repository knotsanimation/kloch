import logging

import kloch.launchers
from kloch.launchers import LauncherSerializedDict
from kloch.launchers import LauncherSerializedList
from kloch.launchers import LauncherContext
from kloch.launchers import LauncherPlatform

LOGGER = logging.getLogger(__name__)


def test__LauncherSerializedDict():
    launcher_serial = LauncherSerializedDict(
        {
            "+=#python": {
                "python_file": "/foo",
            },
            ".base": {
                "environ": {
                    "PATH": ["$PATH", "/foo/bar"],
                    "PROD": "unittest",
                },
            },
        },
    )
    launcher_classes = kloch.launchers.get_available_launchers_serialized_classes()
    launchers = launcher_serial.to_serialized_list(launcher_classes)
    assert len(launchers) == 2
    assert isinstance(launchers[0], kloch.launchers.PythonLauncherSerialized)
    assert launchers[0]["python_file"] == "/foo"
    assert isinstance(launchers[1], kloch.launchers.BaseLauncherSerialized)
    assert launchers[1]["environ"]["PATH"] == ["$PATH", "/foo/bar"]


def test__LauncherSerializedDict__filter():
    launcher_serial = LauncherSerializedDict(
        {
            "system@os=windows": {
                "command": "powershell script.ps1",
            },
            "system@os=linux": {
                "command": "bash script.sh",
            },
            ".base": {
                "environ": {
                    "PATH": ["$PATH", "/foo/bar"],
                    "PROD": "unittest",
                },
            },
        },
    )
    context = LauncherContext(platform=LauncherPlatform.windows)
    result = launcher_serial.get_filtered_context(context)
    assert result is not launcher_serial
    assert "system@os=linux" in launcher_serial
    assert "system@os=linux" not in result
    assert "system@os=windows" in result
    assert ".base" in result

    launcher_serial = LauncherSerializedDict(
        {
            ".base@user=tester": {
                "envion": {"TESTING": "1"},
            },
            ".base": {
                "environ": {
                    "PATH": ["$PATH", "/foo/bar"],
                    "PROD": "unittest",
                },
            },
        },
    )
    context = LauncherContext(platform=LauncherPlatform.windows, user="tester")
    result = launcher_serial.get_filtered_context(context)
    assert ".base@user=tester" in result
    assert ".base" in result


def test__LauncherSerializedDict__with_context_resolved():
    launcher_serial = LauncherSerializedDict(
        {
            "system@os=windows": {
                "command": "powershell script.ps1",
            },
            "system@os=linux": {
                "!=command": "bash script.sh",
            },
            ".base@user=tester": {
                "environ": {"TESTING": "1"},
            },
            ".base": {
                "environ": {
                    "PATH": ["$PATH", "/foo/bar"],
                    "PROD": "unittest",
                },
            },
        },
    )
    expected = LauncherSerializedDict(
        {
            "system": {
                "command": "powershell script.ps1",
            },
            ".base": {
                "environ": {
                    "TESTING": "1",
                    "PATH": ["$PATH", "/foo/bar"],
                    "PROD": "unittest",
                },
            },
        },
    )
    result = launcher_serial.with_context_resolved()
    assert result == expected


def test__LauncherSerializedList():
    src_list = [
        kloch.launchers.BaseLauncherSerialized(
            {
                "environ": {
                    "PATH": ["$PATH", "/foo/bar"],
                    "PROD": "unittest",
                    "SOME_LIST": [".base"],
                },
            }
        ),
        kloch.launchers.PythonLauncherSerialized(
            {
                "python_file": "/foo",
                "+=environ": {
                    "+=PATH": ["/rez"],
                    "REZVERBOSE": 2,
                    "SOME_LIST": ["rez"],
                },
            }
        ),
    ]
    launcher_serial = LauncherSerializedList(src_list)
    # check copied on instancing
    src_list.append(5)
    assert 5 not in launcher_serial
    assert len(launcher_serial) == 2

    launcher_serial = launcher_serial.with_base_merged()
    assert len(launcher_serial) == 1
    environ = launcher_serial[0]["+=environ"]
    assert len(environ) == 4
    assert environ["+=PATH"] == ["$PATH", "/foo/bar", "/rez"]
