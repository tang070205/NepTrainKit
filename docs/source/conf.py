# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
from recommonmark.parser import CommonMarkParser

project = 'NepTrainKit'
copyright = '2024, ChengBing Chen'
author = 'ChengBing Chen'
release = '1.4.9'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.mathjax',
    'recommonmark',
]

templates_path = ['_templates']
exclude_patterns = [  'recommonmark']
locale_dirs = ['docs/locales']  # 语言文件目录
language = 'zh_CN'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
source_parsers = {
    '.md': CommonMarkParser,
}

source_suffix = ['.rst', '.md']