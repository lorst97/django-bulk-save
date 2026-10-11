"""Sphinx configuration; documentation builds without Django setup."""

from pathlib import Path
import tomllib


metadata = tomllib.loads((Path(__file__).parents[1] / "pyproject.toml").read_text())
project = metadata["project"]["name"]
release = metadata["project"]["version"]
extensions = []
exclude_patterns = ["_build"]
html_theme = "alabaster"
