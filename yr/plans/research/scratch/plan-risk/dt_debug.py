import nbformat as nbf
from nbclient import NotebookClient
body = '''
import doctest, sys
def count_e(word):
    """Count.

    >>> count_e('Eerie')
    3
    """
    return word.count('e')
tests = doctest.DocTestFinder(recurse=False).find(count_e, 'count_e', globs=globals())
print('found', [(t.name, len(t.examples), t.filename, t.lineno) for t in tests], file=sys.__stdout__)
print('found', [(t.name, len(t.examples), t.filename, t.lineno) for t in tests])
doctest.run_docstring_examples(count_e, globals(), name='count_e')
print('after')
'''
cells = ['def run_code(code):\n    get_ipython().run_cell(code, store_history=False)', body, "run_code(r'''" + body + "''')"]
nb = nbf.v4.new_notebook(cells=[nbf.v4.new_code_cell(c) for c in cells])
NotebookClient(nb, kernel_name='python3', allow_errors=True).execute()
for c in nb.cells[1:]:
    print('----'); [print(o.get('text', o.get('evalue'))) for o in c.outputs]
