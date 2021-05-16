.. _middlewares:

.. currentmodule:: baguette

Middlewares
===========

Create your own middleware
--------------------------

A middleware is a class that is initialized with a :class:`Baguette` argument,
The class must me an asynchronous callable that takes a :class:`Request`
argument and returns a :class:`Response`.

For example, a middleware that would time the request:

.. code-block:: python
    :linenos:

    import time

    class TimingMiddleware:
        def __init__(self, app, config):
            self.app = app
            self.config = config

        async def __call__(request: Request):
            start_time = time.time()
            response = await self.app(request)
            process_time = time.time() - start_time
            print("{0.method} {0.path} took {} seconds to be handled".format(request, process_time))
            return response

.. _default_middlewares:

Default middlewares
-------------------

There are some middlewares that are in the middleware stack by default.
The middleware stack will be like this:

- :class:`~baguette.middlewares.ErrorMiddleware`
- Your custom middlewares
- :class:`~baguette.middlewares.DefaultHeadersMiddleware`
- :meth:`app.dispatch(request) <Baguette.dispatch>`
