import nbformat as nbf, re
from nbclient import NotebookClient
from nbclient.exceptions import CellExecutionError
variants = {
'showtraceback': '''
def run_code(code):
    try:
        exec(code, globals())
    except Exception:
        get_ipython().showtraceback()
''',
'run_cell': '''
def run_code(code):
    get_ipython().run_cell(code)
''',
'stderr_text': '''
import sys
def run_code(code):
    ip = get_ipython()
    try:
        exec(code, globals())
    except Exception:
        etype, value, tb = sys.exc_info()
        if issubclass(etype, SyntaxError):
            stb = ip.SyntaxTB.structured_traceback(etype, value, [])
        else:
            stb = ip.InteractiveTB.structured_traceback(etype, value, tb, tb_offset=1)
        print(ip.InteractiveTB.stb2text(stb), file=sys.stderr)
''',
}
ansi = re.compile(r'\x1b\[[0-9;]*m')
for name,setup in variants.items():
    cells = [setup, 'def f(n):\n    return f(n-2) if n else 0', 'run_code("f(5)")',
             'run_code("""\nx = 5\nif x = 5:\n    print(\'five\')\n""")', 'print("end")']
    nb = nbf.v4.new_notebook(cells=[nbf.v4.new_code_cell(c) for c in cells])
    try:
        NotebookClient(nb, timeout=60, kernel_name='python3', allow_errors=False).execute()
        status = 'ran to the end' 
    except CellExecutionError as e:
        status = 'STOPPED: ' + str(e).splitlines()[0]
    print('=====', name, '|', status, '| execution counts', [c.execution_count for c in nb.cells])
    for k in (2, 3):
        out = nb.cells[k].outputs
        print('  cell', k, [ (o.output_type, o.get('name')) for o in out])
        for o in out:
            txt = '\n'.join(o.traceback) if o.output_type == 'error' else o.get('text', '')
            lines = ansi.sub('', txt).splitlines()
            print('    %d lines; first 6:' % len(lines), lines[:6], ' last:', lines[-1:])
