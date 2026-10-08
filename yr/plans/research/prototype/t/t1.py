import nbformat as nbf, json, re
from nbclient import NotebookClient
setup = '''
def run_code(code):
    try:
        exec(code, globals())
    except Exception:
        get_ipython().showtraceback(tb_offset=1)
'''
cells = [setup,
 'run_code("""\nx = 5\nif x = 5:\n    print(\'five\')\n""")',
 'run_code("""\nx = 5\n y = 6\n""")',
 'def f(n):\n    return f(n-2) if n else 0',
 'run_code("f(5)")',
 'print("reached the end")']
nb = nbf.v4.new_notebook(cells=[nbf.v4.new_code_cell(c) for c in cells])
NotebookClient(nb, timeout=60, kernel_name='python3', allow_errors=False).execute()
ansi = re.compile(r'\x1b\[[0-9;]*m')
for c in nb.cells:
    print('=== cell:', c.source[:40].replace('\n','|'))
    for o in c.outputs:
        if o.output_type=='error':
            tb = ansi.sub('', '\n'.join(o.traceback))
            print('  ERROR output ename=%s evalue=%r\n  traceback (%d lines, first 12):' % (o.ename, o.evalue, len(tb.splitlines())))
            print('    ' + '\n    '.join(tb.splitlines()[:12]))
        else:
            print('  ', o.output_type, o.get('text', o.get('data')))
