# kloch

[![documentation badge](https://img.shields.io/badge/documentation-blue?style=flat&logo=readthedocs&logoColor=white)](https://knotsanimation.github.io/kloch/)
![Made with Python](https://img.shields.io/badge/Python->=3.7-blue?logo=python&logoColor=white)


> [!WARNING]
> Despite being public, this repository is still in development stage and
> have not been tested extensively yet.

![banner with logo and logotype](./doc/source/_static/banner.svg)

``kloch`` _/klˈoʃ/_ is a configuration system for launching software. 
Configurations are yaml files referred as "environment profile" which specify
the parameters for one or multiple pre-defined _launchers_.

_Launchers_ are internally defined python objects that specify how to execute
a combinations of options and (optional) command.

In a very abstract way, `kloch` is a system that:
- serialize the arguments passed to a pre-defined function as yaml files.
- execute that function by unserializing the parameters provided at runtime.

`kloch` was initially designed as the environment manager layer when used with
the [rez](https://rez.readthedocs.io) package manager.

## features

- offer a CLI and a public python API
- custom config format for environment profiles:
  - inheritance
  - inheritance merging rules with token system
- arbitrary profile locations with flexible configuration
- plugin system for launchers

## programming distinctions

- robust logging.
- good amount of unittesting
- good documentation with a lot of doc created at code level
- python 3.7+ support (EOL was in June 2023).
- PyYAML as only mandatory external python dependency.
- flexible "meta" configuration from environment variable or config file.
- clear public and private API

## quick-start

```shell
pip install kloch
kloch --help
# or:
python -m kloch --help 
```


## documentation

Check the detailed documentation at https://knotsanimation.github.io/kloch/
