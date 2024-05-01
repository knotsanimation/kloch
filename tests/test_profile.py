from kenvmanager import EnvironmentProfileFileSyntax
from kenvmanager import PackageManagersProfile


def test_EnvironmentProfile_merging():
    profile1 = EnvironmentProfileFileSyntax(
        identifier="knots",
        version="0.1.0",
        base=None,
        content=PackageManagersProfile(
            {
                "rezenv": {
                    "requires": ["__maya-2023", "__houdini-20"],
                    "+=tests": {
                        "+=foo": [1, 2, 3],
                        "deeper!": {"as deep": [1, 2]},
                    },
                },
                "testenv": {"command": "echo $cwd"},
            }
        ),
    )
    profile2 = EnvironmentProfileFileSyntax(
        identifier="knots:echoes",
        version="0.1.0",
        base=profile1,
        content=PackageManagersProfile(
            {
                "+=rezenv": {
                    "+=config": {
                        "+=package_filter": [
                            {"excludes": ["after(1429830188)"], "includes": ["foo"]}
                        ]
                    },
                    "requires": [
                        "OK-echoes-1+",
                    ],
                    "+=tests": {
                        "+=foo": [4, 5, 6],
                        "+=new-echoes-key": {"working": True},
                        "deeper!": {"+=as deep": [0, 0]},
                    },
                }
            }
        ),
    )
    result = profile2.get_merged_profile().content
    expected = {
        "+=rezenv": {
            "+=config": {
                "+=package_filter": [
                    {"excludes": ["after(1429830188)"], "includes": ["foo"]}
                ]
            },
            "requires": ["OK-echoes-1+"],
            "+=tests": {
                "+=foo": [1, 2, 3, 4, 5, 6],
                "+=new-echoes-key": {"working": True},
                "deeper!": {"+=as deep": [0, 0]},
            },
        },
        "testenv": {"command": "echo $cwd"},
    }
    assert result == expected
    result = profile2.get_merged_profile().content.get_resolved()
    expected = {
        "rezenv": {
            "config": {
                "package_filter": [
                    {"excludes": ["after(1429830188)"], "includes": ["foo"]}
                ]
            },
            "requires": ["OK-echoes-1+"],
            "tests": {
                "foo": [1, 2, 3, 4, 5, 6],
                "new-echoes-key": {"working": True},
                "deeper!": {"as deep": [0, 0]},
            },
        },
        "testenv": {"command": "echo $cwd"},
    }
    assert result == expected
