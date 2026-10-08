import sys, json, os
import nbformat as nbf
from nbclient import NotebookClient
V2 = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.environ['JUPYTER_PATH'] = os.path.join(V2, 'kernels')
RC = '''def run_code(code):
    """doc"""
    code = code.removeprefix('\\n')
    try:
        from IPython import get_ipython
        ip = get_ipython()
    except ImportError:
        ip = None
    if ip is None:
        exec(code, globals())
        return
    result = ip.run_cell(code, store_history=False)
    if isinstance(result.error_in_exec, KeyboardInterrupt):
        raise KeyboardInterrupt
'''
cells = [RC,
 'from jupyturtle import make_turtle, forward, left, right, penup, pendown',
 '# @title Output of part a { display-mode: "form" }\nrun_code(r"""\nx = 5\nif x = 5:\n    print(\'five\')\n""")',
 '# @title Output of part c { display-mode: "form" }\nrun_code(r"""\nx = 5\n y = 6\n""")',
 'def countdown_by_two(n):\n    if n == 0:\n        print(\'Blastoff!\')\n    else:\n        countdown_by_two(n - 2)',
 '# @title Output { display-mode: "form" }\nrun_code(r"""\ncountdown_by_two(5)\n""")',
 '# @title Output { display-mode: "form" }\nminutes = 135\nprint(minutes // 60, minutes % 60)',
 '# @title Output { display-mode: "form" }\nmake_turtle(delay=0, height=100)\nforward(30)\nleft(90)\nforward(20)',
 '# @title Output { display-mode: "form" }\nrun_code(r"""\nprice = 4\nprice * 3\n""")',
 'print("END")']
nb = nbf.v4.new_notebook(cells=[nbf.v4.new_code_cell(c) for c in cells])
status = {}
def hook(cell, cell_index, execute_reply):
    status[cell_index] = execute_reply['content']['status']
c = NotebookClient(nb, kernel_name=sys.argv[1], allow_errors=False, force_raise_errors=True, on_cell_executed=hook, timeout=120,
                   resources={'metadata': {'path': os.path.join(V2, 'work')}})
c.execute()
for i, cell in enumerate(nb.cells):
    print('== cell', i, status.get(i), cell.execution_count)
    for o in cell.outputs:
        d = dict(o)
        if 'data' in d:
            d['data'] = {k: (v[:200] + '...' if len(v) > 200 else v) for k, v in d['data'].items()}
        print(json.dumps(d, indent=1)[:3000])
