import sys, re, nbformat as nbf, json
from nbclient import NotebookClient
from nbclient.exceptions import CellExecutionError
path = sys.argv[1]
nb = nbf.read(path, nbf.NO_CONVERT)
print(path, 'colab meta:', json.dumps(nb.metadata.get('colab', {}))[:120])
heads = [c for c in nb.cells if c.cell_type == 'markdown' and re.match(r'\s*#### Answer\s*$', c.source)]
ok_meta = all(c.metadata.get('jp-MarkdownHeadingCollapsed') is True and c.metadata.get('id') == c.id for c in heads)
cs = set(nb.metadata.get('colab', {}).get('collapsed_sections', []))
print(' answers', len(heads), 'jp+metadata.id ok', ok_meta, 'all in collapsed_sections', all(c.id in cs for c in heads))
c = NotebookClient(nb, timeout=600, kernel_name='python3', allow_errors=False, force_raise_errors=True, resources={'metadata': {'path': '.'}})
try:
    c.execute(); print(' reached end')
except CellExecutionError as e:
    print(' STOPPED', str(e).splitlines()[-1][:120])
# visibility: a cell is hidden if after a '#### Answer' heading and before next heading level<=4
hidden = False; vis = []
for i, cell in enumerate(nb.cells):
    if cell.cell_type == 'markdown':
        m = re.match(r'\s*(#{1,6}) ', cell.source)
        if m and len(m.group(1)) <= 4:
            hidden = bool(re.match(r'\s*#### Answer\s*$', cell.source))
            continue
    if cell.cell_type == 'code' and cell.outputs and not hidden:
        vis.append((i, [o.output_type for o in cell.outputs], cell.source[:40]))
print(' visible outputs:', vis)
