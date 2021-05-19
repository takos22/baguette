.. _middlewares:

.. currentmodule:: baguette

Middlewares
===========

A middleware adds a behaviour to every request, they goes between the app and
the handler. You can use the included middlewares or create your own.

Create your own middleware
--------------------------

Class based middleware
**********************

A middleware is a class that is initialized with the next middleware
argument and a :class:`Config` argument.
The class must me an asynchronous callable that takes a :class:`Request`
argument and returns a :class:`Response`.

For example, a middleware that would time the request:

.. code-block:: python
    :linenos:

    import time

    class TimingMiddleware:
        def __init__(self, next_middleware, config):
            self.next_middleware = next_middleware
            self.config = config

        async def __call__(self, request: Request):
            start_time = time.time()
            response = await self.next_middleware(request)
            process_time = time.time() - start_time
            print("{0.method} {0.path} took {1} seconds to be handled".format(request, process_time))
            return response

To add that middleware to the application you have 3 ways to do it:

1.  With the :meth:`app.middleware <Baguette.middleware>` decorator:

    .. code-block:: python

        app = Baguette()

        @app.middleware()
        class TimingMiddleware:
            ...

2.  With the ``middleware`` parameter in :class:`Baguette`:

    .. code-block:: python

        app = Baguette(middlewares=[TimingMiddleware])

3.  With the :meth:`app.add_middleware <Baguette.add_middleware>` method:

    .. code-block:: python

        app = Baguette()
        app.add_middleware(TimingMiddleware)

Function based middleware
*************************

You can also write middlewares in functions for simpler middlewares. The
function must have 2 parameters: the next middleware to call and the request.

For example, the same timing middleware with a function would look like this:

.. code-block:: python
    :linenos:

    import time

    @app.middleware()
    async def timing_middleware(next_middleware, request):
        start_time = time.time()
        response = await next_middleware(request)
        process_time = time.time() - start_time
        print("{0.method} {0.path} took {1} seconds to be handled".format(request, process_time))
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
