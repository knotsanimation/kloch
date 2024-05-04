import pytest

import kenvmanager.launchers
from kenvmanager import EnvironmentProfile
from kenvmanager import PackageManagersSerialized


def test_EnvironmentProfile_merging():
    profile1 = EnvironmentProfile(
        identifier="knots",
        version="0.1.0",
        base=None,
        managers=PackageManagersSerialized(
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
        managers=PackageManagersSerialized(
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
    result = profile2.get_merged_profile().managers
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

    result = profile2.get_merged_profile().managers.get_resolved()
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


def test_PackageManagersSerialized_with_base():
    # test rezenv inherit .base properly when rezenv doesn't define the key

    manager_serial = PackageManagersSerialized(
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
    managers = manager_serial.unserialize()
    assert len(managers) == 1
    manager = managers[0]
    assert isinstance(manager, kenvmanager.launchers.RezEnvLauncher)
    assert manager.environ == {"PATH": ["$PATH", "/foo/bar"], "PROD": "unittest"}
    assert manager.get_resolved_environ()["PATH"].endswith("/foo/bar")
    assert not manager.get_resolved_environ()["PATH"].startswith("$PATH")

    # test rezenv inherit .base properly when rezenv already define the key

    manager_serial = PackageManagersSerialized(
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
    managers = manager_serial.unserialize()
    manager = managers[0]
    assert manager.environ == {
        "PATH": ["$PATH", "/foo/bar", "/rez"],
        "REZVERBOSE": 2,
        "PROD": "unittest",
        "SOME_LIST": ["rez"],
    }

    # test non-supported key in .base

    manager_serial = PackageManagersSerialized(
        {
            "+=rezenv": {"requires": {"echoes": "2"}},
            ".base": {
                "environ": {"PROD": "unittest"},
                "error_key": 5,
            },
        },
    )
    with pytest.raises(TypeError) as error:
        managers = manager_serial.unserialize()
        assert "error_key" in str(error)
