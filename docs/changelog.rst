.. currentmodule:: baguette

Changelog
=========

All notable changes to this project will be documented in this file.

The format is based on
`Keep a Changelog <https://keepachangelog.com/en/1.0.0/>`__, and this project
adheres to `Semantic Versioning <https://semver.org/spec/v2.0.0.html>`__.

Version 0.4.0 (unreleased)
--------------------------

Added
*****

- Websockets

Version 0.3.1 (2021-05-23)
--------------------------

Added
*****

- JSON encoders in `baguette.json`.
- Setters in :class:`Request`.
- Properties in :class:`Response`.

Version 0.3.0 (2021-05-21)
--------------------------

Added
*****

- Middlewares.
- :class:`Config`.
- Customizable JSON encoder for JSON responses.

Version 0.2.1(2021-05-15)
--------------------------

Added
*****

- Accept bytes as handler return value.

Version 0.2.0 (2021-05-09)
--------------------------

Added
*****

- HTML templates rendering.

- Redirects.

Version 0.1.6 (2021-05-05)
--------------------------

Fixed
*****

- Bug in ``await request.form(include_querystring=True)``.

Version 0.1.5 (2021-05-01)
--------------------------

Added
*****

- :meth:`request.form`, with support for ``application/x-www-form-urlencoded``
  and ``multipart/form-data`` form content types.

Version 0.1.4 (2021-04-29)
--------------------------

Added
*****

- Add static file serving.
- :class:`FileResponse`

Version 0.1.3 (2021-04-27)
--------------------------

Fixed
*****

- Bug in path converter (`#2 <https://github.com/takos22/baguette/issues/2>`__).

Version 0.1.2 (2021-04-26)
--------------------------

Added
*****

- :meth:`app.run <Baguette.run>` that uses :resource:`uvicorn`.
- Docs.

Version 0.1.1 (2021-04-24)
--------------------------

Fixed
*****

- Error in dynamic routing.

Version 0.1.0 (2021-04-23)
--------------------------

Added
*****

- Dynamic routing, see :ref:`dynamic_routing`.
- Path parameters converters, see :ref:`converters`.
- Implement ASGI lifespan protocol: :meth:`Baguette.startup` and
  :meth:`Baguette.shutdown`.
- Add methods for every HTTP verb on :class:`TestClient`.
- :func:`make_headers` and :func:`make_response`.
- Tests for most of the module.
- Docstrings on most classes and methods.

Changed
*******

- Renamed :mod:`baguette.response` to :mod:`baguette.responses`.

Version 0.0.3 (2021-04-18)
--------------------------

Added
*****

- Keyword arguments to :class:`Baguette`: ``debug``, ``default_headers``,
  ``error_response_type`` and ``error_include_description``.
- :class:`Router` and :class:`Route`.
- :meth:`Baguette.add_route`.
- :mod:`baguette.httpexceptions` so that HTTP errors can be raised with Python
  exceptions.
- :class:`TestClient` for testing a Baguette application.
- Type hinting.
- Docs.

Changed
*******

- ``Baguette.endpoint`` decorator was renamed to :meth:`Baguette.route` because
  it makes more sense with the name of :class:`Router`.

Version 0.0.2 (2021-04-14)
--------------------------

Added
*****

- :class:`Baguette` with basic HTTP request handling.
- :class:`Headers`.
- :class:`Request`.
- Responses: :class:`JSONResponse`, :class:`PlainTextResponse`,
  :class:`HTMLResponse` and :class:`EmptyResponse`.
- Class based endpoints with :class:`View`
- License

Changed
*******

- README

Version 0.0.1 (2021-04-12)
--------------------------

Test release
