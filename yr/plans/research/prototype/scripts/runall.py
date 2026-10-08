"""Simulate "Run all": execute NB with nbclient allow_errors=False (stops at the first cell whose
execute_reply status is 'error'; NOTE nbclient, unlike Colab, also lets cells tagged raises-exception
through, so --strip-tags removes that tag first) and report every output and whether it is visible
(not inside a collapsed heading section)."""
import re, shutil, sys, tempfile, json
from pathlib import Path
import nbformat as nbf
from nbclient import NotebookClient
from nbclient.exceptions import CellExecutionError

src, dst = Path(sys.argv[1]), Path(sys.argv[2])
nb = nbf.read(src, as_version=4)
if '--strip-tags' in sys.argv:
    for c in nb.cells:
        if 'raises-exception' in c.metadata.get('tags', []):
            c.metadata.tags.remove('raises-exception')
tmp = Path(tempfile.mkdtemp())
shutil.copy('/root/.venvs/yrThinkPython/yr-cache/jupyturtle.py', tmp)
client = NotebookClient(nb, timeout=300, kernel_name='python3', allow_errors=False,
                        resources={'metadata': {'path': str(tmp)}})
try:
    client.execute()
    print('RUN ALL: reached the end of the notebook')
except CellExecutionError as e:
    idx = next((i for i, c in enumerate(nb.cells) if any(o.output_type == 'error' for o in c.get('outputs', []))), None)
    print(f'RUN ALL: STOPPED at cell {idx}: {str(e).strip().splitlines()[-1][:120]}')
nbf.write(nb, dst)

# visibility: a cell is hidden if it follows a collapsed heading (level L) before the next heading of level <= L
hidden_by, collapsed_ids = None, set(nb.metadata.get('colab', {}).get('collapsed_sections', []))
where, question = None, ''
counts = {'visible': 0, 'hidden': 0}
for i, c in enumerate(nb.cells):
    if c.cell_type == 'markdown':
        m = re.match(r'\s*(#{1,6}) (.*)', c.source)
        if m:
            level = len(m.group(1))
            if hidden_by and level <= hidden_by[0]:
                hidden_by = None
            if m.group(2).startswith('Question'):
                question = m.group(2).split(':')[0]
            jp = c.metadata.get('jp-MarkdownHeadingCollapsed', False)
            colab = c.get('id') in collapsed_ids or c.metadata.get('id') in collapsed_ids
            if (jp or colab) and not hidden_by:
                hidden_by = (level, i, jp, colab)
        continue
    outs = c.get('outputs', [])
    if not outs:
        continue
    vis = 'HIDDEN (in collapsed %s Answer)' % question if hidden_by else 'VISIBLE'
    counts['hidden' if hidden_by else 'visible'] += 1
    kinds = []
    for o in outs:
        if o.output_type == 'stream':
            kinds.append(f'{o.name}: {o.text.strip().splitlines()[0][:40]!r}...' if o.text.strip() else o.name)
        elif o.output_type == 'error':
            kinds.append(f'error {o.ename}: {o.evalue[:50]}')
        else:
            kinds.append(o.output_type + ' ' + ','.join(o.get('data', {}).keys()))
    print(f'cell {i:2} [{question or "intro"}] {vis}: ' + ' | '.join(kinds))
print('cells with output:', counts)
