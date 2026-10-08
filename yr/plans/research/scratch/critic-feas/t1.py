import sys, nbformat as nbf
from nbclient import NotebookClient
RUN_CODE = '''def run_code(code):
    """Run code (a string) as if it were a cell of its own."""
    try:
        ip = get_ipython()
    except NameError:                 # plain Python (the review tools): just run it
        exec(code, globals())
        return
    result = ip.run_cell(code, store_history=False)
    if isinstance(result.error_in_exec, KeyboardInterrupt):
        raise KeyboardInterrupt       # the Stop button still stops Run all
'''
cells = [RUN_CODE,
 "import sys, IPython; print(sys.version.split()[0], IPython.__version__)",
 "def greet():\n    print('Hello')\n\ngreet",
 "price = 4\nprice * 2\nprice * 3",
 'run_code(r"""\nx = 5\nif x = 5:\n    print(\'five\')\n""")',
 'run_code(r"""\nprint(\'start\')\nprint(total)\n""")',
 'run_code(r"""\ndef f():\n    return 1/0\nf()\n""")',
 'run_code(r"""\nimport nosuchmodule_xyz\n""")',
 "print('end')"]
nb = nbf.v4.new_notebook(cells=[nbf.v4.new_code_cell(c) for c in cells])
stat = []
def hook(cell, cell_index, execute_reply):
    stat.append((cell_index, execute_reply['content']['status']))
NotebookClient(nb, timeout=60, kernel_name='python3', allow_errors=True, on_cell_executed=hook).execute()
import re
A=re.compile(r'\x1b\[[0-9;]*m')
for i,c in enumerate(nb.cells):
    print('--- cell', i, dict(stat).get(i))
    for o in c.outputs:
        if o.output_type=='stream': print('  stream', o.name, repr(o.text[:200]))
        elif o.output_type=='execute_result': print('  result', o.data.get('text/plain'))
        elif o.output_type=='error': print('  error', o.ename, A.sub('',o.evalue)); print('   ', A.sub('','\n'.join(o.traceback))[:600].replace('\n','\n    '))
