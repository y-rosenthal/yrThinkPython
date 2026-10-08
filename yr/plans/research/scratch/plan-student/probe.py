"""Probe the executed converted pages for rules the plan proposes:
 R1 every 'XxxError: msg' line in an Answer ```text block is produced by an error output of that question's run cells
 R2 every run_code-wrapped run cell produces an error output (no wrapped cell raises nothing)
 R3 execute_result text/plain appears in an Answer text block
 R4 headings / setext underlines inside Answer markdown
 R5 question code blocks immediately followed by a text block (heuristic fragility)
 R6 multi-block questions (need part labels)
"""
import re, sys, glob
import nbformat as nbf
TEXT = re.compile(r'```text\n(.*?)```', re.S)
ANS = re.compile(r'\s*#### Answer\s*$')
ERRLINE = re.compile(r'^([A-Za-z_]\w*(?:Error|Exception|Interrupt|Exit))\b: ?(.*)$', re.M)
ANSI = re.compile(r'\x1b\[[0-9;]*m')
def err_line(o):
    v = ANSI.sub('', o.get('evalue', '')); v = re.sub(r' \([^()]*, line \d+\)$', '', v); return f"{o['ename']}: {v}"
for path in sorted(glob.glob(sys.argv[1] + '/*.ipynb')):
    nb = nbf.read(path, 4)
    groups, cur = [], None
    for c in nb.cells:
        if c.cell_type == 'markdown' and c.source.lstrip().startswith('### '): cur = []; groups.append(cur)
        elif c.cell_type == 'markdown' and re.match(r'\s*#{1,2} ', c.source): cur = None
        if cur is not None: cur.append(c)
    for g in groups:
        title = g[0].source.splitlines()[0][4:40]
        k = next((i for i, c in enumerate(g) if c.cell_type == 'markdown' and ANS.match(c.source)), None)
        if k is None: continue
        q, a = g[:k], g[k+1:]
        amd = [c for c in a if c.cell_type == 'markdown']; runs = [c for c in a if c.cell_type == 'code']
        texts = [t.strip() for c in amd for t in TEXT.findall(c.source)]
        errs = [err_line(o) for c in runs for o in c.outputs if o.output_type == 'error']
        for t in texts:
            for m in ERRLINE.finditer(t):
                line = m.group(0).strip()
                if not any(e in line or line in e for e in errs):
                    print(f'R1 {path[-11:]} {title}: Answer shows "{line[:90]}" but no run cell raised it; errs={errs[:3]}')
        for c in runs:
            if c.source.lstrip().startswith('run_code(') and not any(o.output_type == 'error' for o in c.outputs):
                print(f'R2 {path[-11:]} {title}: wrapped cell raised nothing')
            for o in c.outputs:
                if o.output_type == 'execute_result':
                    tp = o.data.get('text/plain', '')
                    print(f'R3 {path[-11:]} {title}: execute_result {tp!r} in texts? {tp.strip() in texts}')
        for c in amd:
            body = re.sub(r'```.*?```', '', c.source, flags=re.S)
            for ln in body.splitlines():
                if re.match(r'\s{0,3}#{1,6}\s', ln) or re.match(r'\s{0,3}(=+|-{2,})\s*$', ln):
                    print(f'R4 {path[-11:]} {title}: heading-like line in Answer: {ln!r}')
        qmd = ''.join(c.source for c in q if c.cell_type == 'markdown')
        nblocks = 0
        has_ph = any(c.cell_type == 'code' and c.source.strip() == '# Your code here' for c in q)
        print(f'R6 {path[-11:]} {title}: run cells={len(runs)} placeholder={has_ph}') if len(runs) > 1 else None
