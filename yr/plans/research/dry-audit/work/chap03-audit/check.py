import json,re,io,contextlib,sys
nb=json.load(open(sys.argv[1]))
cells=nb['cells']
q=None; qdefs={}
for c in cells:
    s=''.join(c['source'])
    m=re.match(r'### (Question \d+)',s)
    if m: q=m.group(1); qdefs[q]=[]
    if q and c['cell_type']=='code' and 'title' not in s and 'Your code' not in s and 'run_code' not in s and s.strip():
        qdefs[q].append(s)
    if q and c['cell_type']=='markdown':
        blocks=re.findall(r'```python\n(.*?)```',s,re.S)
        for b in blocks:
            examples=[]
        if '<details>' in s or s.startswith('```python') or 'Answer' in s:
            pass
        # record python blocks with text after
        for b,t in re.findall(r'```python\n(.*?)```\n```text\n(.*?)```',s,re.S):
            print(q,'EXAMPLE call',repr(b.strip()))
            ns={}
            # run with answer of this question later
            qdefs.setdefault(q+'_ex',[]).append((b,t))
        if ('<summary>Answer' in s) or (c['cell_type']=='markdown' and blocks and 'def ' in ''.join(blocks) and 'Start from' not in s and 'This code displays' not in s):
            for b in blocks:
                if 'def ' not in b: continue
                ns={}
                for d in qdefs[q]: exec(d,ns)
                out=io.StringIO()
                try:
                    with contextlib.redirect_stdout(out): exec(b,ns)
                    print(q,'ANSWER block OK')
                except Exception as e: print(q,'ANSWER FAIL',repr(e))
                # check examples with this solution
                for eb,et in qdefs.get(q+'_ex',[]):
                    o=io.StringIO()
                    try:
                        with contextlib.redirect_stdout(o): exec(eb,ns)
                        print('   example',repr(eb.strip()[:30]),'match' if o.getvalue()==et else 'MISMATCH '+repr(o.getvalue())+' vs '+repr(et))
                    except Exception as e: print('   example err',repr(e))
