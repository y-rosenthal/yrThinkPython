"""Conversion gate: the expected-output blocks the converter removed from each Answer part equal the stored real
output that now replaces them (so removing them lost no information).

    python verify_removed.py NB REMOVED.json

Per part: the removed ```text blocks, in order, must equal the run cell's stdout lines followed by its error lines
(an error block may hold only the last line, 'Name: message', or a substring of it, as today's rule allowed);
a removed picture must be byte-identical to the stored PNG.
"""
import base64
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from review_v2 import parse_page, semantic, text_of

nb = json.load(open(sys.argv[1]))
removed = json.load(open(sys.argv[2]))
qs = {q['title']: q for q in parse_page(nb)}
groups = {}
for r in removed:
    groups.setdefault((r['question'], r['part']), []).append(r)
bad = 0
for (title, part), rs in groups.items():
    q = qs[title]
    ri = q['run_cells'][0] if part is None else next(i for i in q['run_cells'] if q['run_part'][i] == part)
    outs = nb['cells'][ri]['outputs']
    sem = semantic(outs)
    stdout = ''.join(s[1] for s in sem if s[0] == 'stream:stdout').rstrip('\n')
    errors = [f'{s[1]}: {s[2]}' for s in sem if s[0] == 'error']
    texts = [r['block'][len('```text\n'):-len('\n```')] for r in rs if r['block'].startswith('```text')]
    pics = [r for r in rs if not r['block'].startswith('```')]
    ok, what = True, []
    if texts:
        out_blocks = [t for t in texts if not any(t.startswith(e.split(':')[0] + ':') for e in errors)]
        err_blocks = [t for t in texts if t not in out_blocks]
        ok &= '\n'.join(out_blocks) == stdout
        ok &= len(err_blocks) == len(errors) and all(b in e for b, e in zip(err_blocks, errors))
        what.append(f'stdout={stdout!r:.60} errors={errors}')
    for r in pics:
        png = [o for o in outs if 'image/png' in o.get('data', {})]
        same = len(png) == 1 and r['src'] and base64.b64decode(r['src'].split(',', 1)[1]) == \
            base64.b64decode(text_of(png[0]['data']['image/png']))
        ok &= bool(same)
        what.append(f'removed picture {"byte-identical to" if same else "DIFFERS from"} the stored PNG')
    bad += not ok
    print(('OK  ' if ok else 'BAD ') + f'{title[:40]:40} part={part}: removed {len(rs)} block(s) | {"; ".join(what)[:130]}')
print(f'{len(groups) - bad}/{len(groups)} parts: removed blocks equal the stored real output ({len(removed)} blocks)')
sys.exit(1 if bad else 0)
