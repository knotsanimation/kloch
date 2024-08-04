Configuration
=============


Tweak the behavior of the kloch runtime using a configuration system.

Configuration are serialized on disk using yaml file with a simple flat key/value structure:

.. exec-inject::
   :filename: _injected/exec-config-yaml.py

You specify which configuration file to use with the environment variable:

.. exec_code::
   :hide_code:

   import kloch
   print(kloch.Environ.CONFIG_PATH)

Each config key can also be set using an individual environment variable:

.. exec_code::
   :hide_code:
   :filename: _injected/exec-config-envvar.py

Be aware that specifying a config key in an environment variable will
override any value specified in the config file.


Content
-------

.. admonition:: Relative Paths
   :class: tip

   All config **file** key that expect a ``Path`` and whose value is a relative path
   are turned absolute to the config parent directory.

   Example: config is read from ``C:/configs/kloch.yml``,
   then ``cli_session_dir: ../sessions/`` will produce ``C:/sessions/``

.. admonition:: Environment Variables in Paths
   :class: tip

   All config **file** key that expect a ``Path`` can have environment variable that
   will be resolved. Environment variable are specified like ``$MYVAR/mydir``.
   You can escape the resolving by doubling the ``$`` like ``$$myvar/mydir``.

.. program:: config

.. exec-inject::
   :filename: _injected/exec-config-autodoc.py