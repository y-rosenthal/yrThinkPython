import nbformat as nbf, re
from nbclient import NotebookClient
SETUP = r'''
import sys
def run_code(code):
    ip = get_ipython()
    def to_stderr(etype, evalue, stb):
        print(ip.InteractiveTB.stb2text(stb), file=sys.stderr)
    ip._showtraceback = to_stderr
    try:
        r = ip.run_cell(code, store_history=False)
    finally:
        del ip._showtraceback
    if isinstance(r.error_in_exec, KeyboardInterrupt):
        raise r.error_in_exec
'''
nb = nbf.v4.new_notebook()
nb.cells = [nbf.v4.new_code_cell(SETUP),
            nbf.v4.new_code_cell('run_code("""\nx = 5\nif x = 5:\n    print(1)\n""")'),
            nbf.v4.new_code_cell('run_code("""\ndef f(n):\n    return n / 0\nprint(\'start\')\nf(3)\n""")'),
            nbf.v4.new_code_cell("1/0"),
            nbf.v4.new_code_cell("print('last')")]
st = {}
NotebookClient(nb, timeout=120, kernel_name='python3', allow_errors=True,
               on_cell_executed=lambda cell, cell_index, execute_reply: st.__setitem__(cell_index, execute_reply['content']['status'])).execute()
A = re.compile(r'\x1b\[[0-9;]*m')
for i, c in enumerate(nb.cells):
    print('== cell', i, st.get(i), [o.output_type + ':' + o.get('name', o.get('ename', '')) for o in c.outputs])
    for o in c.outputs:
        if o.output_type == 'stream' and o.name == 'stderr': print(A.sub('', o.text))
