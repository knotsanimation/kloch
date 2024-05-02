kenvmanager
===========

``kenvmanager`` is an environment manager which wrap
:abbr:`requests (usually a collection of software to load with some specific conditions)`
sent to package managers.

Those requests are stored as "environment profiles",
:abbr:`serialized (translating a data structure or object state into a format that can be stored on disk)` on disk
as files in the `yaml <https://en.wikipedia.org/wiki/YAML>`_ language.

In its current state, it only include support for `rez <https://rez.readthedocs.io>`_.

.. literalinclude:: demo-fileformat/profile.yml
   :language: yaml
   :caption: demo-profile.yml

The above profile can be executed by using the
:abbr:`CLI (Command Line Interface)` tool:

.. code-block:: shell

   python -m kenvmanager run knots:echoes

The profile system includes:

- profile inheritance (a profile specify it merge on top of another profile)
- token system to determine merging rules during inheritance
- arbitrary profile locations definition through API and environment variable.
- potential (not-tested) support for multiple package manager at once


Contents
--------

.. toctree::
   :maxdepth: 2

   Home <self>
   install
   usage
   cli
   file-format
   public-api
   developer
