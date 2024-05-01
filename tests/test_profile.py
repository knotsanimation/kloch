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
