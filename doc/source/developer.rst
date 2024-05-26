Developing
==========

How to work on the library and extend it as needed.

packaging a distributable application
-------------------------------------

My use-case for this tool imply that I need to package it as an easily shareable
application.

For doing so there is the very popular `pyinstaller <https://pyinstaller.org/en/stable/>`_
but my context have brought me to use `nuitka <https://nuitka.net/>`_ instead.

I have found that the pyinstaller app was very slow on a mapped network drive
and by looking for solutions, nuitka seems to produce a build that is 2 times
faster to execute on the mapped network drive.

You can find a build recipe for both packager in the ``scripts/`` directory
at the root of the repository.

They should be pretty straightforward to use and only assume the project ``dev``
dependencies are installed.

.. code-block:: shell

   cd {project root}
   python ./scripts/app-build.py
   ls ./scripts/build/

Both scripts generate the packaged application in the ``scripts/build`` directory.
