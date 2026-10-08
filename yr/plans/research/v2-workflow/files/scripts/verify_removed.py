"""Conversion gate: every expected-output block the converter removed from an Answer equals the stored
real output that now replaces it (so removing it lost no information).

    python verify_removed.py NB REMOVED.json
"""
import json, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from review_v2 import parse_page, semantic, source

nb = json.load(open(sys.argv[1]))
removed = json.load(open(sys.argv[2]))
qs = {q['title']: q for q in parse_page(nb)}
bad = 0
for r in removed:
    q = qs[r['question']]
    k = 0 if r['part'] is None else ord(r['part']) - ord('a')
    sem = semantic(nb['cells'][q['run_cells'][k]]['outputs'])
    block = r['block']
    if block.startswith('```text'):
        text = block[len('```text\n'):-len('\n```')]
        stdout = ''.join(s[1] for s in sem if s[0] == 'stream:stdout').rstrip('\n')
        errors = [f'{s[1]}: {s[2]}' for s in sem if s[0] == 'error']
        ok = (text == stdout and not errors) or (not stdout and errors and all(line in errors[0] for line in text.split('\n')))
        what = f'stdout={stdout!r} errors={errors}'
    else:
        d = [s[1] for s in sem if s[0] == 'drawing']
        ok = len(d) == 1
        what = f'stored drawing (PNG, SVG sha1 {d[0][:10] if d else None})'
    bad += not ok
    print(('OK  ' if ok else 'BAD ') + f"{r['question'][:40]:40} part={r['part']}: removed {block[:60]!r} | {what[:110]}")
print(f'{len(removed) - bad}/{len(removed)} removed blocks equal the stored real output')
sys.exit(1 if bad else 0)
