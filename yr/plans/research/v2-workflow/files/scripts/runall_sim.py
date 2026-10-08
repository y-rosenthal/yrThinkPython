"""Simulate Colab's Runtime > Run all on a review page and list what a student sees without clicking.

    python runall_sim.py NB KERNEL [--download] [--save OUT.ipynb]

- before running: every code cell with STORED output, and whether it is inside a collapsed Answer
- Run all: nbclient with allow_errors=False and force_raise_errors=True (stops at the first cell whose
  reply status is "error", like Run all), all cell tags removed first (Colab ignores raises-exception)
- after running: every code cell with output outside a collapsed section (should be only the setup
  cell's 'Downloaded ...' line)
--download runs in an empty folder (the setup cell downloads jupyturtle.py); otherwise jupyturtle.py is
copied in first.
"""
import copy
import os
import shutil
import sys
import tempfile
from pathlib import Path

import nbformat as nbf
from nbclient import NotebookClient
from nbclient.exceptions import CellExecutionError

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from review_v2 import collapsed_sections_hidden, source

os.environ['JUPYTER_PATH'] = str(HERE.parent / 'kernels')


def describe(cell):
    o = cell.outputs[0]
    what = o.get('text') or o.get('ename') or ','.join(o.get('data', {}))
    what = ''.join(what) if isinstance(what, list) else what
    return f'{o.output_type}: {what.strip()[:60]!r}'


def visible_outputs(nb):
    hidden = collapsed_sections_hidden(nb)
    vis = [(i, c) for i, c in enumerate(nb.cells) if c.cell_type == 'code' and c.get('outputs') and i not in hidden]
    n_hidden = sum(1 for i, c in enumerate(nb.cells) if c.cell_type == 'code' and c.get('outputs') and i in hidden)
    return vis, n_hidden


def main(argv):
    path, kernel = argv[0], argv[1]
    nb = nbf.read(path, as_version=4)
    vis, n_hidden = visible_outputs(nb)
    print(f'{Path(path).name} [{kernel}] BEFORE running: {n_hidden} code cells with stored output inside collapsed '
          f'Answers, {len(vis)} outside')
    for i, c in vis:
        print(f'   VISIBLE cell {i} ({c.id}): {describe(c)}')
    run = copy.deepcopy(nb)
    for c in run.cells:
        c.metadata.pop('tags', None)
    n_code = sum(c.cell_type == 'code' for c in run.cells)
    executed = []
    tmp = tempfile.mkdtemp()
    if '--download' not in argv:
        shutil.copy('/root/.venvs/yrThinkPython/yr-cache/jupyturtle.py', tmp)
    client = NotebookClient(run, kernel_name=kernel, timeout=600, allow_errors=False, force_raise_errors=True,
                            record_timing=False, resources={'metadata': {'path': tmp}},
                            on_cell_executed=lambda cell, cell_index, execute_reply: executed.append(
                                (cell_index, execute_reply['content']['status'])))
    try:
        client.execute(env={**os.environ, 'TMPDIR': '/tmp'})
        status = 'REACHED THE END'
    except CellExecutionError as e:
        status = 'STOPPED: ' + str(e).strip().splitlines()[-1][:120]
    shutil.rmtree(tmp, ignore_errors=True)
    errs = [i for i, s in executed if s != 'ok']
    print(f'   Run all: {status}; executed {len(executed)}/{n_code} code cells; reply status not ok: {errs or "none"}')
    vis, n_hidden = visible_outputs(run)
    print(f'   AFTER Run all: {n_hidden} code cells with output inside collapsed Answers, {len(vis)} outside')
    for i, c in vis:
        print(f'   VISIBLE cell {i} ({c.id}, tags {nb.cells[i].metadata.get("tags")}): {describe(c)}')
    if '--save' in argv:
        nbf.write(run, argv[argv.index('--save') + 1])
    ok = status == 'REACHED THE END' and all('setup' in nb.cells[i].metadata.get('tags', []) for i, _ in vis)
    print('   RESULT:', 'PASS' if ok else 'FAIL')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
