import typing

import jinja2

from .types import FilePath

_renderer = None


class Renderer:
    def __init__(
        self,
        templates_directory: typing.Union[
            FilePath, typing.List[FilePath]
        ] = "templates",
    ):
        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(templates_directory),
            enable_async=True,
        )

    async def render(self, template_name, *args, **kwargs):
        template: jinja2.Template = self.env.get_template(template_name)
        return await template.render_async(*args, **kwargs)


def init(
    templates_directory: typing.Union[
        FilePath, typing.List[FilePath]
    ] = "templates"
):
    global _renderer
    _renderer = Renderer(templates_directory)
    return _renderer


async def render(template_name, *args, **kwargs):
    if _renderer is None:
        init(kwargs.pop("templates_directory", "templates"))

    return await _renderer.render(template_name, *args, **kwargs)
