"""Sphinx configuration; documentation builds without Django setup."""

from pathlib import Path
import re
import tomllib


metadata = tomllib.loads((Path(__file__).parents[1] / "pyproject.toml").read_text())
project = metadata["project"]["name"]
release = metadata["project"]["version"]
extensions = []
exclude_patterns = ["_build"]
html_theme = "alabaster"


def prepare_sphinx_source(app, docname, source):
    """Keep checked-in RST portable while enabling Sphinx navigation."""
    source[0] = re.sub(
        r"`([^`]+) <([a-z]+)\.rst>`_",
        r":doc:`\1 <\2>`",
        source[0],
    )
    if docname == "index":
        source[0] += (
            "\n\n.. toctree::\n   :hidden:\n   :maxdepth: 2\n\n"
            "   installation\n   usage\n   api\n"
        )


def setup(app):
    app.connect("source-read", prepare_sphinx_source)
