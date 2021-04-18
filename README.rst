baguette - asynchronous web framework
=====================================

.. image:: https://img.shields.io/pypi/v/baguette?color=blue
    :target: https://pypi.python.org/pypi/baguette
    :alt: PyPI version info
.. image:: https://img.shields.io/pypi/pyversions/baguette?color=orange
    :target: https://pypi.python.org/pypi/baguette
    :alt: Supported Python versions
.. image:: https://img.shields.io/github/checks-status/takos22/baguette/master?label=tests
    :target: https://github.com/takos22/baguette/actions/workflows/lint-test.yml
    :alt: Lint and test workflow status
.. image:: https://readthedocs.org/projects/baguette/badge/?version=latest
    :target: https://baguette.readthedocs.io/en/latest/
    :alt: Documentation build status
.. image:: https://codecov.io/gh/takos22/baguette/branch/master/graph/badge.svg?token=0P3BV8D3AJ
    :target: https://codecov.io/gh/takos22/baguette
    :alt: Code coverage
.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black
    :alt: Code style: Black
.. image:: https://img.shields.io/discord/831992562986123376.svg?label=&logo=discord&logoColor=ffffff&color=7389D8&labelColor=6A7EC2
    :target: https://discord.gg/PGC3eAznJ6
    :alt: Discord support server

``baguette`` is an asynchronous web framework for ASGI servers.

Installation
------------

**Python 3.6 or higher is required.**

Install ``baguette`` with pip:

.. code:: sh

    pip install baguette

You also need an ASGI server to run your app like `uvicorn <https://www.uvicorn.org/>`_ or `hypercorn <https://gitlab.com/pgjones/hypercorn/>`_.
To install `uvicorn <https://www.uvicorn.org/>`_ directly with baguette, you can add the ``uvicorn`` argument:

.. code:: sh

    pip install baguette[uvicorn]

Quickstart
----------

Create an application, in ``example.py``:

.. code:: python

    from baguette import Baguette

    app = Baguette()

    @app.route("/")
    async def index(request):
        return "<h1>Hello world</h1>"

Run the server with `uvicorn <https://www.uvicorn.org/>`_:

.. code:: sh

    uvicorn example:app

See `uvicorn's deployment guide <https://www.uvicorn.org/deployment/>`_ for more deployment options.

Contribute
----------

- `Source Code <https://github.com/takos22/baguette>`_
- `Issue Tracker <https://github.com/takos22/baguette/issues>`_


Support
-------

If you are having issues, please let me know by joining the discord support server at https://discord.gg/8HgtN6E

License
-------

The project is licensed under the MIT license.

Links
------

- `PyPi <https://pypi.org/project/baguette/>`_
- `Documentation <https://baguette.readthedocs.io/en/latest/index.html>`_
- `Discord support server <https://discord.gg/PGC3eAznJ6>`_
