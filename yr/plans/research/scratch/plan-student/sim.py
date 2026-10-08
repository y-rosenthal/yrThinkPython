import sys, re, shutil, tempfile
import nbformat as nbf
from nbclient import NotebookClient
nb = nbf.read(sys.argv[1], 4)
tmp = tempfile.mkdtemp(); shutil.copy('/root/.venvs/yrThinkPython/yr-cache/jupyturtle.py', tmp)
st = {}
NotebookClient(nb, timeout=300, kernel_name='python3', allow_errors=True, resources={'metadata': {'path': tmp}},
               on_cell_executed=lambda cell, cell_index, execute_reply: st.__setitem__(cell_index, execute_reply['content']['status'])).execute()
hidden = False; lvl = None
for i, c in enumerate(nb.cells):
    if c.cell_type == 'markdown':
        m = re.match(r'\s*(#{1,6}) ', c.source)
        if m:
            n = len(m.group(1))
            if hidden and n <= lvl: hidden = False
            if c.metadata.get('jp-MarkdownHeadingCollapsed'): hidden, lvl = True, n
        continue
    kinds = [o.output_type + (':' + o.name if o.output_type == 'stream' else '') for o in c.outputs]
    print(f'cell {i:2} status={st.get(i)} {"HIDDEN " if hidden else "VISIBLE"} {kinds} {c.source.splitlines()[0][:45]!r}')
