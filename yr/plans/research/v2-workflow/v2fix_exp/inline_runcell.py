"""Inline run_cell form on both stacks: line numbers, reply status, doctest, stream splitting, no setup needed."""
import os, re, sys, nbformat as nbf
from nbclient import NotebookClient
os.environ['JUPYTER_PATH'] = sys.argv[1]
os.environ['TMPDIR'] = '/tmp'
W = lambda code: '# @title Output\n__import__(\'IPython\').get_ipython().run_cell(\nr"""\n' + code + '\n""");'
W1 = lambda code: "# @title Output\n__import__('IPython').get_ipython().run_cell(\nr'''\n" + code + "\n''');"
doctest_code = '''def count_e(word):
    """Count the letter e.

    >>> count_e('hello')
    1
    >>> count_e('eel')
    3
    """
    return word.count('e')

import doctest
doctest.run_docstring_examples(count_e, globals())'''
cells = [
 W("x = 5\nif x = 5:\n    print('five')"),
 W("x = 5\nif x > 0\n    print('positive')"),
 W("x = 5\n y = 6"),
 "def countdown_by_two(n):\n    if n == 0:\n        print('Blastoff!')\n    else:\n        countdown_by_two(n - 2)",
 W("countdown_by_two(5)"),
 W1(doctest_code),
 '# @title Output\n' + doctest_code,
 "# @title Output\nimport time\nprint('a')\ntime.sleep(0.6)\nprint('b')",
 W("price = 4\nprice * 3"),
 'print("next cell ran")',
]
for k in sys.argv[2:]:
    nb = nbf.v4.new_notebook(cells=[nbf.v4.new_code_cell(s) for s in cells])
    st = []
    NotebookClient(nb, kernel_name=k, allow_errors=False, timeout=60,
                   on_cell_executed=lambda cell, cell_index, execute_reply: st.append(execute_reply['content']['status'])).execute()
    print('=====', k, 'statuses', st)
    for i, cell in enumerate(nb.cells):
        for o in cell.outputs:
            if o.output_type == 'error':
                t = re.sub(r'\x1b\[[0-9;]*m', '', '\n'.join(o.traceback))
                print(f' [{i}] error {o.ename}: {t[:400]!r}')
            elif o.output_type == 'stream':
                print(f' [{i}] stream:{o.name} {o.text[:300]!r}')
            else:
                print(f' [{i}] {o.output_type} {dict(o.get("data", {}))}')
