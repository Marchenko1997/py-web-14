# Configuration file for the Sphinx documentation builder.

import sys
import os

sys.path.append(os.path.abspath(".."))

project = "Сontacts API"
copyright = "2025, Marchenko Galina"
author = "Marchenko Galina"

# General configuration
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.autosummary",
]

autosummary_generate = True

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# HTML output
html_theme = "nature"
html_static_path = ["_static"]
