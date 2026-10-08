"""Plain cell vs run_code(\"\"\"...\"\"\") for the same code: compare outputs (uniform wrapping test)."""
import re, shutil, sys, tempfile
import nbformat as nbf
from nbclient import NotebookClient
ANSI = re.compile(r'\x1b\[[0-9;]*m')
SETUP = open('make_smoke.py').read().split("SETUP = r'''")[1].split("'''")[0]
SNIPS = {
 'ch07q14': open('snip_doctest.txt').read(),
 'ch03q9': "def greet():\n    print('Hello')\n\ngreet",
 'ch02q4': "price = 4\nprice * 2\nprice * 3",
 'ch04q14c': "def polygon(n, length):\n    angle = 360 / n\n    for i in range(n):\n        forward(length)\n        left(angle)\n\nmake_turtle()\npolygon(-4, 20)",
}
cells = [nbf.v4.new_code_cell(SETUP)]
for k, s in SNIPS.items():
    cells.append(nbf.v4.new_code_cell(s))
    q = "'''" if '"""' in s else '"""'
    cells.append(nbf.v4.new_code_cell('run_code(r' + q + '\n' + s + '\n' + q + ')'))
nb = nbf.v4.new_notebook(cells=cells)
tmp = tempfile.mkdtemp(); shutil.copy('/root/.venvs/yrThinkPython/yr-cache/jupyturtle.py', tmp)
NotebookClient(nb, timeout=120, kernel_name='python3', allow_errors=False, resources={'metadata': {'path': tmp}}).execute()
def norm(c):
    out = []
    for o in c.outputs:
        if o.output_type == 'stream': out.append((o.name, ANSI.sub('', o.text)))
        elif o.output_type == 'execute_result': out.append(('result', o['data']['text/plain']))
        elif o.output_type == 'display_data': out.append(('display', re.sub(r'id="[^"]*"', '', o['data'].get('text/html', ''))[:40]))
        else: out.append((o.output_type,))
    return out
for n, k in enumerate(SNIPS):
    a, b = norm(nb.cells[1 + 2 * n]), norm(nb.cells[2 + 2 * n])
    print(k, 'SAME' if a == b else 'DIFFERENT'); 
    if a != b: print('  plain:', a); print('  wrapped:', b)
    else: print('  ', a[:2])
