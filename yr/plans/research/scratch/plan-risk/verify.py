"""Simulate Colab's Run all on the smoke notebooks (stop at first error, ignore tags); print what each cell showed."""
import re, shutil, sys, tempfile, time, queue
import nbformat as nbf
from nbclient import NotebookClient
from nbclient.exceptions import CellExecutionError
ANSI = re.compile(r'\x1b\[[0-9;]*m')
nbpath = sys.argv[1]
nb = nbf.read(nbpath, nbf.NO_CONVERT)
tmp = tempfile.mkdtemp(); shutil.copy('/root/.venvs/yrThinkPython/yr-cache/jupyturtle.py', tmp)
status = {}
def hook(cell, cell_index, execute_reply): status[cell_index] = execute_reply['content']['status']
try:
    NotebookClient(nb, timeout=120, kernel_name='python3', allow_errors=False, force_raise_errors=True,
                   on_cell_executed=hook, resources={'metadata': {'path': tmp}}).execute()
    print('REACHED THE END')
except CellExecutionError as e:
    print('STOPPED:', ANSI.sub('', str(e)).strip().splitlines()[-1][:200])
for i, c in enumerate(nb.cells):
    if c.cell_type != 'code': continue
    kinds = []
    for o in c.outputs:
        if o.output_type == 'stream': kinds.append(f"{o.name}:{ANSI.sub('', o.text).strip().splitlines()[-1][:70]!r}")
        elif o.output_type == 'error': kinds.append(f'error:{o.ename}:{ANSI.sub("", o.evalue)[:60]}')
        else: kinds.append(f"{o.output_type}:{sorted(o.get('data', {}))}")
    print(f'[{i:2}] status={status.get(i)} src={c.source.splitlines()[0][:38]!r} -> {kinds}')
