import os, sys, re
import nbformat as nbf
from nbclient import NotebookClient
sys.path.insert(0, 'scripts')
from review_v2 import RUN_CODE_CELL
os.environ['JUPYTER_PATH'] = os.path.abspath('kernels')
A = re.compile(r'\x1b\[[0-9;]*m')
cells = [RUN_CODE_CELL,
 "def countdown_by_two(n):\n    if n == 0:\n        print('Blastoff!')\n    else:\n        countdown_by_two(n - 2)",
 'countdown_by_two(5)',
 'run_code(r"""\ncountdown_by_two(5)\n""")',
 'import sys; print(sys.getrecursionlimit())']
nb = nbf.v4.new_notebook(cells=[nbf.v4.new_code_cell(c) for c in cells])
NotebookClient(nb, kernel_name=sys.argv[1], allow_errors=True, timeout=120).execute()
for i in (2, 3):
    tb = nb.cells[i].outputs[0]['traceback']
    print(sys.argv[1], 'cell', i, 'plain' if i == 2 else 'run_code', len(tb), 'items;', [A.sub('', t)[:70] for t in tb if 'skipping' in A.sub('', t) or 'repeated' in A.sub('', t)][:2])
print(nb.cells[4].outputs[0]['text'])
