"""Prototype (design-1): can sync GENERATE the write-code header block and the
Answer's import lines from the author's reference solution?  Read-only on yr/.
For every write-code question on today's pages:
  - reference = first ```python block in the Answer, minus top-level example calls
  - header    = 'def NAME(PARAMS):\n    ...' for each def named in today's header
  - imports   = import lines derived from free names, resolved via the setup cell
Compares each generated piece with what the author typed today."""
import ast, builtins, json, re, sys
from pathlib import Path

FENCE = re.compile(r'```python\n(.*?)```', re.S)

def src(c): return ''.join(c['source'])

def questions(nb):
    qs, cur = [], None
    for c in nb['cells']:
        s = src(c)
        if c['cell_type'] == 'markdown' and re.match(r'#{1,3} ', s):
            if s.startswith('### Question'):
                cur = {'head': s.splitlines()[0], 'cells': []}; qs.append(cur)
            else:
                cur = None
        if cur is not None: cur['cells'].append(c)
    return qs

def setup_imports(nb):
    """name -> import line, from the setup cell."""
    out = {}
    for c in nb['cells']:
        if c['cell_type'] == 'code' and 'setup' in c['metadata'].get('tags', []):
            for node in ast.walk(ast.parse(src(c))):
                if isinstance(node, ast.Import):
                    for a in node.names: out[a.asname or a.name] = f'import {a.name}'
                elif isinstance(node, ast.ImportFrom):
                    for a in node.names: out[a.asname or a.name] = ('from', node.module, a.name)
    return out

def strip_calls(code):
    """Drop top-level expression statements (example calls) and the blank lines around them."""
    tree = ast.parse(code); lines = code.splitlines()
    drop = set()
    for n in tree.body:
        if isinstance(n, ast.Expr) and not isinstance(n.value, ast.Constant):
            drop.update(range(n.lineno - 1, n.end_lineno))
    kept = [l for i, l in enumerate(lines) if i not in drop]
    return '\n'.join(kept).rstrip() + '\n'

def header_of(code, names):
    tree = ast.parse(code); lines = code.splitlines(); out = []
    for n in tree.body:
        if isinstance(n, ast.FunctionDef) and (names is None or n.name in names):
            first = n.body[0].lineno - 1
            if (isinstance(n.body[0], ast.Expr) and isinstance(n.body[0].value, ast.Constant)):
                pass  # docstring: header stops before it either way
            sig = lines[n.lineno - 1: first]
            # a one-line body on the def line is not used on these pages
            out.append('\n'.join(sig) + '\n    ...')
    return '\n\n'.join(out) + '\n'

def free_names(code):
    tree = ast.parse(code)
    bound, used = set(), set()
    for n in ast.walk(tree):
        if isinstance(n, (ast.FunctionDef, ast.ClassDef)): bound.add(n.name)
        elif isinstance(n, ast.arg): bound.add(n.arg)
        elif isinstance(n, ast.Name):
            (bound if isinstance(n.ctx, ast.Store) else used).add(n.id)
        elif isinstance(n, (ast.Import, ast.ImportFrom)):
            for a in n.names: bound.add((a.asname or a.name).split('.')[0])
    return sorted(used - bound - set(dir(builtins)))

def derive_imports(names, setup):
    plain, frm = [], {}
    names = sorted(names, key=lambda n: list(setup).index(n) if n in setup else 999)
    for nm in names:
        imp = setup.get(nm)
        if imp is None: continue
        if isinstance(imp, str): plain.append(imp)
        else: frm.setdefault(imp[1], []).append(imp[2])
    return plain + [f'from {m} import ' + ', '.join(v) for m, v in frm.items()]

if __name__ == '__main__':
    ROOT = Path(sys.argv[1])
    tot = {'q': 0, 'hdr_same': 0, 'hdr_diff': 0, 'imp_same': 0, 'imp_diff': 0}
    for nbp in sorted(ROOT.glob('yr/chap0*_review.ipynb')):
        nb = json.load(open(nbp)); setup = setup_imports(nb)
        for q in questions(nb):
            md = '\n'.join(src(c) for c in q['cells'] if c['cell_type'] == 'markdown')
            if 'Start from this header' not in md: continue
            qpart, apart = md.split('<summary>Answer</summary>', 1)
            hdr_typed = FENCE.search(qpart.split('Start from this header', 1)[1]).group(1)
            sols = FENCE.findall(apart)
            names = [n.name for n in ast.parse(hdr_typed.replace('...', 'pass')).body]
            # reference: first Answer block that defines every header name
            ref = next(s for s in sols if all(re.search(rf'^def {n}\(', s, re.M) for n in names))
            ref = strip_calls(ref)
            gen = header_of(ref, names)
            tot['q'] += 1
            same = gen.strip() == hdr_typed.strip()
            tot['hdr_same' if same else 'hdr_diff'] += 1
            typed_imps = [l for l in ref.splitlines() if l.startswith(('import ', 'from '))]
            body = '\n'.join(l for l in ref.splitlines() if l not in typed_imps)
            # R3: helpers the question provides are dropped from the Answer
            helpers = [n.name for n in ast.parse(body).body
                       if isinstance(n, ast.FunctionDef) and n.name not in names]
            fn = free_names(body)
            got = derive_imports(fn, setup)
            isame = sorted(got) == sorted(typed_imps)
            tot['imp_same' if isame else 'imp_diff'] += 1
            undefined = [n for n in fn if n not in setup]
            print(f'{nbp.name} {q["head"][:46]:46} header:{"same" if same else "DIFF"} '
                  f'imports:{"same" if isame else "DIFF"} needs-from-question:{undefined} other-defs:{helpers}')
            if not same: print('   typed:', repr(hdr_typed), '\n   gen:  ', repr(gen))
            if not isame: print('   typed:', typed_imps, '\n   gen:  ', got)
    print(tot)
