"""Build the Colab smoke-test notebooks for the 'collapsed Answer section' design."""
import secrets, sys
import nbformat as nbf
out = sys.argv[1]
RUN_CODE = r'''def run_code(code):
    """Run code (a string) as if it were a cell of its own: show its output, and its error if it
    raises, without stopping "Run all". (Code in a string is also not underlined by Colab's editor.)"""
    try:
        ip = get_ipython()
    except NameError:              # plain Python: just run it
        exec(code, globals())
        return
    result = ip.run_cell(code, store_history=False)
    if isinstance(result.error_in_exec, KeyboardInterrupt):
        raise KeyboardInterrupt    # the Stop button still stops "Run all"


def run_code_stderr(code):
    """Fallback variant: same, but the traceback is printed to stderr (no 'error' output at all)."""
    ip = get_ipython()
    def to_stderr(etype, evalue, stb):
        print(ip.InteractiveTB.stb2text(stb), file=sys.stderr)
    ip._showtraceback = to_stderr
    try:
        result = ip.run_cell(code, store_history=False)
    finally:
        del ip._showtraceback
    if isinstance(result.error_in_exec, KeyboardInterrupt):
        raise KeyboardInterrupt'''
used = set()
def fid():
    while True:
        i = secrets.token_hex(4)
        if i not in used:
            used.add(i); return i
def md(s, **meta):
    c = nbf.v4.new_markdown_cell(s); c.id = fid(); c.metadata.update(meta); return c
def code(s):
    c = nbf.v4.new_code_cell(s); c.id = fid(); return c
def heading():
    c = md('#### Answer'); c.metadata['id'] = c.id; c.metadata['jp-MarkdownHeadingCollapsed'] = True; return c
def q(title, prompt, qcode, answer_md, run_src):
    h = heading()
    return [md(f'### {title}\n\n{prompt}'), md(f'```python\n{qcode}\n```', tags=['question-code']), h,
            md(answer_md), code(run_src)], h.id

def build(name, intro, questions, end_code):
    cells = [md(intro), code('import sys, IPython, ipykernel\nprint("Python", sys.version.split()[0], "| IPython", IPython.__version__, "| ipykernel", ipykernel.__version__)\n\n'
                             "from os.path import exists\nfrom urllib.request import urlretrieve\n"
                             "if not exists('jupyturtle.py'):\n    urlretrieve('https://github.com/ramalho/jupyturtle/releases/download/2024-03/jupyturtle.py', 'jupyturtle.py')\n"
                             "from jupyturtle import make_turtle, forward, left\n\n" + RUN_CODE)]
    cells[1].metadata['tags'] = ['setup']
    ids = []
    for args in questions:
        cs, i = q(*args); cells += cs; ids.append(i)
    cells += [md('## End\n\nThis section is not collapsed. If **Run all** reached the end, the next cell shows `END`.'), code(end_code)]
    nb = nbf.v4.new_notebook(cells=cells)
    nb.metadata = {'colab': {'collapsed_sections': ids},
                   'kernelspec': {'display_name': 'Python 3 (ipykernel)', 'language': 'python', 'name': 'python3'},
                   'language_info': {'name': 'python'}}
    nbf.validate(nb); nbf.write(nb, f'{out}/{name}')

build('colab_runall_test.ipynb',
 '# Colab test: collapsed Answers and Run all\n\nOpen this from GitHub in Colab. **Before running anything**, check that every **Answer** is collapsed. '
 'Then use **Runtime > Run all**. The B tests (stderr tracebacks) come first and the A tests (normal error outputs) after them, '
 'so if Run all stops, the last cell that ran tells which variant Colab tolerates.',
 [('Test 1 (B): syntax error, traceback printed to stderr', 'What happens?', "x = 5\nif x = 5:\n    print('five')",
   '```text\nSyntaxError: invalid syntax. Maybe you meant \'==\' or \':=\' instead of \'=\'?\n```', 'run_code_stderr("""\nx = 5\nif x = 5:\n    print(\'five\')\n""")'),
  ('Test 2 (B): runtime error, traceback printed to stderr', 'What is displayed?', "print('start')\nprint(total)",
   "```text\nstart\n```\n\n```text\nNameError: name 'total' is not defined\n```", 'run_code_stderr("""\nprint(\'start\')\nprint(total)\n""")'),
  ('Test 3: plain print (no error)', 'What is displayed?', 'print(7 // 2, 7 % 2)', '```text\n3 1\n```', 'print(7 // 2, 7 % 2)'),
  ('Test 4: last expression of a cell', 'What is displayed?', 'price = 4\nprice * 2\nprice * 3', '```text\n12\n```', 'price = 4\nprice * 2\nprice * 3'),
  ('Test 5: turtle drawing', 'What is drawn?', 'make_turtle()\nfor i in range(4):\n    forward(50)\n    left(90)', 'A square.', 'make_turtle()\nfor i in range(4):\n    forward(50)\n    left(90)'),
  ('Test 6 (A): syntax error, normal error output', 'What happens?', "x = 5\nif x > 0\n    print('positive')",
   "```text\nSyntaxError: expected ':'\n```", 'run_code("""\nx = 5\nif x > 0\n    print(\'positive\')\n""")'),
  ('Test 7 (A): runtime error inside a function, normal error output', 'What happens?', "def outer(s):\n    return inner(s)\n\ndef inner(s):\n    return s + 1\n\nouter('hi')",
   '```text\nTypeError: can only concatenate str (not "int") to str\n```', 'run_code("""\ndef outer(s):\n    return inner(s)\n\ndef inner(s):\n    return s + 1\n\nouter(\'hi\')\n""")'),
 ], "print('END: Run all reached the last cell')")

build('colab_stop_test.ipynb',
 '# Colab test: the Stop button during Run all\n\nUse **Runtime > Run all**, then press Stop (the square on the running cell, or **Runtime > Interrupt execution**) '
 'while Test 1 is running (it takes 60 seconds). Expected: Run all stops, so the cell under **End** does **not** show `END`.',
 [('Test 1: a slow cell run by run_code', 'This runs for 60 seconds.', "import time\nfor i in range(60):\n    time.sleep(1)\nprint('finished')",
   '```text\nfinished\n```', 'run_code("""\nimport time\nfor i in range(60):\n    time.sleep(1)\nprint(\'finished\')\n""")')],
 "print('END: Run all was NOT stopped')")
print('ok')
