import nbformat as nbf
from nbclient import NotebookClient
src = nbf.read('new/chap07_review.ipynb', as_version=4)
dt = [c for c in src.cells if c.cell_type=='code' and 'run_docstring_examples' in c.source][0].source
body = dt.split("r'''\n",1)[1].rsplit("\n''')",1)[0]
nb = nbf.v4.new_notebook()
nb.cells = [nbf.v4.new_code_cell('import difflib\nCODE = ' + repr(body)),
            nbf.v4.new_code_cell("x = r'''\n" + body + "\n'''\nprint('\\n'.join(difflib.unified_diff(('\\n'+CODE+'\\n').split('\\n'), x.split('\\n'), lineterm=''))) "),
            nbf.v4.new_code_cell("print(repr(get_ipython().transform_cell(" + repr(dt) + ")))"),
            ]
NotebookClient(nb, kernel_name='python3', allow_errors=True).execute()
for i, c in enumerate(nb.cells):
    for o in c.outputs: print('--- cell', i, o.get('text') or o.get('evalue'))
