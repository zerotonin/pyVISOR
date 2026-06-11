"""Sphinx configuration for pyVISOR documentation."""

import sys
from pathlib import Path

# Make the package importable for autodoc without a full install.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

project = "GameThogram"
author = "Bart Geurten, Ilyas Kuhlemann"
release = "0.1.0"
version = release

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
]

# Mock heavy / GUI runtime imports so docs build on cheap CI runners
# without installing the full dependency stack.
autodoc_mock_imports = [
    "PyQt5",
    "pygame",
    "av",
    "pims",
    "matplotlib",
    "numpy",
    "pandas",
    "scipy",
    "PIL",
    "dill",
    "xlsxwriter",
    "appdirs",
    "imageio",
]

# Napoleon settings for Google/NumPy style docstrings
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True

templates_path = ["_templates"]
exclude_patterns = ["_build"]

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
html_logo = "_static/gamethogram_128.png"
html_favicon = "_static/gamethogram_128.png"
html_theme_options = {
    "logo_only": False,
    "display_version": True,
}

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
    "pandas": ("https://pandas.pydata.org/docs/", None),
}
