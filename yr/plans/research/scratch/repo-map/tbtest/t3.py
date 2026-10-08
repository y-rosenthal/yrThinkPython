import nbformat as nbf, json
from nbclient import NotebookClient
src = json.load(open('/home/user/yrThinkPython/yr/chap07_review.ipynb'))['cells'][46]['source']
q = ''.join(src)
cells = ['def run_code(code):\n    exec(code, globals())',
         'q14 = ' + repr(q),
         'run_code(q14)',
         q]
nb = nbf.v4.new_notebook(cells=[nbf.v4.new_code_cell(c) for c in cells])
NotebookClient(nb, timeout=60, kernel_name='python3', allow_errors=True).execute()
for i in (2, 3):
    print('--- cell', i, 'exec' if i == 2 else 'plain cell')
    for o in nb.cells[i].outputs:
        print(o.get('text', o.get('evalue')))
