kenvmanager
===========

``kenvmanager`` is a CLI writen in python, providing the environment managing
task when used along a package manager.

It was designed to be used with `rez <https://rez.readthedocs.io>`_.

``kenvmanager`` define "environment profiles" which are yaml config files
which store a serialized package manager request.

Example of profile:

.. code-block:: yaml

   __magic__: KenvEnvironmentProfile:1
   name: echoes
   identifier: studio
   version: 0.1.0
   content:
     +=rezenv:
       +=params:
         - --verbose
       +=requires:
         - python-3.9+
         - studioLib-2

Which can the be used as :

.. code-block:: shell

   python -m kenvmanager run studio


Contents
--------

.. toctree::
   :maxdepth: 2

   Home <self>
   public-api
