kloch
=====

.. warning::

   Despite being public, this repository is still in development stage and
   have not been tested extensively yet.

``kloch`` `/klˈoʃ/` [1]_ [2]_, is an environment manager which wrap
:abbr:`requests (usually a collection of software to load with some specific conditions)`
sent to package managers, which we abstract as "launchers".

A launcher is a predefined piece of code which on execution will produce
an environment session as requested, and optionally execute a command.

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

   python -m kloch run knots:echoes

The profile system includes:

- profile inheritance (a profile specify it merge on top of another profile)
- token system to determine merging rules during inheritance
- arbitrary profile locations definition through API and environment variable.
- abstract launcher system to accomodate any package manager or software launching.


Contents
--------

.. toctree::
   :maxdepth: 2
   :caption: user

   Home <self>
   install
   usage
   cli
   file-format

.. toctree::
   :maxdepth: 2
   :caption: developer

   public-api
   developer
   changelog

----

**References**

.. [1] https://www.internationalphoneticalphabet.org/ipa-sounds/ipa-chart-with-sounds/#ipachartstart
.. [2] https://unalengua.com/ipa-translate?hl=en&ttsLocale=fr-FR&voiceId=Celine&sl=fr&text=clauche&ttsMode=word&speed=2