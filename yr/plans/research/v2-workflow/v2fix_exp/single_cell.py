"""Press play on ONE run cell in a fresh kernel, before the setup cell (reviewer 3's scenario)."""
import json, os, re, sys
sys.path.insert(0, sys.argv[1] + '/scripts')
os.environ['JUPYTER_PATH'] = sys.argv[1] + '/kernels'
import nbformat as nbf
from nbclient import NotebookClient
from review_v2 import canon_outputs, normalize_outputs, parse_page
nb = nbf.read(sys.argv[1] + '/out/chap05_review.ipynb', as_version=4)
for q in parse_page(nb):
    for ri in q['run_cells']:
        c = nb.cells[ri]
        one = nbf.v4.new_notebook(cells=[nbf.v4.new_code_cell(c.source)])
        NotebookClient(one, kernel_name='colablike', allow_errors=True, timeout=60).execute(env={**os.environ, 'TMPDIR': '/tmp'})
        out = normalize_outputs(one.cells[0].outputs, c.outputs)
        same = canon_outputs(out) == canon_outputs(c.outputs)
        e = [o for o in out if o['output_type'] == 'error']
        shown = re.sub(r'\x1b\[[0-9;]*m', '', '\n'.join(e[0]['traceback'])) if e else ''
        print(f"{q['title'][:12]:12} {c.id}: {'same as stored' if same else 'DIFFERENT: ' + (e[0]['ename'] + ': ' + e[0]['evalue'] if e else str(out)[:80])}"
              + (f"  | traceback shows title/wrapper: {'@title' in shown or 'run_cell' in shown}" if e and not same else ''))
