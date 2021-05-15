.. _quickstart:

.. currentmodule:: baguette

Quickstart
==========

This page gives a brief introduction to the baguette module.
It assumes you have baguette installed, if you don't check the
:ref:`installing` portion.

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

Make sure to have an :ref:`ASGI server <installing_asgi_server>` installed.
Then simply run the server via:

.. code:: sh

    uvicorn hello-world:app

You can also add the following code to the end of your program:

.. code-block:: python
    :linenos:
    :lineno-start: 9

    if __name__ == "__main__":
        app.run()

This will run your app on http://127.0.0.1:8000 by default, you can change the
host and the port with ``app.run(host="1.2.3.4", port=1234)`` if you want to
run it on ``http://1.2.3.4:1234``. For more options, see
:meth:`app.run <Baguette.run>`.
