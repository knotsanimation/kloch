Input/Output
============

.. code-block:: python

   import kloch
   import kloch.filesyntax

..
   we do a private module import else autodoc doesn't work properly when variable is namespaced

.. autodata:: kloch.filesyntax._io.KENV_PROFILE_PATH_ENV_VAR

.. autofunction:: kloch.add_profile_location
.. autofunction:: kloch.get_profile_locations
.. autofunction:: kloch.get_all_profile_file_paths
.. autofunction:: kloch.get_profile_file_path
.. autofunction:: kloch.serialize_profile
.. autofunction:: kloch.write_profile_to_file
.. autofunction:: kloch.read_profile_from_file
