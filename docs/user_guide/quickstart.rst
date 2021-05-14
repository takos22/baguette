.. _quickstart:

.. currentmodule:: baguette

Quickstart
==========

This page gives a brief introduction to the library. It assumes you have the
library installed, if you don't check the :ref:`installing` portion.

Minimal website
---------------

Let's see how a very simple app that returns a small HTML response looks.

.. code-block:: python
    :linenos:
    :caption: ``hello-world.py``

    from baguette import Baguette

    app = Baguette()

    @app.route("/")
    async def hello_world():
        return "<h1>Hello world</h1>"

Just save it as ``hello-world.py`` or something similar. Make sure to not call
your file ``baguette.py`` because this would conflict with Baguette itself.

Make sure to have an :ref:`installing_asgi_server` installed.
Then simply run the server via:

.. code:: sh

    uvicorn hello-world:app
