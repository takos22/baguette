.. currentmodule:: baguette

.. _intro:

Introduction
============

This is the documentation for ``baguette``, a micro web framework for ASGI servers.

Prerequisites
-------------

**Python 3.6 or higher is required.**


.. _installing:

Installing
----------

Install ``baguette`` with pip:

.. tab:: Linux or MacOS

    .. code:: sh

        python3 -m pip install -U baguette

.. tab:: Windows

    .. code:: sh

        py -3 -m pip install -U baguette

.. _installing_asgi_server:

Installing ASGI server
~~~~~~~~~~~~~~~~~~~~~~

You also need an ASGI server to run your app like `uvicorn <https://www.uvicorn.org/>`_ or `hypercorn <https://gitlab.com/pgjones/hypercorn/>`_.
To install `uvicorn <https://www.uvicorn.org/>`_ directly with baguette, you can add the ``uvicorn`` argument:

.. tab:: Linux or MacOS

    .. code:: sh

        python3 -m pip install -U baguette[uvicorn]

.. tab:: Windows

    .. code:: sh

        py -3 -m pip install -U baguette[uvicorn]

You can also install it with pip:

.. tab:: Linux or MacOS

    .. code:: sh

        python3 -m pip install -U uvicorn[standard]

.. tab:: Windows

    .. code:: sh

        py -3 -m pip install -U uvicorn[standard]

.. _venv:

Virtual Environments
~~~~~~~~~~~~~~~~~~~~

Sometimes you want to keep libraries from polluting system installs or use a different version of
libraries than the ones installed on the system. You might also not have permissions to install libraries system-wide.
For this purpose, the standard library as of Python 3.3 comes with a concept called "Virtual Environment"s to
help maintain these separate versions.

A more in-depth tutorial is found on :doc:`py:tutorial/venv`.

However, for the quick and dirty:

1. Go to your project's working directory:

    .. tab:: Linux or MacOS

        .. code:: sh

            cd your-website-dir

    .. tab:: Windows

        .. code:: sh

            cd your-website-dir

2. Create a virtual environment:

    .. tab:: Linux or MacOS

        .. code:: sh

            python3 -m venv venv

    .. tab:: Windows

        .. code:: sh

            py -3 -m venv venv

3. Activate the virtual environment:

    .. tab:: Linux or MacOS

        .. code:: sh

            source venv/bin/activate

    .. tab:: Windows

        .. code:: sh

            venv\Scripts\activate.bat

4. Use pip like usual:

    .. tab:: Linux or MacOS

        .. code:: sh

            pip install -U baguette

    .. tab:: Windows

        .. code:: sh

            pip install -U baguette

Congratulations. You now have a virtual environment all set up. You can start to code, learn more in the :doc:`quickstart`.
