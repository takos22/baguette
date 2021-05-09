import pytest

from baguette import rendering
from baguette.rendering import Renderer, init, render

expected_html = """\
<!DOCTYPE html>
<html lang="en">
    <head>
        <link rel="stylesheet" href="/static/css/style.css" />
        <title>Index - My Webpage</title>
        <style type="text/css">
            .important {
                color: #336699;
            }
        </style>
    </head>
    <body>
        <div id="content">
            <h1>Index</h1>
            <p class="important">Welcome to my awesome homepage.</p>
            <p>1st paragraph</p>
            <p>2nd paragraph</p>
        </div>
        <div id="footer">
            &copy; Copyright 2021 by <a href="https://example.com/">me</a>.
        </div>
    </body>
</html>"""


def strip(text: str) -> str:
    return text.replace(" ", "").replace("\n", "")


@pytest.mark.asyncio
async def test_renderer():
    renderer = Renderer("tests/templates")
    html = await renderer.render(
        "index.html",
        paragraphs=["1st paragraph", "2nd paragraph"],
    )
    assert strip(html) == strip(expected_html)


def test_init():
    renderer = init("tests/templates")
    assert isinstance(renderer, Renderer)
    assert rendering._renderer == renderer


@pytest.mark.asyncio
async def test_render():
    rendering._renderer = None
    html = await render(
        "index.html",
        paragraphs=["1st paragraph", "2nd paragraph"],
        templates_directory="tests/templates",
    )
    assert strip(html) == strip(expected_html)
