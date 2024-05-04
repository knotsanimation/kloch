Install
=======

`kloch` is a python-based tool with external dependencies.

It uses `poetry <https://python-poetry.org/>`_ to manage its dependencies.
Those are defined in the ``pyproject.toml`` that can be found
at the repository's root :

.. literalinclude:: .pyproject.toml
      :language: toml
      :caption: pyproject.toml

A quick install could look like:

.. code-block:: shell

   git clone https://github.com/knotsanimation/kloch.git
   cd kloch
   poetry install
   poetry run python -m kloch --help
