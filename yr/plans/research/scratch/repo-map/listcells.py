import json, sys, re
for p in sys.argv[1:]:
    nb = json.load(open(p))
    print('=' * 30, p, len(nb['cells']), 'cells')
    for i, c in enumerate(nb['cells']):
        s = ''.join(c['source'])
        s = re.sub(r'data:image/png;base64,[A-Za-z0-9+/=]+', 'data:PNG', s)
        tags = c.get('metadata', {}).get('tags', [])
        n = int(sys.argv[0] and 0) 
        lines = s.splitlines()
        print(f'--- [{i}] {c["cell_type"]} id={c.get("id")} tags={tags} ({len(lines)} lines)')
        if c['cell_type'] == 'code':
            for l in lines: print('   |', l)
        else:
            for l in lines[:int(__import__("os").environ.get("MDL", "6"))]: print('   >', l)
