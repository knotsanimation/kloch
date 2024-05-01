kenvmanager
===========

``kenvmanager`` is an environment manager which wrap requests sent to
package managers.

Those requests are stored as "environment profiles", serialized on disk
as files in the yaml language.

In its current state, it only include support for `rez <https://rez.readthedocs.io>`_.

.. literalinclude:: demo-a/profile.yml
   :language: yaml
   :caption: demo-profile.yml

The above profile can be executed by using the CLI:

.. code-block:: shell

   python -m kenvmanager run knots:echoes

The profile system includes:

- profile inheritance
- token system to determine merging rules during inheritance
- arbitrary profile locations definition through API and environment variable.
- potential support for multiple package manager at once


Contents
--------

.. toctree::
   :maxdepth: 2

   Home <self>
   install
   cli
   file-format
   public-api
