CLI
===

Command Line Interface documentation.

Usage
-----

Assuming kloch and its dependencies are installed:

.. code-block:: shell

   python -m kloch --help

The CLI can also be started from a python script:

.. code-block:: python

   import kloch
   kloch.run_cli(["--help"])

   # you can also use get_cli to have more control
   # main difference is logging not being configuring
   cli = kloch.get_cli(["..."])
   cli.execute()

Commands
--------

``--help``
__________

.. exec_code::

   import kloch
   kloch.get_cli(["--help"])

run
___

.. exec_code::

   import kloch
   kloch.get_cli(["run", "--help"])

Be aware that the `run` command need to create files on the system. The
location is determined by the :option:`cli_session_dir <config cli_session_dir>`
option. Those locations can be cleared automaticaly based on a
:option:`lifetime option <config cli_session_dir_lifetime>`.

list
____

.. exec_code::

   import kloch
   kloch.get_cli(["list", "--help"])

resolve
_______

.. exec_code::

   import kloch
   kloch.get_cli(["resolve", "--help"])

python
______

.. exec_code::

   import kloch
   kloch.get_cli(["python", "--help"])

plugins
_______

.. exec_code::

   import kloch
   kloch.get_cli(["plugins", "--help"])
