"""Design-3 feasibility prototype for write-code questions (read-only on the repo).

For every write-code question of today's six review pages:
  1. TRIM each Answer ```python block the way design 3 would store it:
     - drop trailing lines that are example calls (lines that appear in an Example block),
     - drop leading assignment lines that are an example's inputs (no-signature questions),
     - drop helper defs the question provides ("You may use these ..." blocks become definition cells),
     - drop the run_doctests helper (it becomes a page definition cell).
  2. R3: exec each trimmed block in a namespace that holds ONLY the question's definition cells
     (plus, for no-signature questions, example 1's inputs, which become a definition cell), NOT the
     setup cell. It must not raise.
  3. EXAMPLES: namespace = setup + definitions + trimmed reference block; exec each example block,
     capture stdout, compare with the hand-typed ```text block (what sync would write instead).
  4. HEADER: generate the "Start from this header" block from the reference solution's def lines
     (functions the question does not provide) and compare with the hand-typed block.
Turtle examples: only checked to run (pictures are turtle_images.py's job, already generated).
"""
import ast, contextlib, io, json, os, re, sys, traceback
from pathlib import Path

REPO = Path('/home/yitz/Dropbox/_yrQuarto-master/yrThinkPython')
HERE = Path(__file__).resolve().parent
os.chdir(HERE)                      # words.txt and jupyturtle.py live here
sys.path.insert(0, str(HERE))
FENCE = re.compile(r'```(\w*)[^\n]*\n(.*?)```', re.S)
DOCTEST_HELPER = re.compile(r'from doctest import run_docstring_examples\s*\n|def run_doctests\(func\):\n(?:    .*\n?)+')


def src(c):
    return ''.join(c['source'])


def questions(nb):
    cells, qs, cur = nb['cells'], [], None
    for c in cells:
        s = src(c)
        if c['cell_type'] == 'markdown' and re.match(r'#{1,3} ', s):
            cur = None
            if s.startswith('### Question'):
                cur = {'title': s.split('\n')[0], 'q_md': [], 'defs': [], 'answer': None}
                qs.append(cur)
        if cur is None:
            continue
        if c['cell_type'] == 'markdown' and '<summary>Answer</summary>' in s:
            cur['answer'] = s
        elif c['cell_type'] == 'markdown':
            cur['q_md'].append(s)
        elif c['cell_type'] == 'code' and src(c).strip() != '# Your code here' and 'run_code(' not in s:
            cur['defs'].append(s)
        if c['cell_type'] == 'code' and src(c).strip() == '# Your code here':
            cur['writecode'] = True
            cur['nosig'] = 'no-signature' in c['metadata'].get('tags', [])
    return qs


def setup_code(nb):
    for c in nb['cells']:
        if c['cell_type'] == 'code' and 'setup' in c['metadata'].get('tags', []):
            s = src(c)
            s = re.sub(r"download\('[^']*'\);?", '', s)          # files are already here
            return re.sub(r'def run_code\(code\):\n(?:    .*\n|\n)+', '', s)
    return ''


def examples(md):
    """(python, kind, expected) for each ```python block followed by a text block or turtle img."""
    out = []
    for m in re.finditer(r'```python\n((?:(?!```).)*?)```\s*(?:```text\n(.*?)```|(<img data-turtle))', md, re.S):
        out.append((m.group(1), 'turtle' if m.group(3) else 'text', m.group(2)))
    return out


def provided_helpers(md):
    """Code of ```python blocks after 'You may use' (helpers given as text today)."""
    m = re.search(r'You may use[^\n]*\n\n```python\n(.*?)```', md, re.S)
    return m.group(1) if m else ''


def header_block(md):
    m = re.search(r'Start from this header[^\n]*\n\n```python\n(.*?)```', md, re.S)
    return m.group(1) if m else None


def run(code, ns):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        try:
            exec(compile(code, '<cell>', 'exec'), ns)
            err = None
        except Exception as e:
            err = f'{type(e).__name__}: {e}'
    return buf.getvalue(), err


def def_names(code):
    try:
        return {n.name for n in ast.parse(code).body if isinstance(n, ast.FunctionDef)}
    except SyntaxError:
        return set()


def trim(block, ex_lines, given_names, input_lines):
    tree = ast.parse(block)
    lines = block.split('\n')
    drop = set()
    for node in tree.body:
        span = range(node.lineno - 1, node.end_lineno)
        text = '\n'.join(lines[i] for i in span).strip()
        if isinstance(node, ast.FunctionDef) and node.name in given_names:
            drop.update(span)
        elif isinstance(node, ast.FunctionDef) and node.name == 'run_doctests':
            drop.update(span)
        elif isinstance(node, ast.ImportFrom) and node.module == 'doctest':
            drop.update(span)
        elif not isinstance(node, (ast.FunctionDef, ast.Import, ast.ImportFrom)) and (
                text in ex_lines or text in input_lines):
            drop.update(span)
    kept = [l for i, l in enumerate(lines) if i not in drop]
    return re.sub(r'\n{3,}', '\n\n', '\n'.join(kept)).strip() + '\n', len(drop)


def gen_header(ref, given, prompt=''):
    tree = ast.parse(ref)
    lines = ref.split('\n')
    heads = []
    for n in tree.body:
        if isinstance(n, ast.FunctionDef) and n.name not in given and re.search('`' + n.name + r'\b', prompt):
            first_body = n.body[0].lineno - 1
            heads.append('\n'.join(lines[n.lineno - 1:first_body]).rstrip() + '\n    ...')
    return '\n\n'.join(heads) + '\n'


def main():
    report = []
    totals = dict(q=0, blocks=0, dropped=0, r3_fail=0, ex=0, ex_bad=0, hdr_same=0, hdr_diff=0)
    for ch in ['02', '03', '04', '05', '06', '07']:
        nb = json.loads((REPO / f'yr/chap{ch}_review.ipynb').read_text())
        setup = setup_code(nb)
        page_defs = ''                                     # definition cells so far (page order)
        for q in qs_iter(nb):
            qmd = '\n'.join(q['q_md'])
            for d in q['defs']:
                page_defs += d + '\n'
            if not q.get('writecode') or not q['answer']:
                continue
            totals['q'] += 1
            exs = examples(qmd)
            helpers = provided_helpers(qmd)
            given = def_names(helpers) | def_names('\n'.join(q['defs']))
            ex_lines = {l.strip() for py, _, _ in exs for l in py.split('\n') if l.strip()}
            ex_stmts = set()
            for py, _, _ in exs:
                for node in ast.parse(py).body:
                    ex_stmts.add(ast.get_source_segment(py, node).strip())
            input_lines = set()
            if q.get('nosig'):
                input_lines = {ast.get_source_segment(exs[0][0], n).strip() for n in ast.parse(exs[0][0]).body}
            blocks = [b for lang, b in FENCE.findall(q['answer']) if lang == 'python']
            trimmed = []
            for b in blocks:
                t, nd = trim(b, ex_stmts | ex_lines, given, input_lines)
                trimmed.append(t)
                totals['blocks'] += 1
                totals['dropped'] += nd
            # R3: namespace = question definitions (+ helper definition cell, + example-1 inputs), no setup
            r3_ns_code = '\n'.join(q['defs']) + '\n' + helpers
            if 'run_doctests' in ''.join(blocks):
                r3_ns_code += ('from doctest import run_docstring_examples\n'
                               'def run_doctests(func):\n'
                               '    run_docstring_examples(func, globals(), name=func.__name__)\n')
            if q.get('nosig'):
                r3_ns_code += exs[0][0]
            r3 = []
            for t in trimmed:
                ns = {'__name__': '__main__'}
                run(r3_ns_code, ns)
                out, err = run(t, ns)
                if err:
                    totals['r3_fail'] += 1
                r3.append(err or 'ok')
            # examples generated from the reference (marked block, else first)
            ref_i = 1 if 'scaffolding' in q['answer'] and ch == '06' else 0
            ex_res = []
            for py, kind, expected in exs:
                ns = {'__name__': '__main__'}
                run(setup, ns); run(page_defs, ns); run(helpers, ns)
                body = trimmed[ref_i]
                if q.get('nosig'):
                    run(py, ns)                      # the example's inputs, then the solution
                    out, err = run(body, ns)
                else:
                    run(body, ns)
                    out, err = run(py, ns)
                totals['ex'] += 1
                got = (out + (err + '\n' if err else '')).strip()
                ok = kind == 'turtle' and not err or kind == 'text' and got == expected.strip()
                if not ok:
                    totals['ex_bad'] += 1
                ex_res.append('ok' if ok else f'MISMATCH got={got!r} want={expected!r}')
            hb = header_block(qmd)
            hdr = None
            if hb is not None:
                g = gen_header(trimmed[ref_i], given, qmd)
                same = g.strip() == hb.strip()
                totals['hdr_same' if same else 'hdr_diff'] += 1
                hdr = 'same' if same else f'DIFF generated={g!r} typed={hb!r}'
            report.append(dict(page=ch, q=q['title'], r3=r3, examples=ex_res, header=hdr,
                               trimmed_first=trimmed[0]))
    Path(HERE / 'proto_writecode.json').write_text(json.dumps(report, indent=1))
    for r in report:
        flag = [x for x in r['r3'] if x != 'ok'] + [x for x in r['examples'] if x != 'ok'] + (
            [r['header']] if r['header'] not in (None, 'same') else [])
        print(r['page'], r['q'][:55], 'OK' if not flag else flag)
    print(totals)


qs_iter = questions
if __name__ == '__main__':
    main()
