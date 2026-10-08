import re, shutil, sys, tempfile
import nbformat as nbf
from nbclient import NotebookClient
ANSI = re.compile(r'\x1b\[[0-9;]*m')
nb = nbf.read('out/colab_test_runall.ipynb', nbf.NO_CONVERT)
tmp = tempfile.mkdtemp(); shutil.copy('/root/.venvs/yrThinkPython/yr-cache/jupyturtle.py', tmp)
NotebookClient(nb, timeout=120, kernel_name='python3', allow_errors=True, resources={'metadata': {'path': tmp}}).execute()
for i in (44, 51):
    for o in nb.cells[i].outputs:
        if o.output_type == 'error':
            print(f'--- cell {i} ename={o.ename} evalue={ANSI.sub("", o.evalue)!r}'); print(ANSI.sub('', '\n'.join(o.traceback)))
