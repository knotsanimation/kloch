from kloch._dictmerge import MergeableDict


def test__MergeableDict__type():
    d1 = {"+=foo": [1, 2]}
    dm1 = MergeableDict({"+=foo": [1, 2]})
    assert d1 == dm1

    # check copy at instancing
    dm2 = MergeableDict(d1)
    assert dm2 is not d1
    dm2["added"] = True
    assert "added" not in d1

    # check no deepcopy
    arg1 = [1, 2]
    d1 = MergeableDict({"foo": arg1})
    assert d1["foo"] is arg1


def test__MergeableDict__get():
    arg1 = [1, 2]
    d1 = MergeableDict({"+=foo": arg1})
    assert d1.get("foo") is None
    assert d1.get("foo", default=5) is 5
    assert d1.get("foo", default=5, ignore_tokens=True) is arg1

    arg1 = [1, 2]
    d1 = MergeableDict({"foo": arg1})
    assert d1.get("foo") is arg1
    assert d1.get("foo", default=5) is arg1
    assert d1.get("+=foo", default=5, ignore_tokens=True) is arg1


def test__MergeableDict__add():
    dict_root = MergeableDict(
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
    )
    dict_leaf = MergeableDict(
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
    )
    dict_expected = MergeableDict(
        {
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
    )
    result = dict_root + dict_leaf
    assert result == dict_expected

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
    result = result.resolved()
    assert result == expected
    assert not isinstance(result, MergeableDict)


def test__MergeableDict__add__subclass():
    class MyDict(MergeableDict):
        pass

    md1 = MyDict({"+=requires": {"maya": "2020", "houdini": "20"}})
    assert isinstance(md1, MyDict)

    md2 = MyDict({"+=requires": {"maya": "2023", "nuke": "20"}})

    mm = md1 + md2
    assert isinstance(mm, MyDict)


def test__MergeableDict__add__different_type():
    dm1 = MergeableDict(
        {
            "+=rezenv": {
                "+=config": {"exclude": "whatever"},
                "requires": ["houdini-20"],
                "bar": 5,
                "+=params": ["--debug"],
            }
        }
    )
    dm2 = MergeableDict(
        {
            "+=rezenv": {
                "+=config": None,
                "+=requires": "maya-2023",
                "-=bar": "test?",
                "params": "overriden !",
            }
        }
    )
    dmmerged = dm1 + dm2
    assert dmmerged["+=rezenv"]["+=config"] is None
    assert dmmerged["+=rezenv"]["+=requires"] == "maya-2023"
    assert "-=bar" not in dmmerged["+=rezenv"]
    assert "bar" not in dmmerged["+=rezenv"]
    assert dmmerged["+=rezenv"]["params"] == "overriden !"


def test__MergeableDict__add__nested():
    dm1 = MergeableDict(
        {
            "+=rezenv": MergeableDict(
                {
                    "+=config": {"exclude": "whatever"},
                }
            ),
        }
    )
    assert isinstance(dm1["+=rezenv"], MergeableDict)

    dm2 = MergeableDict(
        {
            "+=rezenv": MergeableDict(
                {
                    "+=config": {"include": "IAMINCLUDED"},
                    "+=requires": ["maya-2023"],
                }
            ),
        }
    )
    dmmerged = dm1 + dm2
    assert isinstance(dmmerged["+=rezenv"], MergeableDict)
    assert dmmerged["+=rezenv"]["+=config"] == {
        "exclude": "whatever",
        "include": "IAMINCLUDED",
    }
