import re, json, nbformat as nbf
from pathlib import Path
here = Path(__file__).parent
PY = re.compile(r'```python\n(.*?)```', re.S)
TXT = re.compile(r'```text\n(.*?)```', re.S)
IMG = re.compile(r'<img\b[^>]*\bdata-turtle\b[^>]*>')
def is_answer(c): return c.cell_type=='markdown' and re.match(r'\s*<details>\s*<summary>Answer</summary>', c.source)
def outsum(c):
    parts=[]
    for o in c.outputs:
        t=o.output_type
        if t=='stream': parts.append(f"{o.name}:{len(o.text.splitlines())}L")
        elif t=='error': parts.append(f"ERR {o.ename}")
        elif t in('display_data','execute_result'):
            keys=','.join(sorted(o.data.keys()))
            parts.append(f"{'RESULT' if t=='execute_result' else 'DISPLAY'}[{keys}]")
    return ' '.join(parts) or '-'
for p in sorted((here/'run').glob('*.executed.ipynb')):
    nb=nbf.read(p,nbf.NO_CONVERT)
    print('=====',p.name)
    cur=None; groups=[]
    for i,c in enumerate(nb.cells):
        if c.cell_type=='markdown' and c.source.lstrip().startswith('### '):
            cur=[]; groups.append(cur)
        elif c.cell_type=='markdown' and c.source.lstrip().startswith(('# ','## ')):
            cur=None
        if cur is not None: cur.append((i,c))
        if c.cell_type=='code' and 'setup' in c.metadata.get('tags',[]):
            print(f'  setup cell {i}: outputs {outsum(c)}')
    for g in groups:
        title=g[0][1].source.strip().splitlines()[0][4:]
        items=[]
        for i,c in g:
            tags=c.metadata.get('tags',[])
            if c.cell_type=='code':
                src=c.source.strip()
                if src=='# Your code here': kind='YOURCODE'+('(no-sig)' if 'no-signature' in tags else '')
                elif src.startswith('run_code('): kind='run_code'
                elif re.match(r'^\s*def ',src) and not re.search(r'^[^\s#].*\(', '\n'.join(l for l in src.splitlines() if not l.startswith((' ','def','\t','"""'))), re.M): kind='DEF-only'
                else: kind='code'
                if 'raises-exception' in tags: kind+='+RX'
                items.append(f"[{i}]{kind}=>{outsum(c)}")
            elif is_answer(c):
                items.append(f"[{i}]ANSWER(py={len(PY.findall(c.source))},txt={len(TXT.findall(c.source))},img={len(IMG.findall(c.source))})")
            else:
                s=c.source
                d=' def' if 'Run this cell to define' in s else ''
                items.append(f"[{i}]md(py={len(PY.findall(s))},img={len(IMG.findall(s))}{d})")
        print(f"  {title}\n      "+'  '.join(items))
