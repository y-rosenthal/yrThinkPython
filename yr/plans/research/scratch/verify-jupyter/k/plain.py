import nbformat as nbf, re
from nbclient import NotebookClient
nb = nbf.v4.new_notebook()
nb.cells = [nbf.v4.new_code_cell('def run_code(code):\n    exec(code, globals())'),
            nbf.v4.new_code_cell('run_code("""\nx = 5\nif x = 5:\n    print(1)\n""")')]
NotebookClient(nb, timeout=60, kernel_name='python3', allow_errors=True).execute()
A = re.compile(r'\x1b\[[0-9;]*m')
for o in nb.cells[1].outputs:
    print(A.sub('', '\n'.join(o.traceback)))
