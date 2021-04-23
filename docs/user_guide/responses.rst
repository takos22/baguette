.. _responses:

.. currentmodule:: baguette

Responses
=========

The return value from a view function is automatically converted into a :class:`Response` object for you.
The return value will be converted to a :class:`Response` object following the logic described bellow:

#. If the return value is a subclass of :class:`Response`: return it.
#. | If the return value is a tuple in the form ``(response, status)``, ``(response, headers)``, or ``(response, status, headers)``:
     convert the response following the next steps, and replace the status code and the headers with the ones given in the return value.
#. If the return value is a list or a dict: convert it to JSON and return a :class:`JSONResponse`:.
#. If the return value is a string:
    #. If it contains any HTML tags: return an :class:`HTMLResponse`.
    #. Else: return a :class:`PlainTextResponse`
#. If the body is None: return an :class:`EmptyResponse`.
#. Else: convert the body to a string and return a :class:`PlainTextResponse`.
