kenvmanager
===========

``kenvmanager`` is a CLI writen in python, providing the environment managing
task when used along a package manager.

It was designed to be used with `rez <https://rez.readthedocs.io>`_.

``kenvmanager`` define "environment profiles" which are yaml config files
which store a serialized package manager request.

.. literalinclude:: demo-a/profile.yml
   :language: yaml
   :caption: demo-profile.yml

Which can the be used as :

.. code-block:: shell

   python -m kenvmanager run knots:echoes


Contents
--------

.. toctree::
   :maxdepth: 2

   Home <self>
   file-format
   public-api
