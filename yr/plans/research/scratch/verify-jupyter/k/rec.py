import nbformat as nbf
from nbclient import NotebookClient
nb = nbf.v4.new_notebook()
REC = "def countdown(n):\n    countdown(n - 2)\ncountdown(5)"
nb.cells = [nbf.v4.new_code_cell(REC), nbf.v4.new_code_cell(f'get_ipython().run_cell("""{REC}""", store_history=False)')]
NotebookClient(nb, timeout=120, kernel_name='python3', allow_errors=True).execute()
for c in nb.cells:
    for o in c.outputs:
        if o.output_type == 'error':
            print(o.ename, 'traceback lines:', sum(t.count('\n') + 1 for t in o.traceback))
