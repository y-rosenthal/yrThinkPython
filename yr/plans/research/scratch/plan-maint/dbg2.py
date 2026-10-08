import nbformat as nbf
from nbclient import NotebookClient
code = '''from doctest import run_docstring_examples
def count_e(word):
    """Count.

    >>> count_e('Eerie')
    3
    """
    return 2
run_docstring_examples(count_e, globals(), verbose=True, name='count_e')
'''
nb = nbf.v4.new_notebook()
nb.cells = [nbf.v4.new_code_cell('import sys\nCODE = ' + repr(code)),
            nbf.v4.new_code_cell('get_ipython().run_cell(CODE)'),
            nbf.v4.new_code_cell('get_ipython().run_cell(CODE); print("after", file=sys.stderr)'),
            nbf.v4.new_code_cell('r = get_ipython().run_cell(CODE)\nprint(type(sys.stdout), file=sys.stderr)'),
            nbf.v4.new_code_cell('exec(CODE, globals())'),
            ]
NotebookClient(nb, kernel_name='python3', allow_errors=True).execute()
for i, c in enumerate(nb.cells):
    print('--- cell', i, [(o.output_type, o.get('name'), (o.get('text') or str(o.get('data', ''))[:400])) for o in c.outputs])
