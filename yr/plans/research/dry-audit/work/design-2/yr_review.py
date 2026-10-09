"""Prototype: question code stored once in a %%question cell, run by %answer in the Answer."""
from IPython.core.magic import register_cell_magic, register_line_magic
from IPython import get_ipython

QUESTIONS = {}

@register_cell_magic
def question(line, cell):
    """Store this cell's code under the label on the %%question line; run nothing, show nothing."""
    QUESTIONS[line.strip()] = cell

@register_line_magic
def answer(line):
    """Run the code stored by %%question LABEL, exactly as if it were typed in this cell."""
    label = line.strip()
    if label not in QUESTIONS:
        print(f"Run the cell that starts with %%question {label} first (or use Runtime > Run all).")
        return
    get_ipython().run_cell(QUESTIONS[label])
