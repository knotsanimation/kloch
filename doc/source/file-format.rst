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
| ``inherit``    | **required**    | no                                                                         |
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
of each other" using the ``inherit`` key, or from the CLI.

.. important::

   Only the content of the ``launchers`` root key is merged with the other profile.

Assuming ``profile-B`` is declaring a ``base: profile-A`` then the merge will
happen as follow:

- keep all root keys of ``profile-B`` that are not the ``launchers`` key.
- merge the ``launchers`` as ``profile-A + profile-B``

.. note::

   We use the same term as Python to explain inheritance:
   specifying ``inherit: profileA`` in ``profileB`` can be described as
   ``profileA`` is the *super* profile of the *sub* profile ``profileB``


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
of the current profile with the value of the profile specified in ``inherit``.

A merge token:

- MUST only appear in keys
- MUST be prefixed to its key
- CAN be optional

The following merge tokens are available:

.. include:: _injected/tokens.rst

Here is an example making use of all of the tokens and the python API used to merge:

.. exec_code::
   :filename: _injected/exec-fileformat-token-append.py
   :language_output: python

Context Tokens
______________

Those tokens are exclusive to the launcher's name key and allow to
specify for which system context the launcher must be used. This allow you
for example to have a same launcher with 2 different configuration depending
on the operating system.

A context token:

- MUST only appear in the ``{launcher name}`` key
- MUST be suffixed to the launcher name
- CAN be optional

A context have several property, to declare which properties the launcher
must match you use the following syntax:

.. code-block:: bash

   @{property name}={property value}
   # multiple properties can be chained
   @{property name}={property value}@{property name}={property value}@...

.. tip::

   If you need the literal ``@`` character in the launcher name or in the
   properties values you can escape it by doubling it like ``@@``.

The following context properties are availables:

.. exec-inject::
   :filename: _injected/exec-fileformat-token-context.py

Context tokens are then used with the following logic:

- when reading a profile, a context is created from the current system.
- this context is used to **filter out** launcher which doesn't match it.
   - example: ``.system@os=linux: ...`` will be deleted if the current os = windows.
- the remaining launchers which points to the same launcher are then merged
  from top to bottom using the same Merge Tokens logic, thus leaving only
  a launcher name with no context token at the end.

Example:

.. literalinclude:: _injected/demo-usage-tokens/profile-c.yml
  :language: YAML

In the above example we use the builtin system launcher to run a different
command depending on the operating system. Make note that if the os is ``mac``
then this mean the ``.system`` launcher will just not exist at all in the profile !

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

   kloch resolve knots:echoes --profile_roots ./profiles/

.. exec_code::
   :hide_code:
   :filename: _injected/demo-fileformat/exec-merge.py
   :language_output: yaml

----

**References**

.. [1] https://docs.python.org/3/library/os.path.html#os.path.expandvars
.. [2] ``:`` on UNIX, ``;`` on Windows
.. [4] with https://docs.python.org/3.9/library/pathlib.html#pathlib.Path.resolve
