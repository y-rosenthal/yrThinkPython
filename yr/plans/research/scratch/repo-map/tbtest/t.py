import nbformat as nbf, re
from nbclient import NotebookClient
setup = '''
def run_code(code):
    try:
        exec(code, globals())
    except Exception:
        get_ipython().showtraceback()
'''
setup2 = '''
def run_code2(code):
    try:
        exec(compile(code, '<code>', 'exec'), globals())
    except Exception:
        get_ipython().showtraceback(tb_offset=1)
'''
cells = [setup, setup2,
 'def inner(value):\n    print(value + 1)\n\ndef outer(value):\n    print("outer got", value)\n    inner(value)',
 'run_code("""\nouter(\'hi\')\n""")',
 'run_code2("""\nouter(\'hi\')\n""")',
 'run_code("""\nx = 5\nif x = 5:\n    print(1)\n""")',
 'run_code("""\nimport maath\n""")',
 'outer("hi")',
 'print("reached end")']
nb = nbf.v4.new_notebook(cells=[nbf.v4.new_code_cell(c) for c in cells])
c = NotebookClient(nb, timeout=60, kernel_name='python3', allow_errors=False)
try:
    c.execute()
except Exception as e:
    print('STOPPED:', type(e).__name__, str(e).splitlines()[0] if str(e) else '')
ansi = re.compile(r'\x1b\[[0-9;]*m')
for i, cell in enumerate(nb.cells):
    print(f'--- cell {i}: {cell.source.splitlines()[0][:40]!r}')
    for o in cell.get('outputs', []):
        if o.output_type == 'error':
            print('  ERROR output ename=%r evalue=%r' % (o.ename, o.evalue))
            print('  ' + '\n  '.join(ansi.sub('', '\n'.join(o.traceback)).splitlines()))
        elif o.output_type == 'stream':
            print('  stream:', o.text.strip())
