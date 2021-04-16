.. _quickstart:

.. currentmodule:: baguette

Quickstart
==========

This page gives a brief introduction to the library. It assumes you have the library installed,
if you don't check the :ref:`installing` portion.

Minimal website
---------------

Let's see how a very simple app that returns a small HTML response looks.

``hello-world.py``

.. code:: python

    from baguette import Baguette

    app = Baguette()

    @app.route("/")
    async def hello_world(request):
        return "<h1>Hello world</h1>"

Make sure to have an :ref:`installing_asgi_server` installed. Then simply run the server via:

.. code:: sh

    uvicorn hello-world:app
