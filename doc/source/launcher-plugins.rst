Launcher Plugins
================

A basic plugin system that allow you to add new launchers. The workflow can
be simply described as:

- create a new python module at an arbitrary location
- subclass :any:`BaseLauncher` and :any:`BaseLauncherSerialized` inside
- make sure its parent location is registred in the PYTHONPATH
- append the module name to the ``launcher_plugins`` configuration key

Which could be illustrated by the following commands:

.. code-block:: shell

   cd /d/dev/my-kloch-plugins/
   touch kloch_mylauncher.py
   # edit its content ^
   export PYTHONPATH=$PYTHONPATH:/d/dev/my-kloch-plugins/
   export KLOCH_CONFIG_LAUNCHER_PLUGINS=kloch_mylauncher
   # check if we succesfully registred our plugin
   kloch plugins


As example you can check the content of:

- ``{root}/tests/data/plugins-behr``
- ``{root}/tests/data/plugins-tyfa``


.. tip::

   As kloch plugins need to be in the PYTHONPATH, every python code will be
   able to import them so make sure to pick a name that will not conflict
   with other modules. Prefixing them with ``kloch_`` is recommended.


Creating the subclasses
-----------------------

When creating the a new launcher you would need to create a ``dataclass`` object from
it which subclass :any:`BaseLauncher`, and it's corresponding :any:`BaseLauncherSerialized`
subclass which describe how that dataclass is serialized.

Here is an example which subclass both of those class, in which we create
a launcher for "git cloning":

.. literalinclude:: _injected/snip-launcher-plugin-basic.py
   :language: python
   :caption: kloch_gitclone.py

Registering
-----------

Then add the ``kloch_gitclone.py`` parent location in your PYTHONPATH
so the plugin system can do an ``import kloch_gitclone``.

The last step is to add the module name in the list of launcher plugins to use.
You do this by modifying the kloch configuration, which is explained in :doc:`config`

A quick way to do it is just to set the corresponding environment variable before
starting `kloch`.

.. code-block:: shell

   export KLOCH_CONFIG_LAUNCHER_PLUGINS=kloch_gitclone
