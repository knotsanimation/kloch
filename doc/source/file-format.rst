Profile File
============

An environment profile is serialized as a `yaml <https://en.wikipedia.org/wiki/YAML>`_ file on disk.

.. hint::

   yaml is an human readable file format that allow to define tree hierarchies
   as `key:value` pair, where the `value` can also be a `key:value` pair and so on ...

Here are the rules defining an environment profile file, files not matching
those rules are discarded:

- The file CAN have an abitrary name.
- The file extension MUST be ``.yml``.
- The file MUST NOT be empty.
- The file MUST have a ``__magic__`` root key with a value starting by ``kloch_profile``.

The content of the file is then defined as:

+----------------+----------------------------------------------------------------------------------------------+
| ➡parent        | :                                                                                            |
+----------------+----------------------------------------------------------------------------------------------+
| ⬇key           |                                                                                              |
+================+=================+============================================================================+
| ``identifier`` | **required**    | yes                                                                        |
+----------------+-----------------+----------------------------------------------------------------------------+
|                | **type**        | `str`                                                                      |
|                +-----------------+----------------------------------------------------------------------------+
|                | **description** | unique arbitrary chain of character used to retrieve a profile             |
+----------------+-----------------+----------------------------------------------------------------------------+
| ``version``    | **required**    | yes                                                                        |
+----------------+-----------------+----------------------------------------------------------------------------+
|                | **type**        | `str`                                                                      |
|                +-----------------+----------------------------------------------------------------------------+
|                | **description** | arbitrary chain of characters indicating the version of this profile       |
+----------------+-----------------+----------------------------------------------------------------------------+
| ``base``       | **required**    | no                                                                         |
+----------------+-----------------+----------------------------------------------------------------------------+
|                | **type**        | `str`                                                                      |
|                +-----------------+----------------------------------------------------------------------------+
|                | **description** | optional ``identifier`` of the profile that must be inherited              |
+----------------+-----------------+----------------------------------------------------------------------------+
| ``launchers``  | **required**    | yes                                                                        |
+----------------+-----------------+----------------------------------------------------------------------------+
|                | **type**        | `dict`                                                                     |
|                +-----------------+----------------------------------------------------------------------------+
|                | **description** | configuration of each launcher                                             |
+----------------+-----------------+----------------------------------------------------------------------------+

Inheritance
-----------

As explained in :doc:`usage` it's possible to merge profiles "on top
of each other" using the ``base`` key, or from the CLI.

.. important::

   Only the content of the ``launchers`` root key is merged with the other profile.

Assuming ``profile-B`` is declaring a ``base: profile-A`` then the merge will
happen as follow:

- keep all root keys of ``profile-B`` that are not the ``launchers`` key.
- merge the ``launchers`` as ``profile-A + profile-B``

By default a merge actually correspond to only keeping ``profile-B`` value (override).
Check the below `tokens` section to see how you can use other merge rules.

Tokens
------

All keys in the ``launchers`` root key can make use of tokens.

A token is a specific
chain of characters that is removed (resolved) in the final config, but allow to
be replaced by a dynamic value or provide contextual information to the key.

Merge Tokens
____________

Those tokens indicate how the value of the key must be merged with a "base"
value of similar type.

In the context of environment profile it indicate how to merge the key/value pair
of the current profile with the value of the profile specified in ``base``.

A merge token:

- MUST only appear in keys
- MUST be prefixed to its key
- CAN be optional

The following merge tokens are available:

+--------------------+-----------------------------------------------------------------+
| token              | description                                                     |
+====================+=================================================================+
| ``+=``             | indicate the key's value should be appended to the base's value |
+--------------------+-----------------------------------------------------------------+
| ``-=``             | indicate the base's key should be removed if it exist           |
+--------------------+-----------------------------------------------------------------+
| `unset`            | no token indicate the key's value replace the base's value      |
+--------------------+-----------------------------------------------------------------+

.. tip::

   The logic imply that if you have a "A key"  with a ``+=`` token, but
   it's parent "B key" has not, then the "A key" token is useless.

   .. code-block:: yaml

      config:
         +=packages_paths:
            - /foobar

      # ^ is the same as ∨
      config:
         packages_paths:
            - /foobar

      # this is probably what is intended
      +=config:
         +=packages_paths:
            - /foobar


Launchers
---------

Specified as key/value pair where the key is the launcher name and the value
its configuration.

+---------------------+------------------------------------------------------------------------------------------------+
| ➡parent             | :launchers                                                                                     |
+---------------------+------------------------------------------------------------------------------------------------+
| ⬇key                |                                                                                                |
+=====================+=================+==============================================================================+
| ``{launcher name}`` | **required**    | no                                                                           |
+---------------------+-----------------+------------------------------------------------------------------------------+
|                     | **type**        | `dict`                                                                       |
|                     +-----------------+------------------------------------------------------------------------------+
|                     | **description** | a registred launcher name with its configuration                             |
+---------------------+-----------------+------------------------------------------------------------------------------+

List of available built-in launchers (see :doc:`launcher-plugins` for extending it):

.. exec-inject::

   import kloch.launchers

   launchers = kloch.launchers.get_available_launchers_serialized_classes()
   txt = "\n- ".join([""] + [f"``{launcher.identifier}`` : {launcher.summary}" for launcher in launchers])
   print(txt)

.. exec-inject::
   :filename: _injected/exec-launchers-doc.py


Examples
--------

Assuming the file structure:

.. container:: columns

   .. container:: column-left

      .. literalinclude:: _injected/demo-fileformat/profile-beta.yml
         :language: yaml
         :caption: ./profiles/beta.yml

   .. container:: column-right

      .. literalinclude:: _injected/demo-fileformat/profile.yml
         :language: yaml
         :caption: ./profiles/prod.yml


We execute the following command:

.. code-block:: shell

   kloch resolve knots:echoes --profile_paths ./profiles/

.. exec_code::
   :hide_code:
   :filename: _injected/demo-fileformat/exec-merge.py
   :language_output: yaml

----

**References**

.. [1] https://docs.python.org/3/library/os.path.html#os.path.expandvars
.. [2] ``:`` on UNIX, ``;`` on Windows
.. [4] with https://docs.python.org/3.9/library/pathlib.html#pathlib.Path.resolve
