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

- Websockets, see :ref:`websocket`: :class:`Websocket`,
  :mod:`baguette.websocketexceptions`, :class:`WebsocketRouter` and
  :class:`WebsocketRoute`.

Version 0.3.1 (2021-05-23)
--------------------------

Added
*****

- JSON encoders in `baguette.json`, using
  `ujson <https://github.com/ultrajson/ultrajson>`_.
- Setters in :class:`Request`, mainly for setting the body of a request in
  middlewares or while testing.
- Properties in :class:`Response`, mainly for setting the body of a response in
  middlewares or while testing.
- :meth:`Form.copy`.

Version 0.3.0 (2021-05-21)
--------------------------

Added
*****

- Middlewares: see :ref:`middlewares`. ``middlewares`` keyword argument in
  :class:`Baguette`, :meth:`Baguette.middleware` decorator,
  :meth:`Baguette.build_middlewares`, :meth:`Baguette.add_middleware` and
  :meth:`Baguette.remove_middleware`.
- Default middlewares: :class:`DefaultHeadersMiddleware` and
  :class:`ErrorMiddleware`.
- :class:`Config` and :attr:`Baguette.config`.
- Customizable JSON encoder for JSON responses:
  :attr:`JSONResponse.JSON_ENCODER`.

Version 0.2.1 (2021-05-15)
--------------------------

Added
*****

- Accept bytes as handler return value.
- :attr:`Form.files`.
- :attr:`PathConverter.allow_empty`.

Version 0.2.0 (2021-05-09)
--------------------------

Added
*****

- HTML templates rendering: :func:`render`, ``templates_directory`` keyword
  argument in :class:`Baguette`.
- Redirects: :class:`RedirectResponse` and :func:`redirect`

Version 0.1.6 (2021-05-05)
--------------------------

Fixed
*****

- Bug in :meth:`Request.form` when ``include_querystring`` was ``True``.

Version 0.1.5 (2021-05-01)
--------------------------

Added
*****

- :meth:`request.form`, with support for ``application/x-www-form-urlencoded``
  and ``multipart/form-data`` form content types.
- Support for strings in :func:`make_headers`.

Version 0.1.4 (2021-04-29)
--------------------------

Added
*****

- Add static file serving.
- Add ``static_url_path`` and ``static_directory`` keyword arguments to
  :class:`Baguette`.
- :class:`FileResponse`, credits to
  `Quart's implementation <https://gitlab.com/pgjones/quart>`__.
- :func:`make_error_response`.

Changed
*******

- Errors in routes are handled and the traceback is sent back along with the 500
  status code when :attr:`Baguette.debug` is ``True``.

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
