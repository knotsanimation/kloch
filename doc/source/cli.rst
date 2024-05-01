CLI
===

Command Line Interface documentation.

Usage
-----

Assuming kenvmanager and its dependencies are installed:

.. code-block:: shell

   python -m kenvmanager --help

The CLI can also be started from a python script:

.. code-block:: python

   import kenvmanager
   kenvmanager.get_cli(["--help"])

Commands
--------

``--help``
__________

.. exec_code::

   import kenvmanager
   kenvmanager.get_cli(["--help"])

run
___

.. exec_code::

   import kenvmanager
   kenvmanager.get_cli(["run", "--help"])

list
____

.. exec_code::

   import kenvmanager
   kenvmanager.get_cli(["list", "--help"])

resolve
_______

.. exec_code::

   import kenvmanager
   kenvmanager.get_cli(["resolve", "--help"])