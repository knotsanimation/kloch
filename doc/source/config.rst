Configuration
=============

Tweak the behavior of the kloch runtime using a configuration system.

Configuration are serialized on disk using yaml file with a simple flat key/value structure:

.. exec-inject::
   :filename: _injected/exec-config-yaml.py

You specify which configuration file to use with the environment variable:

.. exec_code::
   :hide_code:

   import kloch.config
   print(kloch.config.KLOCH_CONFIG_ENV_VAR)

Each config key can also be set using an individual environment variable:

.. exec_code::
   :hide_code:
   :filename: _injected/exec-config-envvar.py


Content
-------

.. exec-inject::
   :filename: _injected/exec-config-autodoc.py