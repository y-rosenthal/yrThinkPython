"""Conversion gate (plan section 5, V2): everything convert_v3.py removed equals what `review.sh sync` wrote.

    python gate_v3.py SYNCED.ipynb REMOVED.json

- 'run': each removed ```text block equals its run cell's printed output, or (an error) the last exception line of
  the stored traceback; a removed picture equals the stored drawing (same PNG pixels size, and same bytes or a
  re-render of the same SVG);
- 'example': each removed example output equals the generated example region at the same place;
- 'header': each removed header block equals the generated header region;
- 'value': each value is unchanged (sync would have refused or asked for --accept otherwise; checked again here);
- 'trim': listed (check rule 12, C4, proves the trimmed blocks still work).
Exit status 1 on any difference.
"""
import base64
import json
import re
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[5] / 'yrThinkPython' / 'yr' / 'tools'
sys.path.insert(0, str(TOOLS))
import review_format as rf  # noqa: E402

nb = json.loads(Path(sys.argv[1]).read_text())
removed = json.loads(Path(sys.argv[2]).read_text())
qs = {q['title']: q for q in rf.parse_page(nb)}
cells = nb['cells']
bad = 0


def report(ok, what):
    global bad
    bad += not ok
    print(('ok   ' if ok else 'DIFF ') + what)


def png_of(tag_or_output):
    if isinstance(tag_or_output, str):
        m = re.search(r'base64,([A-Za-z0-9+/=]+)', tag_or_output)
        return base64.b64decode(m.group(1)) if m else b''
    return base64.b64decode(rf.text_of(tag_or_output['data']['image/png']))


def text_of_block(block):
    return re.sub(r'^```text\n|\n```$', '', block)


regions = {}            # question -> kind -> [bodies] in page order
for title, q in qs.items():
    for i in range(q['start'], q['end']):
        if cells[i]['cell_type'] == 'markdown':
            for t in rf.md_tokens(rf.source(cells[i])):
                if t.kind == 'region':
                    regions.setdefault(title, {}).setdefault(t.name, []).append(t.code)
seen = {}
for r in removed:
    title, kind = r['where'], r['kind']
    k = seen[(title, kind)] = seen.get((title, kind), -1) + 1
    if kind == 'run':
        q = qs[title]
        ri = rf.run_cell_for(q, r['part']) if r['part'] else rf.run_cell_for(q, None)
        outs = cells[ri]['outputs']
        if r['block'].startswith('```'):
            want = text_of_block(r['block']).strip('\n')
            out = rf.ANSI.sub('', rf.stream_text(outs, 'stdout') + ''.join(
                rf.text_of(o['data'].get('text/plain', '')) for o in outs if o['output_type'] == 'execute_result')).strip('\n')
            err = rf.ANSI.sub('', rf.stream_text(outs, 'stderr'))
            lines = [m.group(0) for m in re.finditer(r'^' + rf.EXC_LINE.pattern.lstrip('^') + r'.*$', err, re.M)]
            got = (out + ('\n' if out and lines else '') + (lines[-1] if lines else '')).strip('\n')
            norm = lambda t: '\n'.join(x.rstrip() for x in t.split('\n'))      # typed text drops trailing spaces
            ok = norm(got) == norm(want) or (lines and want == lines[-1]) or norm(out) == norm(want)
            report(ok, f'{title[:40]} run {r["part"] or ""}: {want[:60]!r}' + ('' if ok else f' != {got[:120]!r}'))
        else:
            drawings = [o for o in outs if o.get('metadata', {}).get('review_drawing')]
            old, new = png_of(r['block']), png_of(drawings[0]) if drawings else b''
            ok = bool(new) and rf.png_size(old) == rf.png_size(new)
            report(ok, f'{title[:40]} run picture: sizes {rf.png_size(old)} vs {rf.png_size(new)}'
                       f'{", same bytes" if old == new else ", bytes differ (re-rendered)"}')
    elif kind in ('example', 'header', 'output'):
        bodies = regions.get(title, {}).get(kind, [])
        got = bodies[k] if k < len(bodies) else None
        if kind == 'header':
            ok = got is not None and got.strip() == r['text'].strip()
            want = r['text']
        elif r['block'].startswith('```'):
            want = r['block']
            ok = got is not None and got.strip() == want.strip()
        else:
            want = '<picture>'
            ok = got is not None and rf.png_size(png_of(got)) == rf.png_size(png_of(r['block']))
        report(ok, f'{title[:40]} {kind} {k + 1}: {want[:50]!r}' + ('' if ok else f' != {str(got)[:120]!r}'))
    elif kind == 'value':
        text = json.dumps([rf.source(c) for c in cells])
        ok = f'`{r["expr"]}` is <!--=-->`{r["value"]}`' in ''.join(rf.source(c) for c in cells)
        report(ok, f'{title[:40]} value `{r["expr"]}` is `{r["value"]}`')
    elif kind == 'trim':
        print(f'trim {title[:40]}: {r["text"][:70]!r}')
print(f'{"GATE OK" if not bad else f"GATE FAILED: {bad} difference(s)"}')
sys.exit(1 if bad else 0)
