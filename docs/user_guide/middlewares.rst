.. _middlewares:

.. currentmodule:: baguette

Middlewares
===========

A middleware adds a behaviour to every request, they go between the app and
the handler. You can use the included middlewares or create your own.

Create your own middleware
--------------------------

Class based middleware
**********************

To make a middleware, you can subclass the :class:`Middleware` and define the
:meth:`__call__ <Middleware.__call__>` method.
This method must be an asynchronous method that takes a :class:`Request`
argument and returns a :class:`Response`.
To call the next middleware, you can use :attr:`self.next <Middleware.next>`
with ``await self.next(request)``.

For example, a middleware that would time the request:

.. code-block:: python
    :linenos:

    import time
    from baguette import Middleware

    class TimingMiddleware(Middleware):
        async def __call__(self, request: Request):
            start_time = time.perf_counter()
            response = await self.next(request)
            print(
                "{0.method} {0.path} took {1} seconds to be handled".format(
                    request, time.perf_counter() - start_time
                )
            )
            return response

To add that middleware to the application you have 3 ways to do it:

1.  With the :meth:`@app.middleware <Baguette.middleware>` decorator:

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
        start_time = time.perf_counter()
        response = await next_middleware(request)
        print(
            "{0.method} {0.path} took {1} seconds to be handled".format(
                request, time.perf_counter() - start_time
            )
        )
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

Editing requests and reponses
-----------------------------

Middlewares usually edit the request and reponse.

In the :class:`Request`, you can't edit the :meth:`Request.body` method and the
other methods of the request body because they are methods and not attributes.
However there are some methods to remedy to this issue:
:meth:`Request.set_raw_body`, :meth:`Request.set_body`, :meth:`Request.set_json`
and :meth:`Request.set_form`.

For :class:`Response`, it is easier: you can just set the :attr:`Response.body`
to the new response body, or for a :class:`JSONResponse` you can edit the
:attr:`JSONResponse.json`. The only exception is for :class:`FileResponse`, if
you want to change the file, you need to create a new :class:`FileResponse`.
