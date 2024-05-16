import os
from pathlib import Path

import pytest

import kloch.launchers
from kloch import EnvironmentProfile
from kloch import LaunchersSerialized


def test__EnvironmentProfile__merging():
    profile1 = EnvironmentProfile(
        identifier="knots",
        version="0.1.0",
        base=None,
        launchers=LaunchersSerialized(
            {
                "rezenv": {
                    "+=config": {"exclude": "whatever"},
                    "requires": {
                        "echoes": "2",
                        "maya": "2023",
                    },
                    "+=tests": {
                        "+=foo": [1, 2, 3],
                        "deeper!": {"as deep": [1, 2]},
                    },
                },
                "testenv": {"command": "echo $cwd"},
            }
        ),
    )
    profile2 = EnvironmentProfile(
        identifier="knots:echoes",
        version="0.1.0",
        base=profile1,
        launchers=LaunchersSerialized(
            {
                "+=rezenv": {
                    "config": {"include": "yes"},
                    "+=requires": {
                        "-=maya": "_",
                        "-=notAdded": "_",
                        "added": "1.2",
                    },
                    "+=tests": {
                        "+=foo": [4, 5, 6],
                        "+=new-echoes-key": {"working": True},
                        "deeper!": {"+=as deep": [0, 0]},
                    },
                }
            }
        ),
    )
    result = profile2.get_merged_profile().launchers
    expected = {
        "+=rezenv": {
            "config": {"include": "yes"},
            "+=requires": {
                "echoes": "2",
                "added": "1.2",
            },
            "+=tests": {
                "+=foo": [1, 2, 3, 4, 5, 6],
                "+=new-echoes-key": {"working": True},
                "deeper!": {"+=as deep": [0, 0]},
            },
        },
        "testenv": {"command": "echo $cwd"},
    }
    assert result == expected

    result = profile2.get_merged_profile().launchers.get_resolved()
    expected = {
        "rezenv": {
            "config": {"include": "yes"},
            "requires": {
                "echoes": "2",
                "added": "1.2",
            },
            "tests": {
                "foo": [1, 2, 3, 4, 5, 6],
                "new-echoes-key": {"working": True},
                "deeper!": {"as deep": [0, 0]},
            },
        },
        "testenv": {"command": "echo $cwd"},
    }
    assert result == expected


def test__LaunchersSerialized__with_base():
    # test rezenv inherit .base properly when rezenv doesn't define the key

    launcher_serial = LaunchersSerialized(
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
    launchers = launcher_serial.unserialize()
    assert len(launchers) == 1
    launcher = launchers[0]
    assert isinstance(launcher, kloch.launchers.RezEnvLauncher)
    assert not launcher.environ["PATH"].startswith("$PATH")
    assert launcher.environ["PATH"].endswith("/foo/bar")
    assert launcher.environ["PROD"] == "unittest"

    # test rezenv inherit .base properly when rezenv already define the key

    launcher_serial = LaunchersSerialized(
        {
            "+=rezenv": {
                "requires": {"echoes": "2", "maya": "2023"},
                "+=environ": {
                    "+=PATH": ["/rez"],
                    "REZVERBOSE": 2,
                    "SOME_LIST": ["rez"],
                },
            },
            ".base": {
                "environ": {
                    "PATH": ["$PATH", "/foo/bar"],
                    "PROD": "unittest",
                    "SOME_LIST": [".base"],
                },
            },
        },
    )
    launchers = launcher_serial.unserialize()
    launcher = launchers[0]
    assert launcher.environ["PATH"].endswith(
        os.pathsep.join(["/foo/bar", str(Path("/rez").resolve())])
    )
    assert launcher.environ["REZVERBOSE"] == "2"
    assert launcher.environ["PROD"] == "unittest"
    assert launcher.environ["SOME_LIST"] == "rez"

    # test non-supported key in .base

    launcher_serial = LaunchersSerialized(
        {
            "+=rezenv": {"requires": {"echoes": "2"}},
            ".base": {
                "environ": {"PROD": "unittest"},
                "error_key": 5,
            },
        },
    )
    with pytest.raises(TypeError) as error:
        launchers = launcher_serial.unserialize()
        assert "error_key" in str(error)
