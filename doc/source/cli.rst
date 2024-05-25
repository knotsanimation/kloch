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
   kloch.get_cli(["--help"])

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
