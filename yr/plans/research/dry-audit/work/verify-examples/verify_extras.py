"""Extra checks beyond question examples:
  1. Answer ```python blocks followed by "That displays:" ```text (chap02 Q4, Q15): run and compare.
  2. chap07 Q14 fixed count_e and Q17 count_doubles: doctests in the Answer pass (run_doctests prints nothing).
  3. chap07 Q14 question cell: its doctest failure report vs the Answer's text block.
  4. Answer turtle pictures of predict questions (no python block above the img): redraw from the
     question's last code cell and compare with the stored PNG.
Usage: python verify_extras.py yr/chap0*_review.ipynb
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import nbformat as nbf
from verify_examples import groups_of, is_answer, run_cells, png_of, CACHE, WORDS, PY
import shutil, tempfile

IMG = re.compile(r'<img\b[^>]*\bdata-turtle[^>]*>')


def run(cells, svg=False):
    work = Path(tempfile.mkdtemp(prefix='vx_'))
    shutil.copy(CACHE, work); shutil.copy(WORDS, work)
    try:
        return run_cells(cells, work, svg)
    finally:
        shutil.rmtree(work, ignore_errors=True)


nodelay = 'import jupyturtle as _jt; _jt.TURTLE_DELAY = 0'
for p in sys.argv[1:]:
    nb = nbf.read(p, 4)
    setup = '\n\n'.join(c.source for c in nb.cells if c.cell_type == 'code' and 'setup' in c.metadata.get('tags', []))
    for g in groups_of(nb.cells):
        title = g[0].source.lstrip().splitlines()[0].lstrip('# ')
        qcode = [c.source for c in g if c.cell_type == 'code' and c.source.strip() != '# Your code here']
        for a in [c for c in g if is_answer(c)]:
            for m in re.finditer(r'```python\n((?:(?!```).)*?)```\s*That displays:\s*```text\n((?:(?!```).)*?)```', a.source, re.S):
                out, errs, early, _ = run([setup, m.group(1)])
                got = (out + '\n'.join(errs)).strip()
                print('THAT-DISPLAYS', p, title, 'OK' if got == m.group(2).strip() else f'MISMATCH got {got!r} expected {m.group(2)!r}')
            if '>>>' in a.source:
                for k, b in enumerate(PY.findall(a.source)):
                    out, errs, early, _ = run([setup, b])
                    print('DOCTEST-ANSWER', p, title, f'block {k}: stdout={out!r} errors={errs}')
            for m in IMG.finditer(a.source):
                if PY.findall(a.source[:m.start()]):
                    continue
                out, errs, early, svg = run([setup, nodelay] + qcode, svg=True)
                stored = re.search(r'base64,([^"]+)"', m.group(0)).group(1)
                print('PREDICT-IMG', p, title, 'identical' if svg and png_of(svg) == stored else 'DIFFERS', errs)
        if '>>>' in ''.join(qcode):
            out, errs, early, _ = run([setup] + qcode)
            ans = ''.join(c.source for c in g if is_answer(c))
            print('DOCTEST-QUESTION', p, title, repr(out))
            print('   answer text block present verbatim:', out.strip() in ans)
