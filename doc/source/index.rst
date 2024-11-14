kloch
=====

.. warning::

   Despite being public, this repository is still in development stage and
   have not been tested extensively yet.

``kloch`` `/klˈoʃ/` [1]_ [2]_, is a configuration system for launching software.

Configurations are `yaml <https://en.wikipedia.org/wiki/YAML>`_ files referred
as `environment profile` which specify the parameters for one or
multiple pre-defined launchers.

.. literalinclude:: _injected/demo-fileformat/profile.yml
   :language: yaml
   :caption: a profile with the configuration for a `rezenv` launcher which inherit another profile

`Launchers` are internally-defined python objects that specify how to execute
a combinations of options and (optional) command.

To use the profile, one must call the :abbr:`CLI (Command Line Interface)` tool.
The profile example shared above can be launched using:

.. code-block:: shell

   python -m kloch run knots:echoes

Design
------

`kloch` was initially designed as the environment manager layer when used with
the `rez <https://rez.readthedocs.io>`_ package manager.

In a very abstract way, `kloch` is a system that:

-
   :abbr:`serialize (translating a data structure or object state into a
   format that can be stored on disk)` the arguments passed to a pre-defined
   function as yaml files.

   .. code-block:: shell

      myLauncher(optionA="paint.exe", optionB={"PATH": "/foo"})

   becomes:

   .. code-block:: yaml
      :caption: myProfile.yml

      myLauncher:
         optionA: paint.exe
         optionB:
            PATH: /foo

-
   execute that function by unserializing the parameters provided at runtime.

   .. code-block:: python
      :caption: pseudo-code in python

      profile = read_profile("myProfile.yml")
      for launcher_name, launcher_config in profile.items():
         launcher = get_launcher(launcher_name)
         launcher(**launcher_config)


Features
--------

- offer a CLI and a public python API
- custom config format for environment profiles:
   - inheritance
   - inheritance merging rules with token system
- arbitrary profile locations with flexible configuration
- plugin system for launchers


Programming distinctions
------------------------

- robust logging.
- good amount of unittesting
- good documentation with a lot of doc created at code level
- python 3.7+ support (EOL was in June 2023).
- PyYAML as only mandatory external python dependency.
- flexible "meta" configuration from environment variable or config file.
- clear public and private API



Contents
--------

.. toctree::
   :maxdepth: 2
   :caption: user

   Home <self>
   install
   usage
   cli
   file-format
   config

.. toctree::
   :maxdepth: 2
   :caption: developer

   public-api/index
   launcher-plugins
   developer
   changelog
   GitHub <https://github.com/knotsanimation/kloch>

----

**References**

.. [1] https://www.internationalphoneticalphabet.org/ipa-sounds/ipa-chart-with-sounds/#ipachartstart
.. [2] https://unalengua.com/ipa-translate?hl=en&ttsLocale=fr-FR&voiceId=Celine&sl=fr&text=clauche&ttsMode=word&speed=2