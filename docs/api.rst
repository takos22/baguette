.. _api:

.. currentmodule:: baguette

API Reference
=============

The following section documents every class and function in the baguette module.

Version Related Info
--------------------

There are two main ways to query version information about the library.

.. data:: version_info

    A named tuple that is similar to :obj:`py:sys.version_info`.

    Just like :obj:`py:sys.version_info` the valid values for ``releaselevel`` are
    'alpha', 'beta', 'candidate' and 'final'.

.. data:: __version__

    A string representation of the version. e.g. ``'1.0.0rc1'``. This is based
    off of :pep:`440`.

Application
-----------

.. autoclass:: Baguette()
    :members:
    :undoc-members:

View
----

.. autoclass:: View()
    :members:
    :exclude-members: METHODS
    :undoc-members:

Request
-------

.. autoclass:: Request()
    :members:
    :undoc-members:

Responses
---------

Base Response
*************

.. autoclass:: Response()
    :members:
    :exclude-members: CHARSET
    :undoc-members:

Plain Text Response
*******************

.. autoclass:: PlainTextResponse()
    :members:
    :undoc-members:

HTML Response
*************

.. autoclass:: HTMLResponse()
    :members:
    :undoc-members:

JSON Response
*************

.. autoclass:: JSONResponse()
    :members:
    :undoc-members:

Empty Response
**************

.. autoclass:: EmptyResponse()
    :members:
    :undoc-members:

File Response
**************

.. autoclass:: FileResponse()
    :members:
    :undoc-members:

Make Response
*************

.. autofunction:: make_response()

.. autofunction:: make_error_response()

Headers
-------

Headers class
*************

.. autoclass:: Headers()
    :members:
    :undoc-members:

Make Headers
************

.. autofunction:: make_headers()

Forms
-----

Form parsers
************

.. autoclass:: baguette.forms.Form()
    :members:
    :undoc-members:

.. autoclass:: baguette.forms.URLEncodedForm()
    :members:
    :undoc-members:

.. autoclass:: baguette.forms.MultipartForm()
    :members:
    :undoc-members:

Fields
******

.. autoclass:: baguette.forms.Field()
    :members:
    :undoc-members:

.. autoclass:: baguette.forms.FileField()
    :members:
    :undoc-members:

Routing
-------

Router
******

.. autoclass:: baguette.router.Router()
    :members:
    :undoc-members:

Route
*****

.. autoclass:: baguette.router.Route()
    :members:
    :exclude-members: PARAM_ARGS_REGEX, PARAM_CONVERTERS, PARAM_REGEX
    :undoc-members:

Path parameters converters
**************************

.. autoclass:: baguette.converters.StringConverter()
    :members:
    :exclude-members: REGEX
    :undoc-members:
    :inherited-members:

.. autoclass:: baguette.converters.PathConverter()
    :members:
    :exclude-members: REGEX
    :undoc-members:
    :inherited-members:

.. autoclass:: baguette.converters.IntegerConverter()
    :members:
    :exclude-members: REGEX
    :undoc-members:
    :inherited-members:

.. autoclass:: baguette.converters.FloatConverter()
    :members:
    :exclude-members: REGEX
    :undoc-members:
    :inherited-members:

Testing
-------

.. autoclass:: baguette.testing.TestClient()
    :members:
    :undoc-members:
    :member-order: bysource

HTTP Exceptions
---------------

.. automodule:: baguette.httpexceptions
    :members:
    :undoc-members:
    :member-order: bysource

Utils
-----

.. automodule:: baguette.utils
    :members:
    :undoc-members:
    :member-order: bysource
