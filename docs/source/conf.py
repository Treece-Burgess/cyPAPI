import subprocess
import sys

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'cyPAPI Programming Guide'
copyright = '2025, The PAPI Team'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

subprocess.check_call([sys.executable, "-m", "pip", "install", "sphinx_copybutton"])

extensions = ['sphinx_copybutton', 'sphinx_search.extension', 'sphinx.ext.githubpages']

templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

subprocess.check_call([sys.executable, "-m", "pip", "install", "furo"])
#html_theme = 'sphinx_rtd_theme'
html_theme = 'furo'
#html_static_path = ['_static']



# Strip the dollar prompt when copying code
# https://sphinx-copybutton.readthedocs.io/en/latest/use.html#strip-and-configure-input-prompts-for-code-cells
copybutton_prompt_text = "$ "
# https://sphinx-copybutton.readthedocs.io/en/latest/use.html#honor-line-continuation-characters-when-copying-multline-snippets
copybutton_line_continuation_character = "\\"
