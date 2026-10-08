import sys, nbformat as nbf
from nbclient import NotebookClient
MAGIC = open('magic_def.py').read()
dt = open('dt_body.txt').read()
cells = [MAGIC,
 '%%run_question\nx = 5\nif x = 5:\n    print(\'five\')',
 '%%run_question\nprint(\'start\')\nprint(1/0)',
 '%%run_question\ndef f(n):\n    return n + undefined_name\nf(3)',
 '%%run_question\nprice = 4\nprice * 3',
 '%%run_question\n' + dt,
 '%%run_question\nimport maath',
 '%%run_question\nx = 5\n y = 6',
 '%%run_question\nline = \'  hello world \\n\'\nprint(len(line), len(line.strip()))',
 '%%run_question\ndef greet(name):\n    """Print a greeting."""\n    print(\'Hello,\', name)\ngreet(\'Ada\')',
 'print("END REACHED")']
nb = nbf.v4.new_notebook(); nb.cells = [nbf.v4.new_code_cell(c) for c in cells]
st = {}
cl = NotebookClient(nb, kernel_name='python3', allow_errors=True)
cl.on_cell_executed = lambda cell, cell_index, execute_reply: st.__setitem__(cell_index, execute_reply['content']['status'])
cl.execute()
import re
A = re.compile(r'\x1b\[[0-9;]*m')
for i, c in enumerate(nb.cells):
    print(f'--- cell {i} status={st.get(i)}')
    for o in c.outputs:
        if o.output_type == 'error':
            print('  ERROR', o.ename, '|', A.sub('', o.evalue)); print('   ', '\n    '.join(A.sub('', '\n'.join(o.traceback)).splitlines()[:8]))
        elif o.output_type == 'stream':
            print('  STREAM', o.name, repr(o.text[:300]))
        else:
            print('  ', o.output_type, str(o.get('data', {}).get('text/plain'))[:100])
