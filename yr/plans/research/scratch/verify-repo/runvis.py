"""Run like Colab's Run all (stop at first error status, ignore raises-exception tags), then report
which outputs are visible under JupyterLab-style heading-section semantics."""
import re, shutil, sys, tempfile
from pathlib import Path
import nbformat as nbf
from nbclient import NotebookClient
from nbclient.exceptions import CellExecutionError

def heading_level(src):
    lines = src.split('\n'); fence = False; best = None
    for k, l in enumerate(lines):
        if l.lstrip().startswith('```'): fence = not fence; continue
        if fence: continue
        m = re.match(r'\s{0,3}(#{1,6}) ', l)
        lev = len(m.group(1)) if m else None
        if lev is None and k > 0 and lines[k-1].strip() and re.match(r'\s{0,3}(=+|-+)\s*$', l):
            lev = 1 if '=' in l else 2
        if lev and (best is None or lev < best): best = lev
    return best

nb = nbf.read(sys.argv[1], as_version=4)
tmp = Path(tempfile.mkdtemp()); shutil.copy('/root/.venvs/yrThinkPython/yr-cache/jupyturtle.py', tmp)
try:
    NotebookClient(nb, timeout=600, kernel_name='python3', allow_errors=False, force_raise_errors=True,
                   resources={'metadata': {'path': str(tmp)}}).execute()
    status = 'REACHED END'
except CellExecutionError as e:
    status = 'STOPPED: ' + str(e).strip().splitlines()[-1][:100]
ids = set(nb.metadata.get('colab', {}).get('collapsed_sections', []))
stack = []  # collapsed heading levels in effect
vis = hid = 0; visible = []
for i, c in enumerate(nb.cells):
    if c.cell_type == 'markdown':
        lev = heading_level(c.source)
        if lev:
            while stack and lev <= stack[-1]: stack.pop()
            if c.metadata.get('jp-MarkdownHeadingCollapsed') or c.get('id') in ids or c.metadata.get('id') in ids:
                stack.append(lev)
        continue
    if c.get('outputs'):
        if stack: hid += 1
        else:
            vis += 1
            o = c.outputs[0]
            visible.append((i, c.source.splitlines()[0][:40], o.output_type, (o.get('text') or o.get('ename') or '')[:40]))
print(Path(sys.argv[1]).name, status, '| cells with output: visible', vis, 'hidden', hid)
for v in visible: print('   VISIBLE', v)
if len(sys.argv) > 2: nbf.write(nb, sys.argv[2])
