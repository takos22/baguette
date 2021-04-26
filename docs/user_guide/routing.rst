.. currentmodule:: baguette

.. _routing:

Routing
=======

.. todo::
    Add information about normal routing

.. _dynamic_routing:

Dynamic Routing
---------------

Dynamic routing is useful to pass variables in URLs.
For example, if you want to show a user's profile from their username, you won't hardcode every username,
instead you will pass the username in the URL: ``/profile/{username}``.

To do this with baguette, it's easy:

.. code-block:: python
    :linenos:

    from baguette import Baguette

    app = Baguette()

    @app.route("/profile/<username>")
    async def profile(request, username):
        return f"<h1>{username}'s profile</h1>"

.. _converters:

Converters
**********

Use converters if you want the path parameters to be of a certain type and reject the request otherwise.
For example, if you work with user IDs, you can make sure that the provided user ID is an integer:

.. code-block:: python
    :linenos:

    from baguette import Baguette

    app = Baguette()

    @app.route("/profile/<user_id:int>")
    async def profile(request, user_id):
        # let's assume we have a database from where we can query the user from their ID
        user = User.fetch(id=user_id)
        return f"<h1>{user.name}'s profile</h1>"

You can also pass arguments to the converters to customize how they convert and what they can convert.
For example if you only want strings that have a length of 4:

.. code-block:: python
    :linenos:

    from baguette import Baguette

    app = Baguette()

    @app.route("/text/<text:str(length=4)>")
    async def profile(request, text):
        return f"{text} is 4 characters long"

.. seealso::
    :ref:`api:Path parameters converters`
