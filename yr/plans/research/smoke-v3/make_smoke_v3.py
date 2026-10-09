"""Build the v3 Colab smoke-test notebook (plan Step 2, checklist Part B), 2026-10-09.

    python make_smoke_v3.py OUTDIR      -> OUTDIR/colab_smoke_v3.ipynb

Only what v1, Part A2 and the 2026-10-09 tests leave open:
  Tests 1-3  which collapse metadata Colab needs (all three / Colab list only / JupyterLab key only)
  Tests 4-6  variant B (chosen): two failing imports (ch02 Q14a; Colab's NOTE and the ColabTraceback unwrap,
             and the handler still working for the second import), a syntax error, a deep recursion
  Test 7     a write-code question in the v3 layout: a definition cell, generated regions (header, example
             output), a trimmed Answer with generated imports and a "Then try" line; after Run all its block
             must run when copied into a new cell (goal 11), and a name-reuse fix keeps its input line (E10)
Manual checks (checklist): clicking a run cell before the helper has run (B's setup dependency), and whether
Shift+Enter / Down arrow open a closed Answer (D10). A visible MARKER cell follows each test; END at the end.
"""
import secrets
import sys

import nbformat as nbf

OUT = sys.argv[1]

SETUP = r'''import sys, IPython, ipykernel
print("Python", sys.version.split()[0], "| IPython", IPython.__version__, "| ipykernel", ipykernel.__version__)

from os.path import exists
from urllib.request import urlretrieve
if not exists('jupyturtle.py'):
    urlretrieve('https://github.com/ramalho/jupyturtle/releases/download/2024-03/jupyturtle.py', 'jupyturtle.py')
from jupyturtle import make_turtle, forward, left'''

HELPER = r'''# @title Helper for the Answers
def run_code(code):
    """Run code as a cell of its own; print an error's traceback as text instead of raising."""
    import sys
    from IPython import get_ipython
    ip = get_ipython()
    if ip is None:
        exec(code, globals())
        return
    def to_stderr(etype, evalue, stb):
        stb = getattr(stb, 'stb', stb)           # Colab passes a ColabTraceback for import errors
        print(ip.InteractiveTB.stb2text(stb), file=sys.stderr)
    ip._showtraceback = to_stderr
    try:
        ip.run_cell(code, store_history=False)
    finally:
        del ip._showtraceback'''

used = set()


def fid():
    while True:
        i = secrets.token_hex(4)
        if i not in used:
            used.add(i)
            return i


def md(s, **meta):
    c = nbf.v4.new_markdown_cell(s)
    c.id = fid()
    c.metadata.update(meta)
    return c


def code(s, tags=None, hidden=False):
    c = nbf.v4.new_code_cell(s)
    c.id = fid()
    if tags:
        c.metadata['tags'] = tags
    if hidden:
        c.metadata['cellView'] = 'form'
        c.metadata['jupyter'] = {'source_hidden': True}
    return c


def answer_heading(config, collapsed):
    c = md('#### Answer')
    if config in ('full', 'jp-only'):
        c.metadata['jp-MarkdownHeadingCollapsed'] = True
    if config == 'full':
        c.metadata['id'] = c.id
    if config in ('full', 'toplevel-only'):
        collapsed.append(c.id)
    return c


def run_cell(title, src, wrapped):
    body = f'run_code(\nr"""\n{src}\n""")' if wrapped else src
    return code(f'# @title {title}\n{body}', hidden=True)


def marker(n):
    return [md(f'#### Marker {n}'), code(f"print('MARKER {n}: Run all got past Test {n}')")]


def predict(n, title, qcode, answer_md, wrapped, collapsed, config='full'):
    return [md(f'### Test {n}: {title}\n\nPredict, then open the Answer.'),
            md(f'~~~python\n{qcode}\n~~~'),
            answer_heading(config, collapsed),
            md(answer_md),
            run_cell(f'Output of Test {n}', qcode, wrapped)] + marker(n)


collapsed = []
cells = [md('''# Colab smoke test (v3): collapsed Answers, variant B errors, copy-and-run

Open this notebook **from GitHub** (the colab.research.google.com/github/... link). Don't expand anything before
check B1. Each test is followed by a visible **MARKER** cell; after **Runtime > Run all**, the MARKERs that show
output tell how far Run all got, and the last cell prints END.'''),
         md('## Setup'),
         code(SETUP, tags=['setup']),
         code(HELPER, tags=['setup'], hidden=True),
         md('## Part 1: which collapse metadata does Colab honour?\n\n'
            'Test 1: all three markers. Test 2: only the Colab list. Test 3: only the JupyterLab key.')]
cells += predict(1, 'collapsed: full metadata', "print('LIVE 1')", 'SECRET 1.', False, collapsed, 'full')
cells += predict(2, 'collapsed: Colab list only', "print('LIVE 2')", 'SECRET 2.', False, collapsed, 'toplevel-only')
cells += predict(3, 'collapsed: JupyterLab key only', "print('LIVE 3')", 'SECRET 3.', False, collapsed, 'jp-only')
cells.append(md('## Part 2: variant B errors (traceback printed as text)'))
cells += predict(4, 'B: a failing import, then a second one (ch02 Q14a)', "print('start')\nimport no_such_module",
                 'SECRET 4: `start`, then a `ModuleNotFoundError` as plain text, with Colab\'s NOTE.', True, collapsed)
cells += [md('### Test 4b: the second failing import must also be plain text'),
          md('~~~python\nimport another_missing_module\n~~~'),
          answer_heading('full', collapsed),
          md('SECRET 4b.'),
          run_cell('Output of Test 4b', 'import another_missing_module', True)] + marker('4b')
cells += predict(5, 'B: a syntax error', "x = 5\nif x = 5:\n    print('five')",
                 'SECRET 5: a `SyntaxError`, as plain text, with the code line and a caret.', True, collapsed)
cells += predict(6, 'B: infinite recursion (ch05 Q14)',
                 "def countdown_by_two(n):\n    if n == 0:\n        print('Blastoff!')\n    else:\n        countdown_by_two(n - 2)\n\ncountdown_by_two(5)",
                 'SECRET 6: a `RecursionError`, as plain text, short ("last 1 frames repeated").', True, collapsed)
cells.append(md('## Part 3: a write-code question in the v3 layout (goal 11, E2-E6, E10, E17, E19)'))
cells += [md('### Test 7: write a function\n\nRun this cell to define `square`.'),
          code('def square(length):\n    for i in range(4):\n        forward(length)\n        left(90)'),
          md('Write a function called `double_square` that takes `length` and draws two squares, the second one '
             'twice as big, using `square`.\n\n<!-- begin generated: header -->\nStart from this header (replace `...` '
             'with the body):\n\n```python\ndef double_square(length):\n    ...\n```\n<!-- end generated: header -->\n\n'
             '**Examples**\n\n```python\nmake_turtle()\ndouble_square(30)\n```\n<!-- begin generated: example -->\n'
             'A square of side 30 and one of side 60.\n<!-- end generated: example -->'),
          code('# Your code here'),
          answer_heading('full', collapsed),
          md('<!-- generated imports: 1 -->\n```python\nfrom jupyturtle import make_turtle\n\n'
             'def double_square(length):\n    square(length)\n    square(2 * length)\n```\n\n'
             '<!-- begin generated: then-try -->\nThen try: `make_turtle()` and `double_square(30)`.\n'
             '<!-- end generated: then-try -->\n\nSECRET 7.')] + marker(7)
cells += [md('### Test 8: a fix that keeps its input line (E10)'),
          md('~~~python\nprice = 4\nprint(price * 2)\n~~~'),
          answer_heading('full', collapsed),
          md('SECRET 8. A later question reassigns `price`, so the fix keeps its input line:\n\n'
             '```python\nprice = 4\nprint(price * 3)\n```'),
          run_cell('Output of Test 8', 'price = 4\nprint(price * 2)', False),
          md('### Test 9: a later question\'s definition cell reassigns `price`\n\nRun this cell to assign `price`.'),
          code("price = '19.99'")] + marker(9)
cells.append(md('## End\n\nIf Run all reached the end, the next cell shows `END`.'))
cells.append(code("print('END: Run all reached the last cell')"))

nb = nbf.v4.new_notebook(cells=cells)
nb.metadata = {'colab': {'collapsed_sections': collapsed},
               'kernelspec': {'display_name': 'Python 3 (ipykernel)', 'language': 'python', 'name': 'python3'},
               'language_info': {'name': 'python'}}
nbf.validate(nb)
nbf.write(nb, f'{OUT}/colab_smoke_v3.ipynb')
print('wrote', f'{OUT}/colab_smoke_v3.ipynb')
