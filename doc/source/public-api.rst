Public API
==========

.. exec_code::
   :hide_code:
   :filename: exec-public-api.py
   :language_output: python



Command Line Interface
----------------------

.. code-block:: python

   import kloch
   import kloch.cli

.. autofunction:: kloch.get_cli

.. autoclass:: kloch.cli.BaseParser
   :members:

Input/Output
------------

.. code-block:: python

   import kloch
   import kloch.filesyntax

.. autodata:: kloch.filesyntax._io.KENV_PROFILE_PATH_ENV_VAR

.. automodule:: kloch
    :members: serialize_profile, write_profile_to_file, read_profile_from_file, add_profile_location, get_profile_locations, get_all_profile_file_paths, get_profile_file_path

Profile Entities
----------------

.. code-block:: python

   import kloch
   import kloch.filesyntax

.. automodule:: kloch
    :members: EnvironmentProfile, LaunchersSerialized

Launchers
---------

.. code-block:: python

   import kloch.launchers

.. automodule:: kloch.launchers
   :members: BaseLauncher, get_available_launchers_classes, get_launcher_class, RezEnvLauncher, SystemLauncher, PythonLauncher
