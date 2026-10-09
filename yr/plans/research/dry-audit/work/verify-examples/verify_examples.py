"""Verify hand-typed example outputs on the review pages by running the code.

For every question on yr/chapNN_review.ipynb:
  * every ```python block in the QUESTION markdown that is followed by a ```text block or a
    data-turtle <img> is an "example" (write-code examples, "Two correct ways to call it",
    help() examples). It runs in a fresh kernel after: the setup cell, the Answer's solution
    block (write-code questions only; each solution block in turn, the first is the "official"
    one), and the question's code cells that come before the example's markdown cell.
    stdout (+ the error line if it raises) is compared with the ```text block.
    Turtle examples: the drawing's SVG is rendered like turtle_images.py does and compared with
    the stored PNG.
  * write-code questions without a header (tag no-signature, chap02): the example block assigns
    the input variables and the solution runs after it, minus its own leading assignments.
  * extra: every ```python block in an ANSWER that is followed by a ```text block is run
    (setup + question code cells + that block) and compared.

Usage: python verify_examples.py OUTDIR yr/chap0*_review.ipynb
"""
import base64
import json
import re
import shutil
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import cairosvg
import nbformat as nbf
from nbclient import NotebookClient

PY = re.compile(r'```python\n(.*?)```', re.S)
PAIR = re.compile(r'```python\n((?:(?!```).)*?)```\s*(?:```text\n((?:(?!```).)*?)```|(<img\b[^>]*\bdata-turtle[^>]*>))', re.S)
ANSI = re.compile(r'\x1b\[[0-9;]*m')
PLACEHOLDER = '# Your code here'
CACHE = Path.home() / '.venvs/yrThinkPython/yr-cache/jupyturtle.py'
WORDS = Path(__file__).resolve().parent.parent / 'chap07-audit/words.txt'


def is_answer(c):
    return c.cell_type == 'markdown' and re.match(r'\s*<details>\s*<summary>Answer</summary>', c.source)


def groups_of(cells):
    groups, cur = [], None
    for c in cells:
        if c.cell_type == 'markdown' and c.source.lstrip().startswith('### '):
            cur = []
            groups.append(cur)
        elif c.cell_type == 'markdown' and c.source.lstrip().startswith(('# ', '## ')):
            cur = None
        if cur is not None:
            cur.append(c)
    return groups


def error_line(o):
    v = ANSI.sub('', o.get('evalue', ''))
    v = re.sub(r' \([^()]*, line \d+\)$', '', v)
    return f"{o['ename']}: {v}"


def run_cells(sources, workdir, want_svg):
    """Run sources as cells in a fresh kernel; return (stdout, errors, svg) of the LAST cell."""
    cells = [nbf.v4.new_code_cell(s) for s in sources]
    if want_svg:
        cells.append(nbf.v4.new_code_cell('import jupyturtle as _jt\nprint(_jt.get_turtle().get_SVG())'))
    nb = nbf.v4.new_notebook(cells=cells)
    nb.metadata['kernelspec'] = {'name': 'python3', 'display_name': 'Python 3', 'language': 'python'}
    NotebookClient(nb, timeout=120, kernel_name='python3', allow_errors=True,
                   resources={'metadata': {'path': str(workdir)}}).execute()
    target = cells[-2] if want_svg else cells[-1]
    out = ''.join(o.get('text', '') for o in target.outputs if o.output_type == 'stream' and o.name == 'stdout')
    errs = [error_line(o) for o in target.outputs if o.output_type == 'error']
    early = [(i, error_line(o)) for i, c in enumerate(cells[:-2 if want_svg else -1])
             for o in c.outputs if o.output_type == 'error']
    svg = None
    if want_svg:
        svg = ''.join(o.get('text', '') for o in cells[-1].outputs if o.output_type == 'stream').strip()
    return out, errs, early, svg


def png_of(svg):
    svg = svg.replace('<svg ', '<svg xmlns="http://www.w3.org/2000/svg" ', 1)
    return base64.b64encode(cairosvg.svg2png(bytestring=svg.encode(), scale=2)).decode()


def strip_leading_assignments(block):
    lines = block.split('\n')
    i = 0
    while i < len(lines) and re.match(r'^\w+ = .*$', lines[i]):
        i += 1
    return '\n'.join(lines[i:]).lstrip('\n')


def plan(path):
    nb = nbf.read(path, nbf.NO_CONVERT)
    setup = '\n\n'.join(c.source for c in nb.cells if c.cell_type == 'code' and 'setup' in c.metadata.get('tags', []))
    nodelay = 'try:\n    import jupyturtle as _jt; _jt.TURTLE_DELAY = 0\nexcept ImportError:\n    pass'
    tests = []
    for g in groups_of(nb.cells):
        title = g[0].source.lstrip().splitlines()[0].lstrip('# ')
        answers = [c for c in g if is_answer(c)]
        sol_blocks = [b for a in answers for b in PY.findall(a.source)]
        placeholders = [c for c in g if c.cell_type == 'code' and c.source.strip() == PLACEHOLDER]
        nosig = any('no-signature' in c.metadata.get('tags', []) for c in placeholders)
        write_code = bool(placeholders)
        before = []  # question code cells seen so far
        for c in g:
            if c.cell_type == 'code':
                if c.source.strip() != PLACEHOLDER:
                    before.append(c.source)
                continue
            if c.cell_type != 'markdown':
                continue
            if is_answer(c):
                # extra: answer python blocks followed by text
                for k, m in enumerate(PAIR.finditer(c.source)):
                    code, text, img = m.groups()
                    if text is None:
                        continue
                    tests.append(dict(page=path.name, q=title, kind='answer-block-output', sol=None,
                                      cells=[setup, nodelay] + before + [code], expect=text, img=None, code=code))
                continue
            for m in PAIR.finditer(c.source):
                code, text, img = m.groups()
                kind = 'write-code example' if write_code else 'correct-call/example'
                if 'help(' in code:
                    kind += ' (help)'
                if write_code:
                    choices = list(enumerate(sol_blocks)) or [(None, None)]
                else:
                    choices = [(None, None)]
                for si, sol in choices:
                    if write_code and nosig:
                        cells = [setup, nodelay] + before + [code + '\n' + strip_leading_assignments(sol)]
                    else:
                        cells = [setup, nodelay] + ([sol] if sol else []) + before + [code]
                    tests.append(dict(page=path.name, q=title, kind=kind, sol=si, cells=cells,
                                      expect=text, img=img, code=code))
    return tests


def execute(t):
    work = Path(tempfile.mkdtemp(prefix='vex_'))
    shutil.copy(CACHE, work)
    shutil.copy(WORDS, work)
    try:
        out, errs, early, svg = run_cells(t['cells'], work, want_svg=t['img'] is not None)
    finally:
        shutil.rmtree(work, ignore_errors=True)
    r = dict(page=t['page'], q=t['q'], kind=t['kind'], sol=t['sol'], code=t['code'].strip(),
             early_errors=early, errors=errs)
    if t['img'] is None:
        got = (out.rstrip('\n') + ('\n' if out.strip() and errs else '') + '\n'.join(errs)).strip()
        exp = t['expect'].strip()
        r.update(expected=exp, got=got, ok=(got == exp))
    else:
        stored = re.search(r'base64,([^"]+)"', t['img'])
        same = None
        if svg and stored:
            same = png_of(svg) == stored.group(1)
        r.update(expected='<turtle img>', got=('ran, image identical' if same else 'ran, image DIFFERS' if same is False else 'no svg'),
                 ok=(not errs), image_same=same)
    return r


def main(outdir, paths):
    tests = [t for p in paths for t in plan(Path(p))]
    print(f'{len(tests)} tests', flush=True)
    with ThreadPoolExecutor(6) as ex:
        results = list(ex.map(execute, tests))
    Path(outdir, 'results.json').write_text(json.dumps(results, indent=1))
    for r in results:
        flag = 'OK ' if r['ok'] and r.get('image_same', True) is not False else 'BAD'
        print(f"{flag} {r['page']} | {r['q']} | {r['kind']} | sol={r['sol']} | {r['code'][:50]!r}")
        if flag == 'BAD' or r['early_errors']:
            print('    expected:', repr(r['expected']))
            print('    got:     ', repr(r['got']))
            if r['early_errors']:
                print('    earlier-cell errors:', r['early_errors'])


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2:])
