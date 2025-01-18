Launchers
=========

A launcher is a fancy python function, but implemented using
:abbr:`OOP (Object Oriented Programming)`.

You can break it in 4 components:

- some user configurable options.
- a execution block that will use the user provided options.
- how it can be serialized in the yaml syntax.
- an unique identifier to refers to it

Kloch comes with a bunch of built-in launchers:

.. exec-inject::

   import kloch.launchers

   launchers = kloch.launchers.get_available_launchers_serialized_classes()
   txt = "\n- ".join([""] + [f"``{launcher.identifier}`` : {launcher.summary}" for launcher in launchers])
   print(txt)

But you can implement as much as you want using the
:doc:`launcher-plugins` system.

The ``.base`` launch is particular because all launchers inherit from it. Which
mean all launcher, even custom will at least have the options of the ``.base``
launcher. But it's also handled differently when specified in a profile file
because its option values will be used as base to merge all the other launchers
values over it (example in :ref:`usage:.base inheritance`).


builtin launchers
-----------------

The following describe how to configure the builtin launchers in the
:doc:`file-format`.

.. exec-inject::
   :filename: _injected/exec-launchers-doc.py

----

**References**

.. [1] https://docs.python.org/3/library/os.path.html#os.path.expandvars
.. [2] ``:`` on UNIX, ``;`` on Windows
.. [4] with https://docs.python.org/3.9/library/pathlib.html#pathlib.Path.resolve
