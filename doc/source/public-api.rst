Public API
==========

Summary
-------

.. autosummary::

    kenvmanager
    kenvmanager.cli
    kenvmanager.filesyntax
    kenvmanager.managers
    kenvmanager.add_profile_location
    kenvmanager.EnvironmentProfile
    kenvmanager.get_all_profile_file_paths
    kenvmanager.get_profile_locations
    kenvmanager.get_profile_file_path
    kenvmanager.getCli
    kenvmanager.PackageManagersSerialized
    kenvmanager.read_profile_from_file
    kenvmanager.write_profile_to_file

Command Line Interface
----------------------

.. automodule:: kenvmanager.cli
    :members:

Input/Output
------------

.. autodata:: kenvmanager.filesyntax._io.KENV_PROFILE_PATH_ENV_VAR

.. automodule:: kenvmanager
    :members: write_profile_to_file, read_profile_from_file, add_profile_location, get_profile_locations, get_all_profile_file_paths, get_profile_file_path

Entities
--------

.. automodule:: kenvmanager
    :members: EnvironmentProfile, PackageManagersSerialized

