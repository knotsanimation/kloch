Usage
=====

Fundamentals
------------

A `package manager` is a collection of software tools that automates the
process of installing, upgrading, configuring, and removing computer programs
for a computer in a consistent manner. [1]_

However you must still specify to the package manager which software you want
to process so you can start using them. This list of software is called an
"environment".

``kenvmanager`` allow to store on disk (serialize) this request of software so
you can create reproducible environment for any user.

Basics
------

   `The following instructions assume you have completed` :doc:`install`.

In its current state, ``kenvmanager`` is designed to work with `rez <https://rez.readthedocs.io>`_.

You can store the `rez-env` request of packages in a config file
that we will refer as `environment profile` or just `profile`.

Imagine you are a VFX production working on an animted movie project. For
that project you wish to use specific version of your creative software and
wish all artists use those same version without having to remember them.

With rez, you have already installed a package for all the desired software version,
like `maya-2023`, `houdini-20`, ...

With ``kenvmanager`` you will be able to create a profile that will "save" this
request of packages:

.. literalinclude:: demo-usage-basics/profile.yml
      :language: yaml
      :caption: basic-profile.yml

Let say we store this profile in a shared location ``/d/pipeline/profiles/``.

The first step is to make our profile discoverable. To do so you can
use environment variable:

.. exec_code::
   :hide_code:
   :language_output: shell

   import kenvmanager
   print("# (shell syntax, to adapt for you context)")
   print(f"export {kenvmanager.KENV_PROFILE_PATH_ENV_VAR}=/d/pipeline/profiles/")

.. tip::

   You can also set locations on the fly by using the ``--profile_paths`` CLI argument.


Then you can validate your manipulation by using the ``list`` command. This
imply we will be using ``kenvmanager`` as a `Command Line Interface` tool [2]_:

.. code-block:: shell

   python -m kenvmanager list

.. exec_code::
   :hide_code:
   :filename: demo-usage-basics/exec-list.py

Time to use your profile:

.. code-block:: shell

   python -m kenvmanager run myMovie

Which in our case should start a rez interactive shell.

.. tip::

   The command line interface tool is documented in :doc:`cli`.

You can also execute a command as multiple argument
specified after a ``--``:

.. code-block:: shell

   python -m kenvmanager run myMovie -- echo "hello world"


Standard workflow
-----------------

Usually the creation of environment for VFX pipeline is much more granular,
meaning we might want to have a profile for each department, e.g. one for
modeling, one for lighting, etc.

It usually lead to a tree-like pipeline hierarchy:

.. code-block:: text

   studio > project > departement > context > ....

To reduce maintenance we would like not to rewrite all our requests
in each profile but instead inherit from each hierarchy level requests.

This is possible with ``kenvmanager`` where a profile can inherit from another
profile.

.. container:: columns

   .. container:: column-left

      .. literalinclude:: demo-usage-standard/profile-a.yml
         :language: yaml
         :caption: /d/pipeline/profiles/studio.yml

   .. container:: column-right

      .. literalinclude:: demo-usage-standard/profile-b.yml
         :language: yaml
         :caption: /d/pipeline/profiles/myMovie.yml

We can notice a few points:

- the ``myMovie`` profile now inherits from the ``myStudio`` profile
  by specifying it in the ``base`` key.
- some keys are prefixed with a ``+=``: this is a token indicating how to merge
  the 2 hierarchies. Without it ``myMovie`` ``requires`` key would totally
  override the one in ``myStudio``.
- we can only inherit one profile at once

If we resolve the ``myMovie`` profile we can see exactly what the final request
to rez will be :

.. code-block:: shell

   python -m kenvmanager resolve myMovie

.. exec_code::
   :hide_code:
   :filename: demo-usage-standard/exec-merge.py
   :language_output: yaml

As you can see the ``requires`` key contain the ``studio_util`` package defined
in ``myStudio`` profile.

.. important::

   The token logic can be tricky to understand at first. Make sure to read
   the full documentation in :doc:`file-format` page.

This example should give you a rough idea at how to build your profiles.

Storing profiles
________________

Profile can be stored at arbitrary location, then inventored in the environment
variable (in most case).

The profile file name is arbitrary and have no specific usage.

We recommend that each of this location is `version controlled` [3]_
(e.g. with Git) to ensure that you can track the history of changes made
to profile during the lifetime of your production/studio.

This is especially important if change made to a profile actually break the
environment and you need to quickly rollback to its previous state.

----

**References**

.. [1] https://en.wikipedia.org/wiki/Package_manager
.. [2] https://en.wikipedia.org/wiki/Command-line_interface
.. [3] https://en.wikipedia.org/wiki/Version_control