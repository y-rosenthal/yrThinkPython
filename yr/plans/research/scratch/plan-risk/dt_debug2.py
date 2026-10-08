import nbformat as nbf
from nbclient import NotebookClient
body = '''
def count_e(word):
    """Count.

    >>> count_e('Eerie')
    3
    """
    return word.count('e')
print(repr(count_e.__doc__))
'''
cells = ['def run_code(code):\n    get_ipython().run_cell(code, store_history=False)', body, "run_code(r'''" + body + "''')",
         "print(repr(get_ipython().transform_cell(" + repr(body) + ")))"]
nb = nbf.v4.new_notebook(cells=[nbf.v4.new_code_cell(c) for c in cells])
NotebookClient(nb, kernel_name='python3', allow_errors=True).execute()
for c in nb.cells[1:]:
    print('----'); [print(o.get('text', o.get('evalue'))) for o in c.outputs]
