import nbformat as nbf, re, sys
from nbclient import NotebookClient
variants = {
'plain_cell': ('', 'f(5)'),
'offset0': ('''
def run_code(code):
    try:
        exec(code, globals())
    except Exception:
        get_ipython().showtraceback()
''', 'run_code("f(5)")'),
'offset1': ('''
def run_code(code):
    try:
        exec(code, globals())
    except Exception:
        get_ipython().showtraceback(tb_offset=1)
''', 'run_code("f(5)")'),
'run_cell': ('''
def run_code(code):
    get_ipython().run_cell(code)
''', 'run_code("f(5)")'),
}
ansi = re.compile(r'\x1b\[[0-9;]*m')
for name,(setup,call) in variants.items():
    cells = [setup, 'def f(n):\n    return f(n-2) if n else 0', call, 'print("end")']
    nb = nbf.v4.new_notebook(cells=[nbf.v4.new_code_cell(c) for c in cells])
    nb.cells[2].metadata['tags'] = ['raises-exception']
    NotebookClient(nb, timeout=60, kernel_name='python3', allow_errors=False).execute()
    out = nb.cells[2].outputs
    print('=====', name, 'outputs:', [o.output_type for o in out], 'end reached:', bool(nb.cells[3].outputs))
    for o in out:
        if o.output_type == 'error':
            tb = ansi.sub('', '\n'.join(o.traceback)).splitlines()
            print('  %d lines' % len(tb)); print('    ' + '\n    '.join(tb[:22])); print('    ...'); print('    ' + '\n    '.join(tb[-4:]))
