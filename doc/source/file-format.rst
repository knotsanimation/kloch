File Format
===========

An environment profile is serialized as a `yaml <https://en.wikipedia.org/wiki/YAML>`_ file on disk.

.. hint::

   yaml is an human readable file format that allow to define tree hierarchies
   as `key:value` pair, where the `value` can also be a `key:value` pair and so on ...

Here are the rules defining an environment profile file, files not matching
those rules are discarded:

- The file CAN have an abitrary name.
- The file extension MUST be ``.yml``.
- The file MUST NOT be empty.
- The file MUST have a ``__magic__`` root key with a value starting by ``KenvEnvironmentProfile``.

The content of the file is then defined as:

+----------------+----------------------------------------------------------------------------------------------+
| ≻ parent       | :                                                                                            |
+----------------+----------------------------------------------------------------------------------------------+
| ∨ key          |                                                                                              |
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
| ``managers``   | **required**    | yes                                                                        |
+----------------+-----------------+----------------------------------------------------------------------------+
|                | **type**        | `dict`                                                                     |
|                +-----------------+----------------------------------------------------------------------------+
|                | **description** | configuration of each package managers                                     |
+----------------+-----------------+----------------------------------------------------------------------------+

Inheritance
-----------

As explained in :doc:`usage` it's possible to merge profiles "on top
of each other" using the ``base`` key, or from the CLI.

.. important::

   Only the content of the ``managers`` root key is merged with the other profile.

Assuming ``profile-B`` is declaring a ``base: profile-A`` then the merge will
happen as follow:

- keep all root keys of ``profile-B`` that are not the ``managers`` key.
- merge the ``managers`` as ``profile-A + profile-B``

By default a merge actually correspond to only keeping ``profile-B`` value (override).
Check the below `tokens` section to see how you can use other merge rules.

Tokens
------

All keys in the ``managers`` root key can make use of tokens.

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


Package Managers
----------------

+--------------------+------------------------------------------------------------------------------------------------+
| ≻ parent           | :managers                                                                                      |
+--------------------+------------------------------------------------------------------------------------------------+
| ∨ key              |                                                                                                |
+====================+=================+==============================================================================+
| ``{manager name}`` | **required**    | no                                                                           |
+--------------------+-----------------+------------------------------------------------------------------------------+
|                    | **type**        | `dict`                                                                       |
|                    +-----------------+------------------------------------------------------------------------------+
|                    | **description** | a registred package manager name with its configuration                      |
+--------------------+-----------------+------------------------------------------------------------------------------+

List of available managers:

.. exec-inject::

   import kenvmanager.managers

   managers = kenvmanager.managers.get_available_managers_classes()
   txt = "\n- ".join([""] + [f"``{manager.name()}`` : {manager.summary()}" for manager in managers])
   print(txt)

.. exec-inject::
   :filename: exec-managers-doc.py



Examples
--------

Assuming the file structure:

.. container:: columns

   .. container:: column-left

      .. literalinclude:: demo-fileformat/profile-beta.yml
         :language: yaml
         :caption: ./profiles/beta.yml

   .. container:: column-right

      .. literalinclude:: demo-fileformat/profile.yml
         :language: yaml
         :caption: ./profiles/prod.yml


We execute the following command:

.. code-block:: shell

   kenvmanager resolve knots:echoes --profile_paths ./profiles/

.. exec_code::
   :hide_code:
   :filename: demo-fileformat/exec-merge.py
   :language_output: yaml

----

**References**

.. [1] https://docs.python.org/3/library/os.path.html#os.path.expandvars
.. [2] ``:`` on UNIX, ``;`` on Windows
.. [3] There was multiple way of doing it. See `rez ASWF slack discussion <https://academysoftwarefdn.slack.com/archives/C0321B828FM/p1714383583013449>`_
