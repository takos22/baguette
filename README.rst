baguette - asynchronous web framework
=====================================

.. image:: https://img.shields.io/pypi/v/baguette?color=blue
   :target: https://pypi.python.org/pypi/baguette
   :alt: PyPI version info
.. image:: https://img.shields.io/pypi/pyversions/baguette?color=orange
   :target: https://pypi.python.org/pypi/baguette
   :alt: PyPI supported Python versions
.. image:: https://img.shields.io/pypi/dm/baguette
   :target: https://pypi.python.org/pypi/baguette
   :alt: PyPI downloads
.. image:: https://readthedocs.org/projects/baguette/badge/?version=latest
   :target: https://baguette.readthedocs.io/en/latest/
   :alt: Documentation Status
.. image:: https://img.shields.io/github/license/takos22/baguette?color=brightgreen
   :alt: License: MIT
.. image:: https://img.shields.io/discord/831992562986123376.svg?label=&logo=discord&logoColor=ffffff&color=7389D8&labelColor=6A7EC2
   :target: https://discord.gg/PGC3eAznJ6
   :alt: Discord support server

baguette is an asynchronous web framework for ASGI servers.

Installation
------------

**Python 3.6 or higher is required.**

Run the following command:

.. code:: sh

    pip install baguette

Quickstart
----------

Create an application, in ``example.py``:

.. code:: python

    from baguette import Baguette

    app = Baguette()

    @app.endpoint("/")
    async def index(request):
        return "<h1>Hello world</h1>"

Run the server with `uvicorn <https://www.uvicorn.org/>`_ (``pip install uvicorn``):

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
