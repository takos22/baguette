.. currentmodule:: codingame

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

- :meth:`app.run <Baguette.run>`.

Version 0.1.1 (2021-04-24)
--------------------------

Fixed
*****

- Error in dynamic routing.

Version 0.1.0 (2021-04-23)
--------------------------

.. todo:: Complete this

Version 0.0.3 (2021-04-18)
--------------------------

.. todo:: Complete this

Version 0.0.2 (2021-04-14)
--------------------------

.. todo:: Complete this

Version 0.0.1 (2021-04-12)
--------------------------

Test release
