# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

import os

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import re
import sys
from typing import NamedTuple

VersionInfo = NamedTuple(
    "VersionInfo", major=int, minor=int, micro=int, releaselevel=str, serial=int
)

sys.path.insert(0, os.path.abspath(".."))
sys.path.append(os.path.abspath("extensions"))


# -- Project information -----------------------------------------------------

project = "baguette"
copyright = "2020 - now, takos22"
author = "takos22"

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.

with open("../baguette/__init__.py") as f:
    # getting version info without importing the whole module
    version_info_code = re.search(
        r"^version_info\s*=\s*(VersionInfo\(\s*major=\d+,\s*minor=\d+,\s*"
        r'micro=\d+,\s*releaselevel=[\'"]\w*[\'"],\s*serial=\d+\s*\))',
        f.read(),
        re.MULTILINE,
    ).group(1)

version_info: VersionInfo = eval(
    version_info_code, globals(), {"VersionInfo": VersionInfo}
)
version = "{0.major}.{0.minor}.{0.micro}".format(version_info)


# The full version, including alpha/beta/rc tags
releaselevels = {
    "alpha": "a",
    "beta": "b",
    "releasecandidate": "rc",
}
release = version + (
    releaselevels.get(version_info.releaselevel, version_info.releaselevel)
    + str(version_info.serial)
    if version_info.releaselevel
    else ""
)

branch = "master" if version_info.releaselevel else "v" + version


# -- General configuration ---------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
needs_sphinx = "3.0"

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx_toolbox.more_autodoc",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.coverage",
    "sphinx.ext.extlinks",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",
    "sphinx_inline_tabs",
    "sphinx_copybutton",
    "notfound.extension",
    "hoverxref.extension",
    "sphinx_search.extension",
    "resourcelinks",
    "og_tags",
]

# Links used for cross-referencing stuff in other documentation
intersphinx_mapping = {
    "py": ("https://docs.python.org/3", None),
    "req": ("https://requests.readthedocs.io/en/latest/", None),
}

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# The master toctree document.
master_doc = "index"

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build"]


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_title = "Baguette"
html_theme = "furo"
html_theme_options = {
    "navigation_with_keys": True,
    "light_logo": "small_logo_black.png",
    "dark_logo": "small_logo.png",
    "dark_css_variables": {
        "color-inline-code-background": "#292d2d",
    },
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

resource_links = {
    "discord": "https://discord.gg/PGC3eAznJ6",
    "repo": "https://github.com/takos22/baguette",
    "issues": "https://github.com/takos22/baguette/issues",
    "examples": f"https://github.com/takos22/baguette/tree/{branch}/examples",
    "uvicorn": "https://www.uvicorn.org/",
}

# remove type hints in signatures
autodoc_typehints = "none"

# display TODOs in docs
todo_include_todos = True

# avoid confusion between section references
autosectionlabel_prefix_document = True

# pygments styles
pygments_style = "sphinx"
pygments_dark_style = "monokai"

# autodoc defaults
autodoc_default_options = {
    "members": True,
    "undoc-members": True,
}
autodoc_member_order = "bysource"
autoclass_content = "both"

rtd_lang = os.environ.get("READTHEDOCS_LANGUAGE", "en")
rtd_version = os.environ.get("READTHEDOCS_VERSION", "latest")

if os.environ.get("READTHEDOCS", False):
    notfound_urls_prefix = f"/{rtd_lang}/{rtd_version}/"
else:
    notfound_urls_prefix = "/"

notfound_context = {
    "title": "Page not found",
    "body": (
        "<h1>Page not found</h1>\n\n"
        "<p>Unfortunately we couldn't find the page you were looking for.</p>"
        "<p>Try using the search box or go to the "
        f'<a href="{notfound_urls_prefix}">homepage</a></p>'
    ),
}

hoverxref_project = "baguette"
hoverxref_version = rtd_version
hoverxref_auto_ref = True
hoverxref_domains = ["py"]
hoverxref_roles = [
    "ref",
    "doc",
    "numref",
    "mod",
    "func",
    "data",
    "const",
    "class",
    "meth",
    "attr",
    "exc",
    "obj",
]


github_username = "takos22"
github_repository = "baguette"
hide_none_rtype = True

og_site_name = "Baguette documentation"
og_desc = (
    "The baguette module is a modern, feature-rich, asynchronous web framework "
    "for high-performance Python backends."
)
og_image = (
    "https://baguette.readthedocs.io/"
    f"{rtd_lang}/{rtd_version}/_static/small_logo.png"
)
if not os.environ.get("READTHEDOCS", False):
    og_site_url = f"https://baguette.readthedocs.io/{rtd_lang}/{rtd_version}/"
