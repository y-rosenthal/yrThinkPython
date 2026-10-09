"""R3 prototype: run each Answer ```python block in a namespace holding the question's own
definition code cells (not the setup cell), first as written, then with helper defs that the
question also shows (as markdown or a cell) removed."""
import json, re, sys, io, contextlib, ast
nb = json.load(open(sys.argv[1]))
cells = nb['cells']
PY = re.compile(r'```python\n(.*?)```', re.S)
groups, cur = [], None
for c in cells:
    s = ''.join(c['source'])
    if c['cell_type'] == 'markdown' and s.lstrip().startswith('### '):
        cur = []; groups.append(cur)
    elif c['cell_type'] == 'markdown' and s.lstrip().startswith(('# ', '## ')):
        cur = None
    if cur is not None: cur.append(c)
def defs(src):
    try: return {n.name for n in ast.parse(src).body if isinstance(n, ast.FunctionDef)}
    except SyntaxError: return set()
def strip(src, names):
    tree = ast.parse(src); lines = src.splitlines(True); out = []
    drop = set()
    for n in tree.body:
        if isinstance(n, ast.FunctionDef) and n.name in names:
            drop |= set(range(n.lineno - 1, n.end_lineno))
    return ''.join(l for i, l in enumerate(lines) if i not in drop)
for g in groups:
    title = ''.join(g[0]['source']).splitlines()[0]
    ans = [c for c in g if c['cell_type']=='markdown' and re.match(r'\s*<details>\s*<summary>Answer', ''.join(c['source']))]
    qmd = ''.join(''.join(c['source']) for c in g if c['cell_type']=='markdown' and c not in ans)
    defcells = [''.join(c['source']) for c in g if c['cell_type']=='code' and ''.join(c['source']).lstrip().startswith('def ')]
    provided_md = set().union(*[defs(b) for b in PY.findall(qmd) if '...' not in b] or [set()])
    provided_cell = set().union(*[defs(s) for s in defcells] or [set()])
    for k, block in enumerate(PY.findall(''.join(''.join(a['source']) for a in ans)), 1):
        rep = (defs(block) & (provided_md | provided_cell))
        res = []
        for label, code in (('as written', block), ('helpers removed', strip(block, rep))):
            if label == 'helpers removed' and not rep: continue
            ns = {'__name__': '__main__'}
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    for d in defcells: exec(d, ns)   # question's definition cells only
                    exec(code, ns)
                res.append(f'{label}: OK')
            except Exception as e:
                res.append(f'{label}: {type(e).__name__}: {e}')
        print(f'{title[:45]:45} block {k}: repeats provided helpers {sorted(rep) or "-"} | ' + ' | '.join(res))
