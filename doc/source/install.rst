Install
=======

`kloch` is a python-based tool with ``PyYAML`` as only dependency.

It's available on `PyPI <https://pypi.org/project/kloch>`_ and can be installed
with:

.. code-block:: shell

   pip install kloch

If you use poetry you can also include it in your project as a git dependency

.. code-block:: shell

   poetry add "git+https://github.com/knotsanimation/kloch.git"

the manual way
--------------

If you don't like all that mess that is the python packaging ecosystem nothing
prevent you to go with a more low-level approach.

You can copy the ``kloch`` directory (the one with an ``__init__.py`` inside)
at any location that is registred in your PYTHONPATH env var.

You just need to ensure PyYAML is also downloaded and accessible in your PYTHONPATH.

Assuming ``python`` is available you coudl use the following recipe:

.. code-block:: shell
   :caption: shell script

   install_dir="/d/demo"
   mkdir $install_dir

   cd ./tmp
   git clone https://github.com/knotsanimation/kloch.git
   cp --recursive ./kloch/kloch "$install_dir/kloch"
   # we should now have /d/demo/kloch/__init__.py

   python -m pip install PyYAML --target "$install_dir"

   export PYTHONPATH="$install_dir"
   python -m kloch --help

