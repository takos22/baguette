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

    Just like :obj:`py:sys.version_info` the valid values for ``releaselevel``
    are 'alpha', 'beta', 'candidate' and 'final'.

.. data:: __version__

    A string representation of the version. e.g. ``'1.0.0rc1'``. This is based
    off of :pep:`440`.

Application
-----------

.. autoclass:: Baguette()
    :exclude-members: handle_static_file

Configuration
-------------

.. autoclass:: Config()

View
----

.. autoclass:: View()
    :exclude-members: METHODS

Request
-------

.. autoclass:: Request()

Responses
---------

Base Response
*************

.. autoclass:: Response()
    :exclude-members: CHARSET


Plain Text Response
*******************

.. autoclass:: PlainTextResponse()
    :inherited-members:
    :exclude-members: CHARSET

HTML Response
*************

.. autoclass:: HTMLResponse()
    :inherited-members:
    :exclude-members: CHARSET

JSON Response
*************

.. autoclass:: JSONResponse()
    :inherited-members:
    :exclude-members: CHARSET, JSON_ENCODER

Empty Response
**************

.. autoclass:: EmptyResponse()
    :inherited-members:
    :exclude-members: CHARSET

Redirect Response
*****************

.. autoclass:: RedirectResponse()
    :inherited-members:
    :exclude-members: CHARSET

There's an alias to create this class, it's the :func:`redirect` function.

.. autofunction:: redirect()

File Response
**************

.. autoclass:: FileResponse()
    :inherited-members:
    :exclude-members: CHARSET, body, raw_body

Make Response
*************

.. autofunction:: make_response()

.. autofunction:: make_error_response()

Headers
-------

Headers class
*************

.. autoclass:: Headers()

Make Headers
************

.. autofunction:: make_headers()

Forms
-----

Form parsers
************

.. autoclass:: baguette.forms.Form()

.. autoclass:: baguette.forms.URLEncodedForm()

.. autoclass:: baguette.forms.MultipartForm()

Fields
******

.. autoclass:: baguette.forms.Field()

.. autoclass:: baguette.forms.FileField()

Rendering
---------

Renderer
********

.. autoclass:: baguette.rendering.Renderer()

Render
******

.. autofunction:: baguette.rendering.init()

.. autofunction:: render()

Routing
-------

Router
******

.. autoclass:: baguette.router.Router()

Route
*****

.. autoclass:: baguette.router.Route()
    :exclude-members: PARAM_ARGS_REGEX, PARAM_CONVERTERS, PARAM_REGEX

Path parameters converters
**************************

.. autoclass:: baguette.converters.StringConverter()
    :exclude-members: REGEX
    :inherited-members:

.. autoclass:: baguette.converters.PathConverter()
    :exclude-members: REGEX
    :inherited-members:

.. autoclass:: baguette.converters.IntegerConverter()
    :exclude-members: REGEX
    :inherited-members:

.. autoclass:: baguette.converters.FloatConverter()
    :exclude-members: REGEX
    :inherited-members:


HTTP Exceptions
---------------

.. automodule:: baguette.httpexceptions

.. currentmodule:: baguette

Websocket
---------

.. autoclass:: Websocket()

Middlewares
-----------

Base middleware
***************

.. autoclass:: Middleware()
    :special-members: __call__

Included middlewares
********************

.. automodule:: baguette.middlewares

.. currentmodule:: baguette

Testing
-------

.. autoclass:: TestClient()
    :exclude-members: DEFAULT_SCOPE

Utils
-----

.. automodule:: baguette.utils
