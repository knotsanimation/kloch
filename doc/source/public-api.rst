Public API
==========

.. exec_code::
   :hide_code:
   :filename: exec-public-api.py
   :language_output: python



Command Line Interface
----------------------

.. code-block:: python

   import kenvmanager
   import kenvmanager.cli

.. autofunction:: kenvmanager.get_cli

.. autoclass:: kenvmanager.cli.BaseParser
   :members:

Input/Output
------------

.. code-block:: python

   import kenvmanager
   import kenvmanager.filesyntax

.. autodata:: kenvmanager.filesyntax._io.KENV_PROFILE_PATH_ENV_VAR

.. automodule:: kenvmanager
    :members: serialize_profile, write_profile_to_file, read_profile_from_file, add_profile_location, get_profile_locations, get_all_profile_file_paths, get_profile_file_path

Profile Entities
----------------

.. code-block:: python

   import kenvmanager
   import kenvmanager.filesyntax

.. automodule:: kenvmanager
    :members: EnvironmentProfile, PackageManagersSerialized

Launchers
---------

.. code-block:: python

   import kenvmanager.launchers

.. automodule:: kenvmanager.launchers
   :members: BaseLauncher, get_launcher_class, RezEnvLauncher