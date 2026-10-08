import nbformat as nbf
from nbclient import NotebookClient
body = 'def f():\n    """Doc.\n\n    >>> f()\n    3\n    """\nprint(repr(f.__doc__))\n'
outer = "run_code(r'''\n" + body + "''')"
cells = ['def run_code(code):\n    get_ipython().run_cell(code, store_history=False)',
         "B = " + repr(body), "run_code(B)", outer,
         "print(repr(get_ipython().transform_cell(" + repr(outer) + ")))",
         "x = r'''\n" + body + "'''\nprint(repr(x))"]
nb = nbf.v4.new_notebook(cells=[nbf.v4.new_code_cell(c) for c in cells])
NotebookClient(nb, kernel_name='python3', allow_errors=True).execute()
for c in nb.cells[2:]:
    print('----', c.source.splitlines()[0][:30]); [print(o.get('text', o.get('evalue'))) for o in c.outputs]
