import nbformat as nbf
from nbclient import NotebookClient
src = nbf.read('new/chap07_review.ipynb', as_version=4)
dt = [c for c in src.cells if c.cell_type=='code' and 'run_docstring_examples' in c.source][0].source
body = dt.split("r'''\n",1)[1].rsplit("\n''')",1)[0]
nb = nbf.v4.new_notebook()
nb.cells = [nbf.v4.new_code_cell('import sys\nCODE = ' + repr(body)),
            nbf.v4.new_code_cell('_ = get_ipython().run_cell(CODE)'),
            nbf.v4.new_code_cell('_ = get_ipython().run_cell(CODE.replace("name=func.__name__", "name=func.__name__, verbose=True"))'),
            nbf.v4.new_code_cell('_ = get_ipython().run_cell(CODE.replace("globals()", "get_ipython().user_ns"))'),
            nbf.v4.new_code_cell('_ = get_ipython().run_cell("print(count_e(\'Eerie\'), count_e.__module__, count_e.__globals__ is globals())")'),
            ]
NotebookClient(nb, kernel_name='python3', allow_errors=True).execute()
for i, c in enumerate(nb.cells):
    print('--- cell', i, [(o.output_type, o.get('name'), (o.get('text') or str(o.get('data', ''))[:600])) for o in c.outputs])
