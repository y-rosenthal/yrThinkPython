import json,re,sys,glob
ANSI=re.compile(r'\x1b\[[0-9;]*m')
TEXT=re.compile(r'```text\n(.*?)```',re.S)
EXC=re.compile(r'^[A-Z]\w*(Error|Exception|Interrupt|Exit)\b')
EXC2=re.compile(r'^\s*[A-Z]\w*(Error|Exception|Warning|Interrupt|Exit|Iteration)\b')
def src(c): s=c['source']; return ''.join(s) if isinstance(s,list) else s
for p in sorted(glob.glob(sys.argv[1])):
    nb=json.load(open(p))
    groups=[];cur=None
    for c in nb['cells']:
        s=src(c).lstrip()
        if c['cell_type']=='markdown' and s.startswith('### '): cur=[];groups.append(cur)
        elif c['cell_type']=='markdown' and s.startswith(('# ','## ')): cur=None
        if cur is not None: cur.append(c)
    for g in groups:
        title=src(g[0]).lstrip().splitlines()[0]
        ans=[c for c in g if c['cell_type']=='markdown' and re.match(r'\s*<details>\s*<summary>Answer</summary>',src(c))]
        errs=[]; stderr=[]; ex=[]
        for c in g:
            if c['cell_type']!='code': continue
            for o in c.get('outputs',[]):
                if o['output_type']=='error':
                    v=ANSI.sub('',o['evalue']); v=re.sub(r' \([^()]*, line \d+\)$','',v)
                    errs.append(f"{o['ename']}: {v}")
                if o['output_type']=='stream' and o['name']=='stderr': stderr.append(''.join(o['text'])[:200])
                if o['output_type']=='execute_result': ex.append(o['data'].get('text/plain'))
        lines=[l for a in ans for t in TEXT.findall(src(a)) for l in t.splitlines() if EXC.match(l)]
        lines2=[l for a in ans for t in TEXT.findall(src(a)) for l in t.splitlines() if EXC2.match(l) and not EXC.match(l)]
        unmatched=[l for l in lines if not any(l.strip() in e or e in l.strip() for e in errs)]
        if unmatched or lines2 or stderr or ex:
            print(p.split('/')[-1][:6], title[:50]); 
            if unmatched: print('   UNMATCHED exc lines:',unmatched,'| errs:',errs)
            if lines2: print('   other exc-like lines not caught by regex:',lines2)
            if stderr: print('   STDERR:',stderr)
            if ex: print('   EXEC_RESULT:',ex)
