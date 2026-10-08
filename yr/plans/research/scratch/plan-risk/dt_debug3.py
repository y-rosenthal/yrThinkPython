import nbformat as nbf
from nbclient import NotebookClient
body = 'def f():\n    """Doc.\n\n    >>> f()\n    3\n    """\n'
cells = ["import IPython\nip = get_ipython()\nprint([t.__name__ if hasattr(t,'__name__') else type(t).__name__ for t in ip.input_transformer_manager.cleanup_transforms + ip.input_transformer_manager.line_transforms])",
         "print(repr(get_ipython().transform_cell(" + repr(body) + ")))",
         "print(repr(get_ipython().transform_cell(" + repr('\n' + body) + ")))",
         "x = " + repr(body) + "\nprint(repr(get_ipython().transform_cell(x)))"]
nb = nbf.v4.new_notebook(cells=[nbf.v4.new_code_cell(c) for c in cells])
NotebookClient(nb, kernel_name='python3', allow_errors=True).execute()
for c in nb.cells:
    print('----'); [print(o.get('text', o.get('evalue'))) for o in c.outputs]
