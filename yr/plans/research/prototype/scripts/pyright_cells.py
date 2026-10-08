"""For each code cell of Question 8 (and its Answer), run Pyright on that cell together with all code
cells above it (like Colab's editor sees it), and report the diagnostics that fall inside the cell."""
import json, subprocess, sys, re
import nbformat as nbf
PYRIGHT = '/tmp/claude-0/-home-user-yrThinkPython/6571a165-f8cc-5e43-8b74-c00357a4a6f6/scratchpad/pr/node_modules/.bin/pyright'
nb = nbf.read(sys.argv[1], 4)
q = next(i for i, c in enumerate(nb.cells) if c.source.startswith('### Question 8'))
e = next(i for i in range(q + 1, len(nb.cells)) if nb.cells[i].source.startswith('### '))
code = [(i, c.source) for i, c in enumerate(nb.cells) if c.cell_type == 'code' and c.source.strip() != '# Your code here']
for k, (i, src) in enumerate(code):
    if not q < i < e:
        continue
    above = '\n\n'.join(s for _, s in code[:k]) + '\n\n'
    start = above.count('\n')
    open('pyr/cell.py', 'w').write(above + src + '\n')
    r = subprocess.run([PYRIGHT, '--outputjson', 'pyr/cell.py'], capture_output=True, text=True)
    diags = json.loads(r.stdout).get('generalDiagnostics', [])
    mine = [d for d in diags if d['range']['start']['line'] >= start and 'jupyturtle' not in d['message']]
    print(f'--- cell {i}: {src.splitlines()[0][:50]!r}...  -> {len(mine)} diagnostic(s)')
    for d in mine:
        print(f"     line {d['range']['start']['line'] - start + 1}: {d['severity']}: {d['message'].splitlines()[0][:110]}")
