The Python Environment
======================

In a custom installation of the ODS application, the configuration of your
Python environment may depend upon where and/or how you are doing the
deployment.

In a `containerized` or similar deployment, you may install the package
dependencies directly to the provided system Python or the one that is installed
as a part of building the `container`.

If deploying to a VM or other server, it would be consindered best practice to
create a Python virtual environment separate from the system's Python and
install the package dependencies there.

Pipenv
------

The ODST Project uses `Pipenv` for managing the project dependencies. `Pipenv`
uses `Pipfiles` for managing project dependencies and is the officially
recommended Python packaging tool from
`Python.org <https://packaging.python.org/new-tutorials/installing-and-using-packages/>`_.

You can learn more about the `Pipfile` specification on the Python Packaging
Authority's GitHub page for the project at `<https://github.com/pypa/pipfile>`_.

If you are new to using `Pipenv` please read the documentation available at
`<https://docs.pipenv.org/>`_.

Installing Package Dependencies
-------------------------------

Install `Pipenv` using `pip`:

.. code-block:: bash

    pip install pipenv

To install the project's package dependencies to the system Python run:

.. code-block:: bash

    pipenv install --system

To create a virtual environment for the project, run the following commands to
build the virtual environment, install the packages, and read back the virtual
environment's path:

.. code-block:: bash

    pipenv install --two
    pipenv --venv

.. note::

    If you are building a development environment for running tests and building
    documentation, you must run the following command to also install the
    development packages:

    .. code-block:: bash

        pipenv install --dev
