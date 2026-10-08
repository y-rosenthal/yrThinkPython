import json, sys
for p in sys.argv[1:]:
    nb = json.load(open(p))
    md = nb.get('metadata', {})
    col = md.get('colab', {})
    print('=====', p.split('/')[-1], 'nbformat', nb.get('nbformat'), nb.get('nbformat_minor'))
    print(' colab meta keys:', {k: (v if k!='provenance' else '...') for k,v in col.items()})
    cs = col.get('collapsed_sections', [])
    idx = {}
    for i,c in enumerate(nb['cells']):
        mid = c.get('metadata',{}).get('id'); tid = c.get('id')
        for x in (mid, tid):
            if x: idx.setdefault(x, []).append((i, 'meta' if x==mid else 'top'))
    for s in cs:
        hits = idx.get(s)
        if not hits: print('  ', s, 'NOT FOUND'); continue
        i = hits[0][0]; c = nb['cells'][i]
        src = ''.join(c['source'])[:80].replace('\n','\\n')
        nxt = [(nb['cells'][j]['cell_type'], ''.join(nb['cells'][j]['source'])[:50].replace('\n','\\n')) for j in range(i+1, min(i+3, len(nb['cells'])))]
        print('  ', s, hits, c['cell_type'], repr(src), 'top-id=',c.get('id'), 'meta=',c.get('metadata'))
        print('      next:', nxt)
