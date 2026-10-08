"""Build the three Colab smoke-test notebooks for the 'collapsed Answer section' design.

    python make_smoke.py OUTDIR

colab_test_runall.ipynb  collapse metadata variants, Run all past caught errors (A: error output,
                         B: stderr traceback), fallback C (output inside an HTML <details>),
                         visible MARKER cells so the professor can see where Run all stopped.
colab_test_editor.ipynb  editor squiggles (never run it): plain errors, run_code strings,
                         '# type: ignore', a custom %%question cell magic.
colab_test_stop.ipynb    the Stop button during Run all must still stop Run all.
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
from jupyturtle import make_turtle, forward, left


def run_code(code):
    """A: run code (a string) as if it were a cell of its own; an error is shown as a normal
    (red) error output, but the cell itself succeeds, so "Run all" goes on."""
    try:
        ip = get_ipython()
    except NameError:              # plain Python: just run it
        exec(code, globals())
        return
    result = ip.run_cell(code, store_history=False)
    if isinstance(result.error_in_exec, KeyboardInterrupt):
        raise KeyboardInterrupt    # the Stop button still stops "Run all"


def run_code_stderr(code):
    """B (fallback 1): the same, but the traceback is printed on stderr, so there is no
    'error' output at all."""
    ip = get_ipython()
    def to_stderr(etype, evalue, stb):
        print(ip.InteractiveTB.stb2text(stb), file=sys.stderr)
    ip._showtraceback = to_stderr
    try:
        result = ip.run_cell(code, store_history=False)
    finally:
        del ip._showtraceback
    if isinstance(result.error_in_exec, KeyboardInterrupt):
        raise KeyboardInterrupt


def run_hidden(code):
    """C (fallback 2): run code, capture everything it shows (prints, errors, last expression,
    turtle drawing) and show it inside a closed HTML <details> ("Show the output"), so the cell
    can stay visible without giving the answer away."""
    import html, re
    from IPython.utils.capture import capture_output
    from IPython.display import display, HTML
    ip = get_ipython()
    def to_stderr(etype, evalue, stb):
        print(ip.InteractiveTB.stb2text(stb), file=sys.stderr)
    ip._showtraceback = to_stderr
    try:
        with capture_output() as cap:
            result = ip.run_cell(code, store_history=False)
    finally:
        del ip._showtraceback
    ansi = re.compile(r'\x1b\[[0-9;]*m')
    parts = []
    if cap.stdout:
        parts.append('<pre>' + html.escape(cap.stdout) + '</pre>')
    rich = {}
    for k, o in enumerate(cap.outputs):          # keep the last version of each display (turtle updates)
        key = (o.transient or {}).get('display_id', k) if hasattr(o, 'transient') else k
        rich[key] = o.data
    for data in rich.values():
        if 'text/html' in data:
            parts.append(data['text/html'])
        elif 'text/plain' in data:
            parts.append('<pre>' + html.escape(data['text/plain']) + '</pre>')
    if cap.stderr:
        parts.append('<pre style="color:#c00">' + html.escape(ansi.sub('', cap.stderr)) + '</pre>')
    display(HTML('<details><summary><b>Show the output</b></summary>' + ''.join(parts) + '</details>'))
    if isinstance(result.error_in_exec, KeyboardInterrupt):
        raise KeyboardInterrupt
'''

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


def code(s, tags=None):
    c = nbf.v4.new_code_cell(s)
    c.id = fid()
    if tags:
        c.metadata['tags'] = tags
    return c


def answer_heading(config, collapsed):
    """'#### Answer' heading saved collapsed in one of three ways (see Part 1)."""
    c = md('#### Answer')
    if config in ('full', 'jp-only'):
        c.metadata['jp-MarkdownHeadingCollapsed'] = True
    if config == 'full':
        c.metadata['id'] = c.id
    if config in ('full', 'toplevel-only'):
        collapsed.append(c.id)
    return c


def question(n, title, qcode, answer_md, run_src, collapsed, config='full', marker=True):
    cells = [md(f'### Test {n}: {title}'),
             md(f'```python\n{qcode}\n```', tags=['question-code']),
             answer_heading(config, collapsed),
             md(answer_md),
             code(run_src)]
    if marker:
        cells.append(md(f'#### Marker {n}'))
        cells.append(code(f"print('MARKER {n}: Run all got past Test {n}')"))
    return cells


def save(name, cells, collapsed):
    nb = nbf.v4.new_notebook(cells=cells)
    nb.metadata = {'colab': {'collapsed_sections': collapsed},
                   'kernelspec': {'display_name': 'Python 3 (ipykernel)', 'language': 'python', 'name': 'python3'},
                   'language_info': {'name': 'python'}}
    nbf.validate(nb)
    nbf.write(nb, f'{OUT}/{name}')


# ---------------------------------------------------------------- colab_test_runall.ipynb
collapsed = []
cells = [md('''# Colab smoke test 1: collapsed Answers and Run all

Open this notebook **from GitHub** (the colab.research.google.com/github/... link), not from a downloaded copy.
Follow the numbered checks in the professor's checklist (R1 to R12). Do not expand anything before check R1.

Each test has a question (code shown as text), then an **Answer** heading whose section holds the expected output
and a code cell that runs the question's code. After each test there is a visible **MARKER** cell: after
**Runtime > Run all**, the last MARKER that shows output tells how far Run all got.'''),
         md('## Setup'),
         code(SETUP, tags=['setup']),
         md('## Part 1: which collapse metadata does Colab honour?\n\n'
            'Test 1 is saved collapsed in all three ways (Colab list + cell metadata.id + JupyterLab key). '
            'Test 2 only through the Colab list with the top-level cell id (no metadata.id). '
            'Test 3 only with the JupyterLab key.')]
cells += question(1, 'collapsed: full metadata', "print('LIVE 1')", 'SECRET 1: the output is\n\n```text\nLIVE 1\n```',
                  "print('LIVE 1')", collapsed, 'full')
cells += question(2, 'collapsed: Colab list + top-level id only', "print('LIVE 2')",
                  'SECRET 2: the output is\n\n```text\nLIVE 2\n```', "print('LIVE 2')", collapsed, 'toplevel-only')
cells += question(3, 'collapsed: JupyterLab key only', "print('LIVE 3')", 'SECRET 3: the output is\n\n```text\nLIVE 3\n```',
                  "print('LIVE 3')", collapsed, 'jp-only')
cells.append(md('## Part 2: Run all past errors\n\n'
                'Tests 4 and 5 (variant B: traceback printed on stderr) come first, then tests 6 and 7 (variant A: normal red '
                'error output). If Run all stops, the last MARKER with output tells which variant Colab tolerates.'))
cells += question(4, 'B: syntax error, traceback on stderr', "x = 5\nif x = 5:\n    print('five')",
                  "```text\nSyntaxError: invalid syntax. Maybe you meant '==' or ':=' instead of '='?\n```",
                  'run_code_stderr("""\nx = 5\nif x = 5:\n    print(\'five\')\n""")', collapsed)
cells += question(5, 'B: runtime error after a print, traceback on stderr', "print('start')\nprint(total)",
                  "```text\nstart\n```\n\n```text\nNameError: name 'total' is not defined\n```",
                  'run_code_stderr("""\nprint(\'start\')\nprint(total)\n""")', collapsed)
cells += question(6, 'A: syntax error, normal error output', "x = 5\nif x > 0\n    print('positive')",
                  "```text\nSyntaxError: expected ':'\n```", 'run_code("""\nx = 5\nif x > 0\n    print(\'positive\')\n""")',
                  collapsed)
cells += question(7, 'A: runtime error inside a function (traceback order), normal error output',
                  "def outer(s):\n    return inner(s)\n\ndef inner(s):\n    return s + 1\n\nouter('hi')",
                  '```text\nTypeError: can only concatenate str (not "int") to str\n```',
                  'run_code("""\ndef outer(s):\n    return inner(s)\n\ndef inner(s):\n    return s + 1\n\nouter(\'hi\')\n""")',
                  collapsed)
cells += question(8, 'A: an import that fails (Colab adds a note)', "print('start')\nimport no_such_module",
                  "```text\nstart\n```\n\n```text\nModuleNotFoundError: No module named 'no_such_module'\n```",
                  'run_code("""\nprint(\'start\')\nimport no_such_module\n""")', collapsed)
cells.append(md('## Part 3: outputs that are not errors'))
cells += question(9, 'last expression of a cell (plain cell)', 'price = 4\nprice * 3', '```text\n12\n```',
                  'price = 4\nprice * 3', collapsed)
cells += question(10, 'turtle drawing (plain cell)', 'make_turtle()\nfor i in range(4):\n    forward(50)\n    left(90)',
                  'A square.', 'make_turtle()\nfor i in range(4):\n    forward(50)\n    left(90)', collapsed)
cells.append(md('## Part 4: fallback C, output inside a closed box\n\n'
                'These cells are **not** in a collapsed section. Their output should be a closed "Show the output" box.'))
cells.append(md('### Test 11: fallback C with an error and a drawing'))
cells.append(code('run_hidden("""\nprint(\'start\')\nmake_turtle()\nforward(80)\nprint(10 / 0)\n""")'))
cells.append(code('run_hidden("""\nprice = 4\nprice * 3\n""")'))
cells.append(md('#### Marker 11'))
cells.append(code("print('MARKER 11: Run all got past Test 11')"))
cells.append(md('## End\n\nThis section is not collapsed. If Run all reached the end, the next cell shows `END`.'))
cells.append(code("print('END: Run all reached the last cell')"))
save('colab_test_runall.ipynb', cells, collapsed)

# ---------------------------------------------------------------- colab_test_editor.ipynb
cells = [md('''# Colab smoke test 2: the editor's red underlines

**Do not run this notebook.** Just look at each code cell (click into it and wait a few seconds; the checker
needs a connected runtime, so first connect with the Connect button). Do this twice: with the default settings,
and with **Tools > Settings > Editor > Code diagnostics** set to **Syntax and type checking**.
For each cell, note: underlined or not, and is the code coloured (syntax highlighting)?'''),
         md('### E1: plain syntax error (expected: underlined)'), code("x = 5\nif x = 5:\n    print('five')"),
         md('### E2: plain undefined name (underlined on default settings?)'), code('print(total_xyz)'),
         md('### E3: plain wrong call (underlined only with type checking?)'), code('import math\nmath.pow(2)'),
         md('### E4: the same mistakes inside run_code (expected: no underline)'),
         code('run_code("""\nx = 5\nif x = 5:\n    print(\'five\')\nprint(total_xyz)\n""")'),
         md('### E5: "# type: ignore" as the first line (underlined?)'), code("# type: ignore\nx = 5\nif x = 5:\n    print('five')"),
         md('### E6: a custom cell magic (coloured? underlined? a warning about an unknown magic?)'),
         code("%%question q8a\nx = 5\nif x = 5:\n    print('five')"),
         md('### E7: an ordinary correct cell after the others (expected: not underlined)'), code('y = 7\nprint(y)')]
cells.insert(1, code('def run_code(code):\n    """Defined here only so the checker knows the name (this notebook is never run)."""\n'
                     '    exec(code, globals())'))
save('colab_test_editor.ipynb', cells, [])

# ---------------------------------------------------------------- colab_test_stop.ipynb
collapsed = []
cells = [md('''# Colab smoke test 3: the Stop button during Run all

Use **Runtime > Run all**. While Test 1 is running (it takes 60 seconds; open its Answer to watch it, or just wait
10 seconds), press **Runtime > Interrupt execution** (or the stop square). Expected: Run all stops, so the
cell under **End** does **not** show `END`.'''),
         code(SETUP, tags=['setup'])]
cells += question(1, 'a slow cell run by run_code', "import time\nfor i in range(60):\n    time.sleep(1)\nprint('finished')",
                  '```text\nfinished\n```', 'run_code("""\nimport time\nfor i in range(60):\n    time.sleep(1)\nprint(\'finished\')\n""")',
                  collapsed, marker=False)
cells.append(md('## End'))
cells.append(code("print('END: Run all was NOT stopped')"))
save('colab_test_stop.ipynb', cells, collapsed)
print('wrote 3 notebooks to', OUT)
