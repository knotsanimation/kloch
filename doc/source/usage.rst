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

``kloch`` allow to store on disk (serialize) this request of software so
you can create reproducible environment for any user.

We abstract the package manager concept even more by using "launchers", which
is an arbitrary set of instruction to start an environment and execute software.

Basics
------

For those explanations we will assume the following context:

- we are a VFX production working on an animated movie project.
- we have `developers` working on the software pipeline, and `artists` which are consumers of this pipeline.
- we are using `rez <https://rez.readthedocs.io>`_ as package manager to manage our software infrastructure.

Installation
____________

- First, ensure you have completed the :doc:`install` page.

We then need to ensure our package-manager is available as `launcher`
with kloch. In our case we need to install the `rez env plugin <https://github.com/knotsanimation/kloch-launcher-rezenv>`_.

- Follow the instructions in :doc:`launcher-plugins`.

Goal
____

Now for our goal we would like for our animated movie project, all artists use
the same software versions without having to remember them. So they just say
they want to load the profile "animated movie" and they have access to all
the software in its expected version.

With our package-manager rez, we have already installed a package for all the desired software version,
like `maya-2023`, `houdini-20`, ...

Instructions
____________

With ``kloch`` we will be able to create a profile that will "save" this
request of packages:

.. literalinclude:: _injected/demo-usage-basics/profile.yml
      :language: yaml
      :caption: basic-profile.yml

Let say we store this profile in a shared location ``/d/pipeline/profiles/``.

The first step is to make our profile discoverable. To do so you can
use the environment variable:

.. exec_code::
   :hide_code:
   :language_output: shell

   import kloch
   print("# (shell syntax, to adapt for you context)")
   print(f"export {kloch.Environ.CONFIG_PROFILE_ROOTS}=/d/pipeline/profiles/")

.. tip::

   You can also set locations on the fly by using the ``--profile_roots`` CLI argument.


Then you can validate your manipulation by using the ``list`` command. This
imply we will be using ``kloch`` as a `Command Line Interface` tool [2]_.

.. note::

   Calling kloch will depends on how you installed it, here we will assume kloch
   have been installed in the currently activated python virtual environment and
   we will use ``python -m kloch`` to launch it.

.. code-block:: shell

   python -m kloch list

.. exec_code::
   :hide_code:
   :filename: _injected/demo-usage-basics/exec-list.py

All good, which mean we can use our profile using the ``run`` command:

.. tip::

   The command line interface tool is documented in :doc:`cli`.

.. code-block:: shell

   python -m kloch run myMovie

Which in our case should start a rez interactive shell.

You can also execute a command as multiple argument
specified after a ``--``:

.. code-block:: shell

   python -m kloch run myMovie -- echo "hello world"

.. note::

   Because profiles can also store a command, the CLI command is always
   **appened** to whatever is already defined.

And that are really the fundamentals of kloch design. We have in a way "aliased"
the build of a complex software environment to a `profile` that can be launched
in one line by artists.

Of course nothing force your artist to use the command-line and you could create
a GUI that wraps kloch and yoru available profile to offer a more intuitive
user-experience for them !


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


Profile inheritance
___________________

This is possible with ``kloch`` where a profile can inherit from another
profile.

.. container:: columns

   .. container:: _column

      .. literalinclude:: _injected/demo-usage-standard/profile-a.yml
         :language: yaml
         :caption: /d/pipeline/profiles/studio.yml

   .. container:: _column

      .. literalinclude:: _injected/demo-usage-standard/profile-b.yml
         :language: yaml
         :caption: /d/pipeline/profiles/myMovie.yml

We can notice a few points:

- the ``myMovie`` profile now inherits from the ``myStudio`` profile
  by specifying it in the ``inherit`` key.
- some keys are prefixed with a ``+=``: this is a token indicating how to merge
  the 2 hierarchies. Without it ``myMovie`` ``requires`` key would totally
  override the one in ``myStudio``.
- we can only inherit one profile at once

If we ``resolve`` the ``myMovie`` profile we can see exactly what the final request
to rez will be :

.. code-block:: shell

   python -m kloch resolve myMovie

.. exec_code::
   :hide_code:
   :filename: _injected/demo-usage-standard/exec-merge.py
   :language_output: yaml

As you can see the ``requires`` key contain the ``studio_util`` package defined
in ``myStudio`` profile.

.. important::

   The token logic can be tricky to understand at first. Make sure to read
   the full documentation in :doc:`file-format` page.

.base inheritance
_________________

The above example works fine if you only have one launcher. But profile can
define multiple of them and it is highly probable that you will not use `rez`
to start all your software.

With this use-case comes the need of sharing information between launcher. And
this where the ``.base`` launcher comes into play:

.. container:: columns

   .. container:: _column

      .. literalinclude:: _injected/demo-usage-.base/profile-a.yml
         :language: yaml
         :caption: /d/pipeline/profiles/studio.yml

   .. container:: _column

      .. literalinclude:: _injected/demo-usage-.base/profile-b.yml
         :language: yaml
         :caption: /d/pipeline/profiles/diagnose.yml


Which once merged internally by kloch will produce a ``launchers`` structure like:

.. exec_code::
   :hide_code:
   :filename: _injected/demo-usage-.base/exec-merge.py
   :language_output: yaml

As you can view, we inherit the ``environ`` keys that were defined in the
``.base`` launcher (that is deleted) for both ``system`` and ``@python`` launchers.

It is also good to notice that we define environment variable that re-use previously
defined environment variable, at profile level or system level (``$PATH``).


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

Advices
-------

- When defining paths, always avoid adding trailling slash (``/`` or ``\``).
  That way you know that when joining paths you can always starts by one.


----

**References**

.. [1] https://en.wikipedia.org/wiki/Package_manager
.. [2] https://en.wikipedia.org/wiki/Command-line_interface
.. [3] https://en.wikipedia.org/wiki/Version_control