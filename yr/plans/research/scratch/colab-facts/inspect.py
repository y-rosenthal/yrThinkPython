import json, sys
for fn in sys.argv[1:]:
    nb = json.load(open(fn))
    md = nb['metadata']
    print('=====', fn, 'nbformat', nb['nbformat'], nb['nbformat_minor'])
    print('metadata.colab =', json.dumps(md.get('colab'))[:600])
    cs = md.get('colab', {}).get('collapsed_sections', [])
    cells = nb['cells']
    for i, c in enumerate(cells):
        cid_md = c.get('metadata', {}).get('id')
        cid_top = c.get('id')
        if cid_md in cs or cid_top in cs:
            src = ''.join(c['source'])
            print(f'  collapsed id match cell#{i} type={c["cell_type"]} md.id={cid_md} top.id={cid_top} src={src[:120]!r}')
            # show following cells until next heading of same or higher level
            j = i+1
            while j < len(cells) and j < i+6:
                cj = cells[j]
                s = ''.join(cj['source'])
                print(f'      next#{j} {cj["cell_type"]} md={json.dumps(cj.get("metadata"))[:150]} src={s[:80]!r}')
                j += 1
    # count which ids style is used
    n_md = sum(1 for c in cells if 'id' in c.get('metadata', {}))
    n_top = sum(1 for c in cells if 'id' in c)
    print('  cells', len(cells), 'with metadata.id', n_md, 'with top-level id', n_top)
