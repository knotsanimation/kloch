# Contributing

Contributing guidelines and workflow for developers.

## pre-requisites

- `git` is available on your system
- `poetry` is available on your system

## getting started

```shell
cd /some/place/to/develop
git clone https://github.com/knotsanimation/kloch.git
cd kloch
# start the python venv
poetry shell
poetry install --all-extras
# create and checkout new branch, DON'T work on main !
git checkout -b <branchname>
```

## running tests

```shell
# useless if you used `install --all-extras`
poetry install --extras tests
python -m pytest ./tests -s
```

## building documentation

build from scratch once:

```shell
# useless if you used `install --all-extras`
poetry install --extras doc
python .doc/build-doc.py
```

build from scratch but start live changes detection:

```shell
# useless if you used `install --all-extras`
poetry install --extras doc
python .doc/serve-doc.py
```

## publishing

`kloch` is published on [PyPI](https://pypi.org/project/kloch/). 
This is an  automatic process performed by GitHub actions `pypi.yml` 
(in `.github/workflows`).
This action is triggered when a new GitHub release is created.

For validation `kloch` is also published
to [TestPyPI](https://test.pypi.org/project/kloch/).
This is also an automatic process performed by GitHub actions `pypi-test.yml`
(in `.github/workflows`). 
This action is triggered when a PR is set "ready-for-review" or when a commit
is pushed to the `main` branch.

Note for the TestPyPI publish:
- TestPyPI is "temporary", repo can be deleted at any time and would need
  to be recreated.
- authentification is done via an API token which may expire at some point and
  would need to be recreated (and added back as secret to this GitHub repo).
