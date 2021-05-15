.. _responses:

.. currentmodule:: baguette

Responses
=========

Normal responses
----------------

Handler functions can return many types that will be interpreted by
:func:`make_response` and converted to a :class:`Response`. Here are some
examples of accepted return values:

.. code-block:: python

    return body
    return body, status_code
    return body, headers
    return body, status_code, headers
    return Response(body, status_code, headers)  # not recommended

In these examples, ``body`` can be anything described in the table below,
``status_code`` is an :class:`int` for the HTTP status code and ``headers`` is a
:class:`dict` or a :class:`Headers`.

.. note::
    The :attr:`app.default_headers <Baguette.default_headers>` will be added to
    every response headers.

.. note::
    The default status code is ``200``, except for :class:`EmptyResponse` which
    defaults to ``204``

.. csv-table::
    :header: "Body", "Response class"
    :widths: 10, 51

    ":class:`str`", ":class:`HTMLResponse` if there are any HTML tags in the
    string, else :class:`PlainTextResponse`"
    ":class:`list` or :class:`dict`", ":class:`JSONResponse`"
    ":obj:`None`", ":class:`EmptyResponse`"
    "Anything else", ":class:`PlainTextResponse` with ``body = str(value)``"

Error responses
---------------

HTTP Exceptions
***************

If there are :mod:`HTTP exceptions <~baguette.httpexceptions>` raised in your
handler, a :class:`Response` will be made with :func:`make_error_response` and
will be sent like a normal response.

For example:

.. code-block:: python
    :linenos:

    from baguette.httpexceptions import NotFound

    @app.route("/profile/{username}")
    async def profile(username):
        if username not in users:  # lets assume users is a list of usernames
            raise NotFound()
        ...

This will send a response with a ``Not Found`` body and a ``404`` status code.

.. seealso::
    For a full list of available HTTP exceptions, see
    :mod:`~baguette.httpexceptions`.

Server errors
*************

If you have a python error somewhere in your handler, Baguette will transform it
in a :exc:`~baguette.httpexceptions.InternalServerError` for you. The error
traceback will be included if :attr:`app.debug <Baguette.debug>` is ``True``.

.. code-block:: python
    :linenos:

    app = Baguette(debug=True)

    @app.route("/error")
    async def eror():
        raise Exception

This will send a response with an ``Internal Server Error`` body along with the
error traceback and a ``500`` status code.
