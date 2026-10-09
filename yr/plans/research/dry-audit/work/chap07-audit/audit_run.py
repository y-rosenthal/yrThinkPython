"""Run chap07 review: question code cells, Answer python blocks (standalone, and R3-style),
and Examples calls, printing real outputs to compare with hand-typed values."""
import json, re, io, contextlib, traceback, sys
nb = json.load(open(sys.argv[1]))
cells = nb['cells']
src = lambda c: ''.join(c['source'])
def run(code, ns):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        try: exec(code, ns)
        except Exception as e: print(f'!! {type(e).__name__}: {e}')
    return buf.getvalue()
q = None
for c in cells:
    s = src(c)
    m = re.match(r'### (Question \d+)', s)
    if m:
        q = m.group(1); qdefs = {'__name__': '__main__'}
        print('\n#####', q)
        # examples in question
        for call, out in re.findall(r'```python\n(.*?)```\n```text\n(.*?)```', s, re.S):
            print('EXAMPLE call:', call.strip(), '| typed:', repr(out))
            qdefs.setdefault('_examples', []).append((call, out))
        continue
    if q is None: continue
    if c['cell_type'] == 'code' and 'Your code here' not in s and 'setup' not in c['metadata'].get('tags', []):
        ns = {'__name__': '__main__', 'run_code': lambda code: exec(code, ns)}
        print('QUESTION CELL output:', repr(run(s, ns)))
    if c['cell_type'] == 'markdown' and ('<summary>Answer' in s or 'Answer' in s[:12] or True):
        for t in re.findall(r'```text\n(.*?)```', s, re.S):
            if '**Examples**' not in s: print('TYPED text block:', repr(t))
        if '**Examples**' in s or s.startswith('### '): continue
        for k, b in enumerate(re.findall(r'```python\n(.*?)```', s, re.S)):
            ns = {'__name__': '__main__'}
            out = run(b, ns)
            print(f'ANSWER block {k} standalone output:', repr(out))
            for call, typed in qdefs.get('_examples', []):
                eo = run(call, dict(ns))
                print('   example', call.strip(), 'real', repr(eo), 'typed', repr(typed), 'OK' if eo == typed else 'DIFF')
