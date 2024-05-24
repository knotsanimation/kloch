import logging

import kloch.launchers
from kloch.launchers import LauncherSerializedDict
from kloch.launchers import LauncherSerializedList

LOGGER = logging.getLogger(__name__)


def test__LauncherSerializedDict():
    launcher_serial = LauncherSerializedDict(
        {
            "+=rezenv": {
                "+=config": {"exclude": "whatever"},
                "requires": {
                    "echoes": "2",
                    "maya": "2023",
                },
            },
            ".base": {
                "environ": {
                    "PATH": ["$PATH", "/foo/bar"],
                    "PROD": "unittest",
                },
            },
        },
    )
    launchers = launcher_serial.to_serialized_list()
    assert len(launchers) == 2
    assert isinstance(launchers[0], kloch.launchers.RezEnvLauncherSerialized)
    assert launchers[0]["requires"]["maya"] == "2023"
    assert isinstance(launchers[1], kloch.launchers.BaseLauncherSerialized)
    assert launchers[1]["environ"]["PATH"] == ["$PATH", "/foo/bar"]


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
        kloch.launchers.RezEnvLauncherSerialized(
            {
                "requires": {"echoes": "2", "maya": "2023"},
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
