import json,re
EXC=re.compile(r'^[A-Z]\w*(Error|Exception|Interrupt|Exit)\b')
TEXT=re.compile(r'```text\n(.*?)```',re.S)
ANSI=re.compile(r'\x1b\[[0-9;]*m')
def eline(o):
    v=ANSI.sub('',o.get('evalue',''));v=re.sub(r' \([^()]*, line \d+\)$','',v);return f"{o['ename']}: {v}"
tot=0
for ch in '234567':
    nb=json.load(open(f'../repo-map/run/chap0{ch}_review.executed.ipynb'))
    src=lambda c:''.join(c['source'])
    groups=[];cur=None
    for c in nb['cells']:
        s=src(c).lstrip()
        if c['cell_type']=='markdown' and s.startswith('### '): cur=[];groups.append(cur)
        elif c['cell_type']=='markdown' and s.startswith(('# ','## ')): cur=None
        if cur is not None: cur.append(c)
    for g in groups:
        qn=re.search(r'Question (\d+)',src(g[0])).group(1)
        errs=[eline(o) for c in g if c['cell_type']=='code' for o in c.get('outputs',[]) if o['output_type']=='error']
        ans=''.join(src(c) for c in g if c['cell_type']=='markdown' and re.match(r'\s*<details>',src(c)))
        lines=[l.strip() for t in TEXT.findall(ans) for l in t.splitlines() if EXC.match(l.strip())]
        # also exception lines in prose (not text blocks)
        for l in lines:
            tot+=1
            if not any(l in e or e in l for e in errs):
                print(f'ch0{ch} Q{qn}: UNMATCHED answer line {l!r}; errors={errs}')
        # also check: lines starting with spaces? e.g. '    raise'
print('total exception-like lines',tot)
