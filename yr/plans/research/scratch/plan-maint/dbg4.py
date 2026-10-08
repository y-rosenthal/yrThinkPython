import nbformat as nbf
from nbclient import NotebookClient
src = nbf.read('new/chap07_review.ipynb', as_version=4)
dt = [c for c in src.cells if c.cell_type=='code' and 'run_docstring_examples' in c.source][0].source
body = dt.split("r'''\n",1)[1].rsplit("\n''')",1)[0]
nb = nbf.v4.new_notebook()
nb.cells = [nbf.v4.new_code_cell('import sys\nCODE = ' + repr(body)),
            nbf.v4.new_code_cell('_ = get_ipython().run_cell("\\n" + CODE + "\\n")'),
            nbf.v4.new_code_cell('_ = get_ipython().run_cell("\\n" + CODE)'),
            nbf.v4.new_code_cell('_ = get_ipython().run_cell(CODE + "\\n")'),
            nbf.v4.new_code_cell('print(repr(get_ipython().transform_cell("\\n" + CODE + "\\n")[:80]))'),
            nbf.v4.new_code_cell('_ = get_ipython().run_cell("\\nprint(1)\\n")'),
            ]
NotebookClient(nb, kernel_name='python3', allow_errors=True).execute()
for i, c in enumerate(nb.cells):
    print('--- cell', i, [(o.output_type, o.get('name'), (o.get('text') or str(o.get('data', ''))[:300])) for o in c.outputs])
