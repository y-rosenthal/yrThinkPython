import nbformat as nbf, re
from nbclient import NotebookClient
setup = '''
import sys, linecache
def run_code(code):
    name = '<run_code>'
    linecache.cache[name] = (len(code), None, code.splitlines(True), name)
    try:
        exec(compile(code, name, 'exec'), globals())
    except Exception:
        etype, value, tb = sys.exc_info()
        get_ipython().showtraceback((etype, value, tb.tb_next))
'''
cells = [setup,
 'def inner(value):\n    print(value + 1)\n\ndef outer(value):\n    print("outer got", value)\n    inner(value)',
 'run_code("""\nouter(\'hi\')\n""")',
 'run_code("""\nx = 5\nif x = 5:\n    print(1)\n""")',
 'print("reached end")']
nb = nbf.v4.new_notebook(cells=[nbf.v4.new_code_cell(c) for c in cells])
NotebookClient(nb, timeout=60, kernel_name='python3', allow_errors=False).execute()
ansi = re.compile(r'\x1b\[[0-9;]*m')
for i, cell in enumerate(nb.cells):
    print(f'--- cell {i}')
    for o in cell.get('outputs', []):
        if o.output_type == 'error':
            print('  ERROR ename=%r evalue=%r' % (o.ename, o.evalue))
            print('  ' + '\n  '.join(ansi.sub('', '\n'.join(o.traceback)).splitlines()))
        elif o.output_type == 'stream':
            print('  stream:', o.text.strip())
