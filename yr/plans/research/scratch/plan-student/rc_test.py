"""Run the plan's run_code (A: nested run_cell; B: stderr fallback) through a kernel, record reply status + outputs."""
import sys, re, json
import nbformat as nbf
from nbclient import NotebookClient
SETUP = r'''
import sys
def run_code(code):
    """Run code (a string) as if it were a cell of its own, showing its output and its error.
    An error does not stop "Run all". (Code in a string is also not underlined by Colab's editor.)"""
    try:
        ip = get_ipython()
    except NameError:              # plain Python (e.g. yr/tools/turtle_images.py): just run it
        exec(code, globals())
        return
    result = ip.run_cell(code, store_history=False)
    if isinstance(result.error_in_exec, KeyboardInterrupt):
        raise KeyboardInterrupt    # the Stop button still stops "Run all"

def run_code_stderr(code):
    """Fallback: the same, but the traceback is printed (stderr) instead of shown as an error output."""
    ip = get_ipython()
    def to_stderr(etype, evalue, stb):
        print(ip.InteractiveTB.stb2text(stb), file=sys.stderr)
    ip._showtraceback = to_stderr
    try:
        result = ip.run_cell(code, store_history=False)
    finally:
        del ip._showtraceback
    if isinstance(result.error_in_exec, KeyboardInterrupt):
        raise KeyboardInterrupt
'''
cells = [SETUP,
 'run_code("""\nx = 5\nif x = 5:\n    print(\'five\')\n""")',
 'run_code("""\nprint(\'start\')\nprint(total)\n""")',
 'run_code("""\ndef outer(s):\n    return inner(s)\ndef inner(s):\n    return s + 1\nouter(\'hi\')\n""")',
 'run_code("""\nprice = 4\nprice * 3\n""")',
 'run_code_stderr("""\nx = 5\nif x = 5:\n    print(\'five\')\n""")',
 'run_code_stderr("""\nprint(total)\n""")',
 'print("END")']
nb = nbf.v4.new_notebook(cells=[nbf.v4.new_code_cell(c) for c in cells])
status = {}
def hook(cell, cell_index, execute_reply):
    status[cell_index] = execute_reply['content']['status']
NotebookClient(nb, kernel_name='python3', allow_errors=False, on_cell_executed=hook).execute()
ANSI = re.compile(r'\x1b\[[0-9;]*m')
import IPython
print('IPython', IPython.__version__, 'Python', sys.version.split()[0])
for i, c in enumerate(nb.cells[1:], 1):
    print(f'--- cell {i} status={status.get(i)} src={c.source.splitlines()[0][:40]!r}')
    for o in c.outputs:
        if o.output_type == 'error':
            print('   error:', o.ename, '|', ANSI.sub('', o.evalue)); print('   ', '\n    '.join(ANSI.sub('', l) for l in '\n'.join(o.traceback).splitlines()[:12]))
        elif o.output_type == 'stream':
            t = ANSI.sub('', o.text); print(f'   stream {o.name}:', '\n    '.join(t.rstrip().splitlines()[-12:]))
        else:
            print('  ', o.output_type, o.get('data', {}).get('text/plain'))
