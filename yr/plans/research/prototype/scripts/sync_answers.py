"""Option A prototype ('review_cells.py sync NB'): the question's ```python blocks are the single source;
regenerate each Answer's code cells from them. Wrap a block in run_code(\"\"\"...\"\"\") if the existing
cell already did, or if it does not compile (syntax error). Stdlib only, like review_cells.py."""
import json, re, secrets, sys
sys.path.insert(0, 'repo/yr/tools')
PY = re.compile(r'```python\n(.*?)```', re.S)
SIGNATURE = re.compile(r'```python\n(?:\s*def \w+\(.*\):\n\s+\.\.\.\n)+')
ANSWER = re.compile(r'\s*#### Answer\s*$')
RUN = re.compile(r'\s*run_code\("""\n(.*?)\n?"""\)\s*$', re.S)
text = lambda c: ''.join(c['source'])
def lines(s):
    p = s.split('\n'); return [x + '\n' for x in p[:-1]] + [p[-1]]

def blocks(md):
    out = []
    for m in PY.finditer(md):
        if re.match(r'\s*(```text\n|<img\b[^>]*\bdata-turtle)', md[m.end():]) or SIGNATURE.match(m.group(0)):
            continue
        out.append(m.group(1).strip('\n'))
    return out

def needs_wrap(code, old):
    if old is not None and re.sub(r'^(#.*\n)+', '', old).lstrip().startswith('run_code('):
        return True
    try:
        compile(code, '<q>', 'exec'); return False
    except SyntaxError:
        return True

nb = json.load(open(sys.argv[1]))
cells, used = nb['cells'], {c.get('id') for c in nb['cells']}
starts = [i for i, c in enumerate(cells) if c['cell_type'] == 'markdown' and text(c).lstrip().startswith('### ')]
changed = 0
for s in reversed(starts):
    e = next((j for j in range(s + 1, len(cells)) if cells[j]['cell_type'] == 'markdown' and re.match(r'\s*#{1,3} ', text(cells[j]))), len(cells))
    h = next((j for j in range(s, e) if cells[j]['cell_type'] == 'markdown' and ANSWER.match(text(cells[j]))), None)
    if h is None:
        continue
    qb = blocks(''.join(text(c) for c in cells[s:h] if c['cell_type'] == 'markdown'))
    run_idx = [j for j in range(h + 1, e) if cells[j]['cell_type'] == 'code']
    old = [text(cells[j]) for j in run_idx]
    new = []
    for k, b in enumerate(qb):
        o = old[k] if k < len(old) else None
        comment = re.match(r'(#.*\n)', o).group(1) if o and re.match(r'#.*\n', o) else ("# The question's code: run it to see its output\n" if len(qb) == 1 else f"# Part {chr(97 + k)}: the question's code\n")
        new.append(comment + (f'run_code("""\n{b}\n""")' if needs_wrap(b, o) else b))
    if new == old:
        continue
    changed += 1
    for j in reversed(run_idx):
        del cells[j]
    at = run_idx[0] if run_idx else e
    for k, src in enumerate(new):
        cid = secrets.token_hex(4)
        while cid in used: cid = secrets.token_hex(4)
        used.add(cid)
        cells.insert(at + k, {'cell_type': 'code', 'execution_count': None, 'id': cid, 'metadata': {}, 'outputs': [], 'source': lines(src)})
    print(f'{text(cells[s]).splitlines()[0]}: {len(new)} Answer code cell(s) regenerated')
json.dump(nb, open(sys.argv[1], 'w'), indent=1, ensure_ascii=False); open(sys.argv[1], 'a').write('\n')
print(f'{changed} question(s) updated')
