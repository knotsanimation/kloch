from kloch import EnvironmentProfile
from kloch.launchers import LauncherSerializedDict


def test__EnvironmentProfile__merging():
    profile1 = EnvironmentProfile(
        identifier="knots",
        version="0.1.0",
        inherit=None,
        launchers=LauncherSerializedDict(
            {
                "rezenv": {
                    "config": {"exclude": "whatever"},
                    "==requires": {
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
        inherit=profile1,
        launchers=LauncherSerializedDict(
            {
                "+=rezenv": {
                    "==config": {"include": "yes"},
                    "requires": {
                        "-=maya": "_",
                        "-=notAdded": "_",
                        "added": "1.2",
                    },
                    "+=tests": {
                        "foo": [4, 5, 6],
                        "+=new-echoes-key": {"working": True},
                        "==deeper!": {"+=as deep": [0, 0]},
                    },
                }
            }
        ),
    )
    result = profile2.get_merged_profile().launchers
    expected = {
        "+=rezenv": {
            "==config": {"include": "yes"},
            "requires": {
                "echoes": "2",
                "added": "1.2",
            },
            "+=tests": {
                "foo": [1, 2, 3, 4, 5, 6],
                "+=new-echoes-key": {"working": True},
                "==deeper!": {"+=as deep": [0, 0]},
            },
        },
        "testenv": {"command": "echo $cwd"},
    }
    assert result == expected

    result = profile2.get_merged_profile().launchers.resolved()
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
