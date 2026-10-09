import json, re, io, contextlib, sys
nb = json.load(open(sys.argv[1]))
cells = nb['cells']
def run(code, ns):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        try: exec(code, ns)
        except Exception as e: print(f'{type(e).__name__}: {e}')
    return buf.getvalue()
# 1. predict questions: code cell then answer text block
qns = {}
cur = None
for c in cells:
    s = ''.join(c['source'])
    m = re.match(r'### (Question \d+)', s)
    if m: cur = m.group(1); qns[cur] = []
    if cur: qns[cur].append(c)
for q, cs in qns.items():
    ns = {}  # no setup import
    qcode = [''.join(c['source']) for c in cs if c['cell_type']=='code' and '# Your code here' not in ''.join(c['source'])]
    out = ''.join(run(code, ns) for code in qcode)
    md = '\n'.join(''.join(c['source']) for c in cs if c['cell_type']=='markdown')
    ans = md.split('<summary>Answer</summary>')[-1] if '<summary>Answer' in md else ''
    qtext = md.split('<summary>Answer</summary>')[0]
    tb = re.findall(r'```text\n(.*?)```', ans, re.S)
    if qcode and tb:
        exp = tb[0]
        print(q, 'PREDICT', 'OK' if out.strip()==exp.strip() or exp.strip().split(':')[0] in out else f'DIFF got {out!r} want {exp!r}')
    # examples in question: python then text
    pairs = re.findall(r'```python\n(.*?)```\n```text\n(.*?)```', qtext, re.S)
    blocks = re.findall(r'```python\n(.*?)```', ans, re.S)
    for k, b in enumerate(blocks):
        ans_ns = dict(ns)  # question definitions only, no 'math' from setup
        o = run(b, ans_ns)
        err = [l for l in o.splitlines() if re.match(r'\w+Error', l)]
        print(q, f'ANSWER block {k+1}', 'ERR '+str(err) if err else 'runs', '| out:', o.replace('\n',' / ')[:90])
        if k == 0 and pairs:
            for call, want in pairs:
                got = run(call, ans_ns)
                print(q, '  EXAMPLE', call.strip().replace('\n','; '), '->', 'OK' if got==want else f'DIFF got {got!r} want {want!r}')
