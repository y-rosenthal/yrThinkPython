"""Prototype (design-1): generator-first sync for a write-code question.

Author writes (once): the prompt with a <!-- header --> marker, example calls as
```python blocks, '#### Answer', and the solution as a ```python block (no
imports, no example calls).  sync generates: the header block, the ```text
block after every python block (examples in the question AND fix/variant blocks
in the Answer), and the import line(s) at the top of each Answer block.
Then check: R3 (each Answer block + each example runs WITHOUT the setup cell's
imports and gives the generated output) and idempotence."""
import ast, builtins, contextlib, io, json, re, sys
sys.path.insert(0, '.')
from gen_static import header_of, free_names

PY = re.compile(r'```python\n(.*?)```\n(?:```text\n.*?```\n)?', re.S)
HDR = re.compile(r'<!-- header -->\n(?:.*?<!-- /header -->\n)?', re.S)
IMP = re.compile(r'^(?:import \w+|from \w+ import [\w, ]+)\n', re.M)

def run(code, ns):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        try:
            exec(compile(code, '<example>', 'exec'), ns)
        except Exception as e:
            print(f'{type(e).__name__}: {e}')
    return buf.getvalue()

def setup_table(setup):
    t = {}
    for n in ast.parse(setup).body:
        if isinstance(n, ast.Import):
            for a in n.names: t[a.asname or a.name] = f'import {a.name}'
        elif isinstance(n, ast.ImportFrom):
            for a in n.names: t[a.asname or a.name] = (n.module, a.name)
    return t

def imports_for(code, table):
    names = [n for n in free_names(code) if n in table]
    names.sort(key=list(table).index)
    plain = [table[n] for n in names if isinstance(table[n], str)]
    frm = {}
    for n in names:
        if not isinstance(table[n], str): frm.setdefault(table[n][0], []).append(table[n][1])
    lines = plain + [f'from {m} import {", ".join(v)}' for m, v in frm.items()]
    return ''.join(l + '\n' for l in lines) + ('\n' if lines else '')

def sync(nb):
    setup = ''.join(nb['cells'][0]['source']); table = setup_table(setup)
    cells = nb['cells']
    a = next(i for i, c in enumerate(cells) if ''.join(c['source']).strip() == '#### Answer')
    question, answer = cells[1:a], cells[a + 1:]
    defs = ''.join(''.join(c['source']) + '\n' for c in question if c['cell_type'] == 'code')
    # 1. Answer blocks: (re)write the import lines sync owns, at the top
    for c in answer:
        s = ''.join(c['source'])
        def fix(m):
            body = IMP.sub('', m.group(1)).lstrip('\n')
            return f'```python\n{imports_for(body, table)}{body}```\n'
        c['source'] = PY.sub(fix, s)
    ans_blocks = [m.group(1) for c in answer for m in PY.finditer(''.join(c['source']))]
    ref = ans_blocks[0]
    names = [n.name for n in ast.parse(ref).body if isinstance(n, ast.FunctionDef)]
    # 2. the question: header from the reference, outputs of examples from the reference
    ctx = {}; run(setup, ctx); run(defs, ctx); run(ref, ctx)
    for c in question:
        if c['cell_type'] != 'markdown': continue
        s = ''.join(c['source'])
        s = HDR.sub(lambda m: '<!-- header -->\nStart from this header (replace `...` with the body):\n\n'
                    f'```python\n{header_of(ref, names)}```\n<!-- /header -->\n', s)
        def out(m):
            code = m.group(1)
            if code.lstrip().startswith('def '):      # the header block itself
                return m.group(0)
            o = run(code, dict(ctx))
            return f'```python\n{code}```\n' + (f'```text\n{o}```\n' if o else '')
        c['source'] = PY.sub(out, s)
    # 3. Answer fix/variant blocks: output after the block too (context: question run)
    return nb

def check_r3(nb):
    """Each Answer block + each example, WITHOUT the setup cell: same output as generated."""
    cells = nb['cells']
    a = next(i for i, c in enumerate(cells) if ''.join(c['source']).strip() == '#### Answer')
    defs = ''.join(''.join(c['source']) + '\n' for c in cells[1:a] if c['cell_type'] == 'code')
    qmd = ''.join(''.join(c['source']) for c in cells[1:a] if c['cell_type'] == 'markdown')
    pairs = re.findall(r'```python\n((?:(?!```).)*?)```\n```text\n(.*?)```', qmd, re.S)
    ok = True
    for blk in [m.group(1) for c in cells[a+1:] for m in PY.finditer(''.join(c['source']))]:
        for code, want in pairs:
            ns = {}; run(defs, ns)
            got = run(blk + code, ns)        # student pastes the Answer, then the example
            if got != want:
                ok = False; print('R3 FAIL', repr(code), repr(got), repr(want))
    return ok

def md(s): return {'cell_type': 'markdown', 'metadata': {}, 'source': s}
def code(s): return {'cell_type': 'code', 'metadata': {}, 'outputs': [], 'execution_count': None, 'source': s}

nb = {'cells': [
    code('import math\n'),
    md('### Question (medium): write a function\n\nWrite a function called `hypotenuse` that takes the two '
       'shorter sides of a right triangle and returns the longest side, rounded to 2 places.\n\n'
       '<!-- header -->\n\n**Examples**\n\n```python\nprint(hypotenuse(3, 4))\n```\n\n'
       '```python\nprint(hypotenuse(1, 1), hypotenuse(5, 12))\n```\n'),
    code('# Your code here\n'),
    md('#### Answer'),
    md('Use `math.sqrt`:\n\n```python\ndef hypotenuse(a, b):\n    return round(math.sqrt(a ** 2 + b ** 2), 2)\n```\n\n'
       'Another approach, with `math.hypot`:\n\n```python\ndef hypotenuse(a, b):\n    return round(math.hypot(a, b), 2)\n```\n'),
]}
once = sync(json.loads(json.dumps(nb)))
for c in once['cells']: print(f"--- [{c['cell_type']}]\n" + c['source'])
twice = sync(json.loads(json.dumps(once)))
print('idempotent:', once == twice)
print('R3 ok:', check_r3(once))
