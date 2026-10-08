import json,re,sys,ast
EXC=re.compile(r'^[A-Z]\w*(Error|Exception|Interrupt|Exit)\b',re.M)
TEXT=re.compile(r'```text\n(.*?)```',re.S)
for ch in '234567':
    p=f'/home/user/yrThinkPython/yr/chap0{ch}_review.ipynb'
    nb=json.load(open(p))
    cells=nb['cells']
    src=lambda c:''.join(c['source'])
    # setup cell tags
    for i,c in enumerate(cells[:12]):
        if c['cell_type']=='code':
            print(f'ch0{ch} early code cell {i} tags={c["metadata"].get("tags")} first={src(c).splitlines()[0][:60]!r}')
    groups=[];cur=None
    for i,c in enumerate(cells):
        s=src(c).lstrip()
        if c['cell_type']=='markdown' and s.startswith('### '):
            cur=[];groups.append(cur)
        elif c['cell_type']=='markdown' and s.startswith(('# ','## ')):
            cur=None
        if cur is not None: cur.append((i,c))
    for g in groups:
        title=src(g[0][1]).splitlines()[0]
        qn=re.search(r'Question (\d+)',title).group(1)
        codes=[(i,c) for i,c in g if c['cell_type']=='code']
        ph=[i for i,c in codes if src(c).strip()=='# Your code here']
        others=[(i,c) for i,c in codes if src(c).strip()!='# Your code here']
        ans=[c for i,c in g if c['cell_type']=='markdown' and re.match(r'\s*<details>',src(c))]
        anstext=''.join(src(a) for a in ans)
        exlines=[l for t in TEXT.findall(anstext) for l in t.splitlines() if EXC.match(l)]
        if ph and others:
            print(f'ch0{ch} Q{qn}: placeholder AND other code cells {[i for i,_ in others]}')
        if ph and exlines:
            print(f'ch0{ch} Q{qn}: write-code answer has exception-like text lines: {exlines}')
        # count non-def cells
        nondef=[]
        for i,c in others:
            s=src(c)
            try:
                t=ast.parse(s)
                defonly=all(isinstance(n,(ast.FunctionDef,ast.ClassDef,ast.Import,ast.ImportFrom,ast.Assign)) for n in t.body)
            except SyntaxError: defonly=False
            if defonly and 'raises-exception' not in c['metadata'].get('tags',[]):
                kinds={type(n).__name__ for n in t.body}
                prev=src(cells[i-1])[-120:].replace('\n',' | ')
                print(f'ch0{ch} Q{qn}: def-only cell {i} kinds={kinds} prev_md=...{prev!r}')
            else: nondef.append(i)
        if len(nondef)>=2:
            labs=[]
            for i in nondef:
                prev=src(cells[i-1]).strip().splitlines()
                labs.append(prev[-1][:40] if prev else '')
            print(f'ch0{ch} Q{qn}: {len(nondef)} run cells; preceding lines {labs}')
        if 'img' in anstext and len(nondef)!=1:
            n_img=anstext.count('data-turtle')
            print(f'ch0{ch} Q{qn}: answer has {n_img} turtle imgs, run cells={len(nondef)}')
        for i,c in others:
            s=src(c)
            if re.search(r'input\(|random|%%|^%',s,re.M): print(f'ch0{ch} Q{qn} cell {i}: special: {s[:80]!r}')
        # answer: exception lines vs which cells raise (tagged)
        if exlines and not ph:
            tagged=[i for i,c in others if 'raises-exception' in c['metadata'].get('tags',[])]
            if not tagged: print(f'ch0{ch} Q{qn}: answer has exception lines {exlines} but no raising cell')
