import json,re,sys
nb=json.load(open(sys.argv[1]))
lo,hi = (int(sys.argv[2]), int(sys.argv[3])) if len(sys.argv)>3 else (0, 10**6)
print('notebook metadata:', json.dumps(nb['metadata']))
for i,c in enumerate(nb['cells']):
    if not lo<=i<=hi: continue
    s=''.join(c['source'])
    s=re.sub(r'data:image/png;base64,[A-Za-z0-9+/=]+','data:...',s)
    print(f"---- cell {i} {c['cell_type']} id={c.get('id')} meta={json.dumps(c['metadata'])}")
    print(s)
    for o in c.get('outputs',[]):
        t=o['output_type']
        if t=='stream': print(f'   [{t}:{o["name"]}]', repr(''.join(o['text'])[:300]))
        elif t=='error': print(f'   [error] {o["ename"]}: {o["evalue"]}  ({len(o["traceback"])} tb entries)')
        else: print(f'   [{t}]', list(o.get('data',{}).keys()))
