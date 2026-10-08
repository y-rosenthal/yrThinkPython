import sys, shutil, tempfile
from pathlib import Path
import nbformat as nbf
from nbclient import NotebookClient
nb = nbf.read(sys.argv[1], as_version=4)
tmp = Path(tempfile.mkdtemp()); shutil.copy('/root/.venvs/yrThinkPython/yr-cache/jupyturtle.py', tmp)
NotebookClient(nb, timeout=600, kernel_name='python3', allow_errors=True, resources={'metadata': {'path': str(tmp)}}).execute()
nbf.write(nb, sys.argv[2])
