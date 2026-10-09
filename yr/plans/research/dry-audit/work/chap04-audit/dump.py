import json,sys
nb=json.load(open(sys.argv[1]))
for i,c in enumerate(nb['cells']):
    src=''.join(c['source'])
    print(f"===== [{i}] {c['cell_type']} id={c.get('id')} meta={json.dumps(c.get('metadata',{}))[:200]}")
    print(src)
    if c['cell_type']=='code' and c.get('outputs'):
        for o in c['outputs']:
            t=o.get('text') or o.get('data',{}).get('text/plain') or o.get('ename')
            if isinstance(t,list): t=''.join(t)
            print(f"  --> OUT[{o['output_type']}]: {str(t)[:400]}")
