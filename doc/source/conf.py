# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
import sys

import kloch
from pathlib import Path

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "kloch"
copyright = "2024, Knots Animation"
author = "Knots Animation"
version = kloch.__version__
release = version

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

sys.path.append(str(Path("_extensions").resolve()))

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.autosectionlabel",
    "sphinx_exec_code",
    "sphinx_copybutton",
    "execinject",
]

templates_path = ["_templates"]
exclude_patterns = []

autosectionlabel_prefix_document = True

suppress_warnings = [
    "autosectionlabel",
]

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"
html_static_path = ["_static"]
html_css_files = [
    "extra.css",
]

html_logo = "_static/logo-color.svg"

html_theme_options = {
    "light_css_variables": {
        "color-highlight-on-target": "#D1DBFF",
        "color-sidebar-item-background--hover": "#002bc5",
        "font-stack--headings": "Dosis, var(--font-stack)",
    },
    "dark_css_variables": {
        "color-brand-primary": "#3953FF",
        "color-brand-content": "#3953FF",
        "color-brand-visited": "#6D92C5",
        "color-highlight-on-target": "#002bc5",
        "color-sidebar-item-background--hover": "#002bc5",
        "color-background-primary": "linear-gradient(90deg, rgba(0,0,0,1) 0%, rgba(28,27,30,1) 50%)",
        "color-sidebar-background": "transparent",
        "color-toc-background": "transparent",
        "color-sidebar-search-background": "#090909",
        "font-stack--headings": "Dosis, var(--font-stack)",
    },
    "footer_icons": [
        {
            "name": "GitHub",
            "url": "https://github.com/knotsanimation/kloch",
            "html": """
                <svg stroke="currentColor" fill="currentColor" stroke-width="0" viewBox="0 0 16 16">
                    <path fill-rule="evenodd" d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0 0 16 8c0-4.42-3.58-8-8-8z"></path>
                </svg>
            """,
            "class": "",
        },
    ],
}
