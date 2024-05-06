# kloch

[![documentation badge](https://img.shields.io/badge/documentation-blue?style=flat&logo=readthedocs&logoColor=white)](https://knotsanimation.github.io/kloch/)
![Made with Python](https://img.shields.io/badge/Python->=3.7-blue?logo=python&logoColor=white)


> [!WARNING]
> Despite being public, this repository is still in development stage and
> have not been tested extensively yet.

![banner with logo and logotype](./doc/source/_static/banner.svg)

``kloch`` _/klˈoʃ/_ is a configuration system for launching software. 
Configurations are yaml files referred as "environment profile" which specify
the parameters for one or multiple pre-defined launchers.

Launchers are internally defined python objects that specify how to execute
a combinations of options and (optional) command.

In a very abstract way, `kloch` is a system that:
- serialize the arguments passed to a pre-defined function as yaml files.
- execute that function by unserializing the parameters provided at runtime.

`kloch` was initially designed as the environment manager layer when used with
the [rez](https://rez.readthedocs.io) package manager.

> Check the detailed documentation at https://knotsanimation.github.io/kloch/
