import json,sys
for fn in sys.argv[1:]:
    try: nb=json.load(open(fn))
    except Exception as e: print(fn, 'ERR', e); continue
    cs=nb['metadata'].get('colab',{}).get('collapsed_sections',[])
    if not cs: continue
    print('=====',fn, 'nbformat',nb['nbformat'],nb['nbformat_minor'],'collapsed_sections=',cs[:6])
    cells=nb['cells']
    for i,c in enumerate(cells):
        mid=c.get('metadata',{}).get('id')
        if mid in cs or c.get('id') in cs:
            print('  cell',i,c['cell_type'],'meta=',json.dumps(c['metadata'])[:150],'top-id=',c.get('id'),repr(''.join(c['source'])[:80]))
