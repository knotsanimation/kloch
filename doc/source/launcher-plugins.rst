Launcher Plugins
================

Kloch comes with a basic plugin system that allow you to add new launchers.
The workflow can be simply described as:

- create a new python module at an arbitrary location
- subclass :any:`BaseLauncher` and :any:`BaseLauncherSerialized` inside
- make sure its parent location is registred in the PYTHONPATH so they can be imported
- append the module name to the ``launcher_plugins`` configuration key

Which could be illustrated by the following bash commands:

.. code-block:: shell

   cd /d/dev/my-kloch-plugins/
   touch kloch_mylauncher.py
   # edit its content ^
   export PYTHONPATH=$PYTHONPATH:/d/dev/my-kloch-plugins/
   export KLOCH_CONFIG_LAUNCHER_PLUGINS=kloch_mylauncher
   # check if we succesfully registred our plugin
   kloch plugins


As example you can check:

- ``{root}/tests/data/plugins-behr``
- ``{root}/tests/data/plugins-tyfa``
- https://github.com/knotsanimation/kloch-launcher-rezenv


Creating the module
-------------------

A plugin for kloch is a regular python module that will be imported and parsed
to find specific object.

So you can create a regular python file at any location, or if you prefer
you can also ship your plugin as a python package by creating a directory
and an ``__init__.py`` file.


.. tip::

   As kloch plugins need to be in the PYTHONPATH, every python code will be
   able to import them so make sure to pick a name that will not conflict
   with other modules. Prefixing them with ``kloch_`` is recommended.


Creating the subclasses
-----------------------

When creating the a new launcher you start by creating a ``dataclass`` object
that declare what are the user-configurable options and how are they "launched".

This is done by subclassing :any:`BaseLauncher`.

Next you need to declare how that dataclass must be serialized, by creating
a subclass of :any:`BaseLauncherSerialized`. This act as a high-level
controller for serialization.

For the granular control over how each field of the dataclass is serialized you
must created another dataclass subclass, but of :any:`BaseLauncherFields`.
Which will just miror the ``BaseLauncher`` field structure, but where each of
its field provide more metadata to unserialize the field.

Here is an example which subclass both of those class, in which we create
a launcher for "git cloning":

.. literalinclude:: _injected/snip-launcher-plugin-basic.py
   :language: python
   :caption: kloch_gitclone.py

.. tip::

   When implementing a field for the user to have control on the launcher,
   it's best to implement it as ``dict`` type over ``list`` because it
   allow users to override one item in particular using the token system.

Registering
-----------

Then add the ``kloch_gitclone.py`` parent location in your PYTHONPATH
so the plugin system can do an ``import kloch_gitclone``.

.. tip::

   PYTHONPATH is the standard mechanism by python to discover and import modules
   but nothing prevent you to use other tools or methods.

   You could for example create a ``pyproject.toml`` which declare ``kloch``
   and your plugin as dependency and let a tool like `uv <https://docs.astral.sh/uv/>`_
   or `poetry <https://python-poetry.org/>`_ create the venv.

   As long as it can be ``import my_plugin_module_name`` it will work !

The last step is to add the module name in the list of launcher plugins to use.
You do this by modifying the kloch configuration, which is explained in :doc:`config`

A quick way to do it is just to set the corresponding environment variable before
starting `kloch`.

.. code-block:: shell

   export KLOCH_CONFIG_LAUNCHER_PLUGINS=kloch_gitclone

You can check your plugin is registred by calling:

.. code-block:: shell

   kloch plugins