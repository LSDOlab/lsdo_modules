"""Create a notebook containing code from a script.
Run as:  python py2nb.py my_script.py
"""
import sys

import nbformat
from nbformat.v4 import new_notebook, new_code_cell, new_markdown_cell

nb = new_notebook()
with open(sys.argv[1]) as f:
    code = f.read()

ex_name = sys.argv[1][3:-3]
nb.cells.append(new_markdown_cell('# '+ ex_name))
nb.cells.append(new_code_cell(code))
nbformat.write(nb, sys.argv[1][:-3]+'.ipynb')