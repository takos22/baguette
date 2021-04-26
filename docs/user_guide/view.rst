.. _view:

.. currentmodule:: baguette

Views
=====

.. _view_func:

View functions
--------------

View functions allow you to handle a request made to a specific route.
There are multiple ways to add them to your app, most notably the :meth:`Baguette.route` decorator:

.. code-block:: python
    :linenos:

    from baguette import Baguette

    app = Baguette()

    @app.route("/")
    async def hello_world():
        return "<h1>Hello world</h1>"

You can specify which methods your function can handle by adding the ``methods`` parameter:

.. code-block:: python
    :linenos:

    from baguette import Baguette

    app = Baguette()

    @app.route("/", methods=["GET", "POST"])
    async def index(request):
        if request.method == "GET":
            return "<h1>Hello from GET</h1>"
        elif request.method == "POST":
            return "<h1>Hello from GET</h1>"

If other methods are requested, the application will respond with a Method Not Allowed response
and a 405 status code.

.. seealso::
    For easier handling of multiple methods, see :ref:`view_class`.

.. _view_class:

View classes
------------

:class:`View` classes allow you to handle a request made to a route with
a function for each method, this is useful when you have multiple METHODS
for the same route and need to handle each method with a different logic.
The most common use case is in an API:
