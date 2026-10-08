import nbformat as nbf
from nbclient import NotebookClient
src = nbf.read('new/chap07_review.ipynb', as_version=4)
dt = [c for c in src.cells if c.cell_type=='code' and 'run_docstring_examples' in c.source][0].source
body = dt.split("r'''\n",1)[1].rsplit("\n''')",1)[0]
nb = nbf.v4.new_notebook()
nb.cells = [nbf.v4.new_code_cell('import sys\nCODE = ' + repr(body) + '\ndef rc(code):\n    get_ipython().run_cell(code)'),
            nbf.v4.new_code_cell('rc(CODE)'),
            nbf.v4.new_code_cell("rc(r'''\n" + body + "\n''')"),
            nbf.v4.new_code_cell("x = r'''\n" + body + "\n'''\n_ = get_ipython().run_cell(x)"),
            nbf.v4.new_code_cell("x = r'''\n" + body + "\n'''\nprint(x == '\\n' + CODE + '\\n')"),
            nbf.v4.new_code_cell("print(repr(In[-1][:200]))"),
            ]
NotebookClient(nb, kernel_name='python3', allow_errors=True).execute()
for i, c in enumerate(nb.cells):
    print('--- cell', i, [(o.output_type, o.get('name'), (o.get('text') or str(o.get('data', ''))[:300])) for o in c.outputs])
