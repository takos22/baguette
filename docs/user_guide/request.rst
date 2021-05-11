.. _request:

.. currentmodule:: baguette

Request
=======

In order to manipulate the :class:`Request`, you will need to include a
parameter named ``request`` in your handler:

.. code-block:: python
    :linenos:

    @app.route("/")
    async def index(request):
        # do something with the request
        return ...

The :class:`Request` object has many useful attributes,
for example :attr:`Request.method` for the HTTP method used in the request,
:attr:`Request.headers` for the HTTP headers included in the request,
:attr:`Request.path` for the full path requested (without the domain name),
:attr:`Request.querystring` for a :class:`dict` of the querystrings included in the URL,
:attr:`Request.content_type` for the request Content-Type.

You can get the request body with :meth:`Request.body` which will return
a :class:`str` of the full body, decoded with :attr:`Request.encoding`.
If you want to work with a :class:`bytes` body instead of a :class:`str` body,
you can use :meth:`Request.raw_body` which will return a :class:`bytes` of the full body.

.. note::
    :meth:`Request.body` and :meth:`Request.raw_body` are coroutines so you need to ``await``
    them: ``await request.body()``

Here's an example on how to use these:

.. code-block:: python
    :linenos:

    @app.route("/<path:path(allow_empty=True)>")
    async def index(request):
        info = (
            "{0.method} {0.path} HTTP/{0.http_version} {0.content_type}"
            "Headers:\n{0.headers}\n\n{1}"
        ).format(request, await request.body())
        return info

This handler will be called for every path and will return information about the request:
the method, the path, the HTTP version, the content type, the headers and the body.

.. _json_body:

JSON body
---------

If you want to get the body decoded to JSON, you can use :meth:`Request.json`.
It will raise a :exc:`~baguette.httpexceptions.BadRequest` if the request body can't be
decoded as JSON, you can usually not handle this error as it will be handled by the app and
converted to a response with a ``400`` status code.

Here's an example for a user creation endpoint, it gets the username and email from the JSON body:

.. code-block:: python
    :linenos:

    @app.route("/users", methods=["POST"])
    async def user_create(request):
        user = await request.json()

        if not isinstance(user, dict):
            raise BadRequest(description="JSON body must be a dictionnary")

        try:
            username, email = user["username"], user["email"]
        except KeyError:
            raise BadRequest(description="JSON body must include username and email")

        # add the user to database
        ...

        return {"username": username, "email": email}

.. _form_body:

Form body
---------

If you want to use forms, the easiest way to parse them from the request body is with
:meth:`Request.form` which will give you a :class:`~baguette.forms.Form`. It will raise
a :exc:`ValueError` if the :attr:`Request.content_type` isn't one of ``application/x-www-form-urlencoded``
or ``multipart/form-data``. You can also include the querystring arguments as form fields if
some of your data is in the querystring.

The easiest way to use forms is with :class:`View`:

.. code-block:: python
    :linenos:
    :caption: From ``examples/forms.py``

    FORM_HTML = """
    <form action="/" method="POST">
    <div>
        <label for="say">What greeting do you want to say?</label>
        <input name="say" id="say" value="Hi">
    </div>
    <div>
        <label for="to">Who do you want to say it to?</label>
        <input name="to" id="to" value="Mom">
    </div>
    <div>
        <button>Send my greetings</button>
    </div>
    </form>
    """

    @app.route("/")
    class Form(View):
        async def get(self):
            return FORM_HTML

        async def post(self, request):
            form = await request.form()
            return '<h1>Said "{}" to {}</h1>'.format(form["say"], form["to"])
