"""Q2 experiments: how errors raised in run_code(...) look and what execute_reply status they give.
Usage: python run_q2.py OUTDIR"""
import sys, re, json
from pathlib import Path
import nbformat
from nbclient import NotebookClient

out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
ANSI = re.compile(r'\x1b\[[0-9;]*m')

SETUP = r'''
import sys, traceback
ip = get_ipython()

def run_plain(code):
    """exec, exception propagates"""
    exec(code, globals())

def run_show(code):
    """exec, catch, showtraceback()"""
    try:
        exec(code, globals())
    except Exception:
        get_ipython().showtraceback()

def run_show_offset(code):
    """exec, catch, showtraceback(tb_offset=1)"""
    try:
        exec(code, globals())
    except Exception:
        get_ipython().showtraceback(tb_offset=1)

def run_show_only(code):
    """exec, catch, showtraceback(exception_only=True)"""
    try:
        exec(code, globals())
    except Exception:
        get_ipython().showtraceback(exception_only=True)

def run_cached(code):
    """compile with IPython's cell-style filename (so source lines show), hide own frame"""
    ip = get_ipython()
    name = ip.compile.cache(code, ip.execution_count)
    try:
        exec(compile(code, name, 'exec'), globals())
    except Exception:
        ip.showtraceback(tb_offset=1)

def run_cell_nested(code):
    """IPython's own run_cell, no history"""
    get_ipython().run_cell(code, store_history=False)
'''

ZERO = "x = 10\ny = 0\nprint('before')\nprint(x / y)\n"
SYN = "x = 5\nif x = 5:\n    print('five')\n"
NAME = "def f(n):\n    return n + undefined_name\n\nprint(f(3))\n"
TYPEERR = "def area(w, h):\n    return w * h\n\narea(3)\n"
EXPR = "x = 3\nx * 2\n"

cases = [
    ('A_normal_zero', ZERO, ['raises-exception']),
    ('A_normal_syntax', SYN, ['raises-exception']),
    ('A_normal_name', NAME, ['raises-exception']),
    ('A_normal_typeerr', TYPEERR, ['raises-exception']),
    ('A_normal_expr', EXPR, []),
]
for fn in ['run_plain', 'run_show', 'run_show_offset', 'run_show_only', 'run_cached', 'run_cell_nested']:
    for label, code in [('zero', ZERO), ('syntax', SYN), ('name', NAME), ('typeerr', TYPEERR), ('expr', EXPR)]:
        tags = ['raises-exception'] if fn == 'run_plain' and label != 'expr' else []
        cases.append((f'{fn}_{label}', f'{fn}("""\n{code}""")', tags))
cases.append(('after_all', "print('still running: last cell reached')", []))

nb = nbformat.v4.new_notebook()
nb.metadata['kernelspec'] = {'name': 'python3', 'display_name': 'Python 3', 'language': 'python'}
nb.cells.append(nbformat.v4.new_code_cell(SETUP))
for label, src, tags in cases:
    c = nbformat.v4.new_code_cell(src); c.metadata['tags'] = tags; c.metadata['label'] = label
    nb.cells.append(c)

replies = {}
def on_exec(cell, cell_index, execute_reply):
    replies[cell_index] = execute_reply['content']['status']

client = NotebookClient(nb, timeout=120, kernel_name='python3', allow_errors=False,
                        on_cell_executed=on_exec)
client.execute()
nbformat.write(nb, out / 'q2_executed.ipynb')

lines = []
import IPython
lines.append(f'# python {sys.version.split()[0]}; kernel IPython: see setup; nbclient allow_errors=False finished all cells\n')
for i, cell in enumerate(nb.cells[1:], start=1):
    lines.append('=' * 78)
    lines.append(f"[{cell.metadata.get('label')}] tags={cell.metadata.get('tags')} execute_reply.status={replies.get(i)}")
    lines.append('--- source:')
    lines.append(cell.source)
    lines.append('--- outputs:')
    for o in cell.outputs:
        if o.output_type == 'error':
            lines.append(f'<error output: ename={o.ename!r} evalue={o.evalue!r}>')
            lines.append(ANSI.sub('', '\n'.join(o.traceback)))
        elif o.output_type == 'stream':
            lines.append(f'<stream {o.name}> ' + o.text.rstrip())
        elif o.output_type == 'execute_result':
            lines.append(f"<execute_result count={o.execution_count}> " + o.data.get('text/plain', ''))
        else:
            lines.append(f'<{o.output_type}> {dict(o).get("data", {}).keys()}')
(out / 'q2_outputs.txt').write_text('\n'.join(lines) + '\n')
print('done; cells:', len(nb.cells))
