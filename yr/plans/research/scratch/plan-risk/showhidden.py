import re, shutil, sys, tempfile
import nbformat as nbf
from nbclient import NotebookClient
nb = nbf.read(sys.argv[1], nbf.NO_CONVERT)
tmp = tempfile.mkdtemp(); shutil.copy('/root/.venvs/yrThinkPython/yr-cache/jupyturtle.py', tmp)
NotebookClient(nb, timeout=120, kernel_name='python3', allow_errors=True, resources={'metadata': {'path': tmp}}).execute()
for c in nb.cells:
    if c.cell_type == 'code' and c.source.startswith('run_hidden'):
        h = c.outputs[0]['data']['text/html']
        print("svg count", h.count("<svg")); h = re.sub(r'<svg.*?</svg>', '<svg …/>', h, flags=re.S)
        print(len(c.outputs), 'outputs; html =', h[:900]); print()
