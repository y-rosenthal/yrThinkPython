import nbformat as nbf, sys
from nbclient import NotebookClient
src = nbf.read('new/chap07_review.ipynb', as_version=4)
setup = [c for c in src.cells if 'setup' in c.metadata.get('tags', [])][0].source
dt = [c for c in src.cells if c.cell_type=='code' and 'run_docstring_examples' in c.source][0].source
body = dt.split("r'''\n",1)[1].rsplit("\n''')",1)[0]
nb = nbf.v4.new_notebook()
nb.cells = [nbf.v4.new_code_cell('import sys\n'+setup.split('def run_code',1)[0][:0] + 'def run_code(code):\n    r = get_ipython().run_cell(code)\n    print("success", r.success, "err", repr(r.error_in_exec), file=sys.stderr)'),
            nbf.v4.new_code_cell(dt),
            nbf.v4.new_code_cell(body),
            nbf.v4.new_code_cell("run_code('import doctest\\nprint(doctest.DocTestFinder().find(count_e))')"),
            nbf.v4.new_code_cell("import doctest\nprint(doctest.DocTestFinder().find(count_e))")]
NotebookClient(nb, kernel_name='python3', allow_errors=True).execute()
for i, c in enumerate(nb.cells):
    print('--- cell', i, [ (o.output_type, (o.get('text') or str(o.get('data',''))[:300] or o.get('evalue'))) for o in c.outputs])
