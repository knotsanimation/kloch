File Format
===========

An environment profile is serialized as a yaml file on disk.

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

+----------------+-----------+-----------+----------------------------------------------------------------------+
| :root                                                                                                         |
+----------------+-----------+-----------+----------------------------------------------------------------------+
| key            | required  | type      | description                                                          |
+================+===========+===========+======================================================================+
| ``identifier`` | yes       | `str`     | unique arbitrary chain of character used to retrieve a profile       |
+----------------+-----------+-----------+----------------------------------------------------------------------+
| ``version``    | yes       | `str`     | arbitrary chain of characters indicating the version of this profile |
+----------------+-----------+-----------+----------------------------------------------------------------------+
| ``base``       | no        | `str`     | optional identifier of the profile that must be inherited            |
+----------------+-----------+-----------+----------------------------------------------------------------------+
| ``managers``   | yes       | `dict`    | configuration of the package managers                                |
+----------------+-----------+-----------+----------------------------------------------------------------------+

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



Package Managers
----------------

+--------------------+-----------+-----------+----------------------------------------------------------------------+
| :root:managers                                                                                                    |
+--------------------+-----------+-----------+----------------------------------------------------------------------+
| key                | required  | type      | description                                                          |
+====================+===========+===========+======================================================================+
| ``{manager name}`` | no        | `dict`    | a registred package manager name with its configuration              |
+--------------------+-----------+-----------+----------------------------------------------------------------------+

There is currently 1 package manager registred:

- ``rezenv`` : launch a rez environment using the ``rez-env`` command

+----------------+-----------+-------------------+----------------------------------------------------------------------------------+
| :root:managers:rezenv                                                                                                             |
+----------------+-----------+-------------------+----------------------------------------------------------------------------------+
| key            | required  | type              | description                                                                      |
+================+===========+===================+==================================================================================+
| ``requires``   | yes       | `dict[str,str]`   | a mapping of rez package name: package version                                   |
+----------------+-----------+-------------------+----------------------------------------------------------------------------------+
| ``params``     | no        | `list[str]`       | list of command line arguments passed to rez-env                                 |
+----------------+-----------+-------------------+----------------------------------------------------------------------------------+
| ``config``     | no        | `dict`            | content of a valid yaml rez config that is created on the fly before the rez-env |
+----------------+-----------+-------------------+----------------------------------------------------------------------------------+

Examples
--------

.. container:: columns

   .. container:: column-left

      .. literalinclude:: demo-profile-beta.yml
         :language: yaml
         :caption: a "beta" profile with no inheritance

   .. container:: column-right

      .. literalinclude:: demo-profile.yml
         :language: yaml
         :caption: a profile that inherit from the above "beta" profile


With the request:

.. code-block:: shell

   kenvmanager run knots:echoes

Will generate internally the following profile (can be checked using ``kenvmanager resolve ...``):

.. literalinclude:: demo-profile-merged.yml
   :language: yaml


