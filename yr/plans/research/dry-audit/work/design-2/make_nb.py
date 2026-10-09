import nbformat as nbf
c, m = nbf.v4.new_code_cell, nbf.v4.new_markdown_cell
cells = [
 c("import yr_review"),
 c("%answer early"),          # answer before its question: friendly message
 m("### Q1"), c("%%question 1\nx = 8\ny = 2\nprint(x + y, x * y)\nprint(x / y)\nx ** y"),
 m("### Q8a"), c("%%question 8a\nx = 5\nif x = 5:\n    print('five')"),
 m("### Q8b"), c("%%question 8b\nprint('start')\nprint(total)\nprint('end')"),
 m("### Q9"), c("%%question 9\ndef greet():\n    print('Hello')\n\ngreet"),
 m("### Q14 doctest"), c('''%%question 14
from doctest import run_docstring_examples

def run_doctests(func):
    run_docstring_examples(func, globals(), name=func.__name__)

def count_e(word):
    """Count e's.

    >>> count_e('Eerie')
    3
    >>> count_e('bee')
    2
    """
    count = 0
    for letter in word:
        if letter == 'e':
            count += 1
    return count

run_doctests(count_e)'''),
 m("### Q17 turtle"), c("%%question 17\nfrom jupyturtle import make_turtle, forward, left\nmake_turtle(delay=0)\nforward(50)\nleft(90)\nforward(30)"),
 m("#### Answers"),
 c("%answer 1"), c("%answer 8a"), c("%answer 8b"), c("%answer 9"), c("%answer 14"),
 m("fix, R3 style: only the changed function; run_doctests comes from the question"),
 c("def count_e(word):\n    \"\"\"Count e's.\n\n    >>> count_e('Eerie')\n    3\n    \"\"\"\n    return word.lower().count('e')\n\nrun_doctests(count_e)"),
 c("%answer 17"),
 c("%answer nosuch"),
 c("print('reached the end')"),
]
nb = nbf.v4.new_notebook(cells=cells)
nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
nbf.write(nb, "proto.ipynb")
