.. _view:

.. currentmodule:: baguette

Views
=====

Views are functions or classes that handle a request made to a route.

.. note::
    Views are also called handlers or endpoints


.. _view_func:

View functions
--------------

View functions must be coroutines (functions defined with ``async def``)
and the ``request`` parameter is optional.

There are multiple ways to add them to your app, most notably
the :meth:`@app.route <Baguette.route>` decorator:

.. code-block:: python
    :linenos:

    from baguette import Baguette

    app = Baguette()

    @app.route("/")
    async def hello_world():
        return "<h1>Hello world</h1>"

You can specify which methods your function can handle by
adding the ``methods`` parameter:

.. code-block:: python
    :linenos:

    from baguette import Baguette

    app = Baguette()

    @app.route("/", methods=["GET", "POST"])
    async def index(request):
        if request.method == "GET":
            return "<h1>Hello from GET</h1>"
        elif request.method == "POST":
            return "<h1>Hello from POST</h1>"

If other methods are requested, the application will respond with a
Method Not Allowed response and a 405 status code.

.. seealso::
    For easier handling of multiple methods, see :ref:`view_class`.

.. _view_class:

View classes
------------

:class:`View` classes allow you to handle a request made to a route with
a function for each method, this is useful when you have multiple METHODS
for the same route and need to handle each method with a different logic.
The most common use case is in an API:

.. code-block:: python
    :linenos:
    :caption: From ``examples/api.py``

    @app.route("/users/<user_id:int>")
    class UserDetail(View):
        async def get(self, user_id: int):
            if user_id not in users:
                raise NotFound(description=f"No user with ID {user_id}")

            return users[user_id]

        async def delete(self, user_id: int):
            if user_id not in users:
                raise NotFound(description=f"No user with ID {user_id}")

            del users[user_id]
            return EmptyResponse()
