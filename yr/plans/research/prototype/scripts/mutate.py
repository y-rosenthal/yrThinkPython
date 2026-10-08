"""Make broken copies of the converted notebook, run the adapted check on each, and show what it reports."""
import subprocess, sys, json, copy
import nbformat as nbf
SRC = 'repo/yr/chap05_review.ipynb'
nb0 = nbf.read(SRC, 4)
def find(pred):
    return next(i for i, c in enumerate(nb0.cells) if pred(c))
def src_has(s): return lambda c: s in c.source
muts = {
 'wrong expected output (Q1)': lambda nb: setattr(nb.cells[find(src_has('135 minutes is 2 hours'))], 'source', nb.cells[find(src_has('135 minutes is 2 hours'))].source.replace('2 15\n', '2 16\n', 1)),
 'question block edited, Answer cell not (Q8 b)': lambda nb: setattr(nb.cells[find(src_has('### Question 8'))], 'source', nb.cells[find(src_has('### Question 8'))].source.replace('if x > 0\n', 'if x > 1\n')),
 'error without run_code (Q8 a)': lambda nb: setattr(nb.cells[find(lambda c: c.cell_type == 'code' and c.source.startswith('run_code("""\nx = 5\nif x = 5'))], 'source', "x = 5\nif x = 5:\n    print('five')"),
 'wrong-call question without 2 correct calls (Q14)': lambda nb: setattr(nb.cells[find(src_has('Two correct ways to call it'))], 'source', 'What happens with this call? How would you fix the function?\n\n```python\ncountdown_by_two(5)\n```'),
 'Answer code cell removed (Q1)': lambda nb: nb.cells.pop(find(lambda c: c.cell_type == 'code' and c.source.startswith('minutes = 135'))),
 'Answer heading not collapsed for JupyterLab (Q2)': lambda nb: nb.cells[find(lambda c: c.get('id') == '61b70332')].metadata.pop('jp-MarkdownHeadingCollapsed'),
 'definition cell prints (Q14)': lambda nb: setattr(nb.cells[find(src_has('def countdown_by_two(n):\n    if n == 0'))], 'source', nb.cells[find(src_has('def countdown_by_two(n):\n    if n == 0'))].source + "\nprint('defined')"),
 'answer block not standalone (Q4)': lambda nb: setattr(nb.cells[find(src_has('A chained conditional, with one branch'))], 'source', nb.cells[find(src_has('A chained conditional, with one branch'))].source.replace('def sign(x):\n    if x > 0', 'def sgn(x):\n    if x > 0')),
 'error text missing (Q14)': lambda nb: setattr(nb.cells[find(src_has('RecursionError: maximum'))], 'source', nb.cells[find(src_has('RecursionError: maximum'))].source.replace('RecursionError: maximum recursion depth exceeded', 'RecursionError')),
 'credits without heading': lambda nb: setattr(nb.cells[-1], 'source', nb.cells[-1].source.replace('## Credits\n\n', '')),
}
for name, f in muts.items():
    nb = copy.deepcopy(nb0)
    f(nb)
    nbf.write(nb, 'out/mut.ipynb')
    r = subprocess.run([sys.executable, 'repo/yr/tools/check_review.py', 'out/mut.ipynb', '/root/.venvs/yrThinkPython/yr-cache/jupyturtle.py'],
                       capture_output=True, text=True)
    lines = [l for l in r.stdout.splitlines() if l.startswith('  -') or l.startswith('OK')]
    print(f'== {name}: exit {r.returncode}'); print('\n'.join('   ' + l[:230] for l in lines))
