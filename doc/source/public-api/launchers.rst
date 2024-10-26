Launchers
=========

.. code-block:: python

   import kloch.launchers

Getters
-------

.. autofunction:: kloch.launchers.get_available_launchers_classes

.. autofunction:: kloch.launchers.get_available_launchers_serialized_classes


Plugins
-------

.. autoclass:: kloch.launchers.LoadedPluginsLaunchers

.. autofunction:: kloch.launchers.check_launcher_plugins

.. autofunction:: kloch.launchers.is_launcher_plugin


Serialized
----------

.. autoclass:: kloch.launchers.LauncherSerializedDict
   :members:
   :show-inheritance:

.. autoclass:: kloch.launchers.LauncherSerializedList
   :members:
   :show-inheritance:


BaseLauncher
------------

.. autoclass:: kloch.launchers.BaseLauncher
   :members:
   :inherited-members:
   :show-inheritance:

.. autoclass:: kloch.launchers.BaseLauncherSerialized
   :members:
   :show-inheritance:

.. autoclass:: kloch.launchers.BaseLauncherFields
   :members:


BaseLauncher Subclasses
-----------------------

.. autoclass:: kloch.launchers.SystemLauncher
   :members:
   :inherited-members:
   :show-inheritance:

.. autoclass:: kloch.launchers.SystemLauncherSerialized
   :members:
   :show-inheritance:

.. autoclass:: kloch.launchers.PythonLauncher
   :members:
   :inherited-members:
   :show-inheritance:

.. autoclass:: kloch.launchers.PythonLauncherSerialized
   :members:
   :show-inheritance:
