"""Print a notebook's cells compactly (type, id, metadata, source, outputs summary)."""
import json, sys
nb = json.load(open(sys.argv[1]))
lo, hi = (int(sys.argv[2]), int(sys.argv[3])) if len(sys.argv) > 3 else (0, 10**6)
print('metadata:', json.dumps(nb['metadata']))
for i, c in enumerate(nb['cells']):
    if not lo <= i < hi: continue
    s = ''.join(c['source'])
    if len(s) > 1500: s = s[:1500] + ' ...[%d chars]' % len(s)
    print(f'===== [{i}] {c["cell_type"]} id={c.get("id")} meta={json.dumps(c["metadata"])}' + (f' exec={c.get("execution_count")}' if c['cell_type']=='code' else ''))
    print(s)
    for o in c.get('outputs', []):
        t = o['output_type']
        if t == 'stream': print(f'   -> stream:{o["name"]}: {"".join(o["text"])[:300]!r}')
        elif t == 'error': print(f'   -> error: {o["ename"]}: {o["evalue"][:100]!r} ({len(o["traceback"])} tb items)')
        else: print(f'   -> {t}: {list(o.get("data",{}))} exec={o.get("execution_count")}')
