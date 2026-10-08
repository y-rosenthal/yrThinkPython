import nbformat, sys, json
from nbclient import NotebookClient
rc = open('rc_new.py').read()
cells = [rc,
 'run_code(r"""\nx = 5\nif x = 5:\n    print(\'five\')\n""")',
 'run_code(r"""\ndef f(n):\n    return 1/n\nf(0)\n""")',
 'run_code(r"""\nimport maath\n""")',
 'run_code(r"""\nprice = 4\nprice * 3\n""")',
 'print("END")']
nb = nbformat.v4.new_notebook(cells=[nbformat.v4.new_code_cell(c) for c in cells])
status = {}
def hook(cell, cell_index, execute_reply):
    status[cell_index] = execute_reply['content']['status']
kn = sys.argv[1]
c = NotebookClient(nb, kernel_name=kn, allow_errors=False, force_raise_errors=True, on_cell_executed=hook, timeout=60)
c.execute()
for i, cell in enumerate(nb.cells):
    outs = []
    for o in cell.outputs:
        if o.output_type == 'error': outs.append('error:' + o.ename)
        elif o.output_type == 'stream': outs.append(o.name + ':' + o.text.strip()[:40])
        else: outs.append(o.output_type + ':' + str(o.get('data', {}).get('text/plain', ''))[:30])
    print(i, status.get(i), outs)
