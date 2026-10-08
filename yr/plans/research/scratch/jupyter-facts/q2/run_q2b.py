"""Q2b: variants that try to make run_code errors look like normal cell errors.
Usage: python run_q2b.py OUTDIR [kernel_name]"""
import sys, re
from pathlib import Path
import nbformat
from nbclient import NotebookClient

out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
kernel = sys.argv[2] if len(sys.argv) > 2 else 'python3'
ANSI = re.compile(r'\x1b\[[0-9;]*m')

SETUP = r'''
import sys, IPython
print('IPython', IPython.__version__, 'Python', sys.version.split()[0])

def run_offset2(code):
    try:
        exec(code, globals())
    except Exception:
        get_ipython().showtraceback(tb_offset=2)

def run_tbnext(code):
    """drop own frame from the traceback object"""
    try:
        exec(code, globals())
    except Exception:
        etype, value, tb = sys.exc_info()
        get_ipython().showtraceback((etype, value, tb.tb_next))

def run_cached_next(code):
    """cell-style filename (source lines shown) + drop own frame; strip the newline after triple quotes"""
    ip = get_ipython()
    if code.startswith('\n'):
        code = code[1:]
    try:
        name = ip.compile.cache(code, ip.execution_count)
        exec(compile(code, name, 'exec'), globals())
    except SyntaxError:
        ip.showsyntaxerror()
    except Exception:
        etype, value, tb = sys.exc_info()
        ip.showtraceback((etype, value, tb.tb_next))

def run_cell_nested(code):
    """IPython's own run_cell, no history"""
    get_ipython().run_cell(code, store_history=False)
'''

ZERO = "x = 10\ny = 0\nprint('before')\nprint(x / y)\n"
SYN = "x = 5\nif x = 5:\n    print('five')\n"
NAME = "def f(n):\n    return n + undefined_name\n\nprint(f(3))\n"
IND = "x = 5\n y = 6\n"
EXPR = "x = 3\nx * 2\n"
REC = "def f(n):\n    return f(n + 1)\n\nf(0)\n"

cases = [('normal_zero', ZERO, ['raises-exception']), ('normal_syntax', SYN, ['raises-exception']),
         ('normal_indent', IND, ['raises-exception']), ('normal_name', NAME, ['raises-exception']),
         ('normal_expr', EXPR, [])]
for fn in ['run_offset2', 'run_tbnext', 'run_cached_next', 'run_cell_nested']:
    for label, code in [('zero', ZERO), ('syntax', SYN), ('indent', IND), ('name', NAME), ('expr', EXPR)]:
        cases.append((f'{fn}_{label}', f'{fn}("""\n{code}""")', []))
cases.append(('run_cell_nested_recursion', f'run_cell_nested("""\n{REC}""")', []))
cases.append(('normal_recursion', REC, ['raises-exception']))
cases.append(('after_all', "print('still running: last cell reached')", []))

nb = nbformat.v4.new_notebook()
nb.cells.append(nbformat.v4.new_code_cell(SETUP))
for label, src, tags in cases:
    c = nbformat.v4.new_code_cell(src); c.metadata['tags'] = tags; c.metadata['label'] = label
    nb.cells.append(c)
replies = {}
client = NotebookClient(nb, timeout=180, kernel_name=kernel, allow_errors=False,
                        on_cell_executed=lambda cell, cell_index, execute_reply: replies.__setitem__(cell_index, execute_reply['content']['status']))
client.execute()
nbformat.write(nb, out / 'q2b_executed.ipynb')

lines = [nb.cells[0].outputs[0].text]
for i, cell in enumerate(nb.cells[1:], start=1):
    lines.append('=' * 78)
    lines.append(f"[{cell.metadata['label']}] In[{cell.execution_count}] tags={cell.metadata['tags']} execute_reply.status={replies.get(i)}")
    lines.append(cell.source)
    lines.append('--- outputs:')
    for o in cell.outputs:
        if o.output_type == 'error':
            tb = ANSI.sub('', '\n'.join(o.traceback))
            if 'recursion' in cell.metadata['label']:
                tb = '\n'.join(tb.splitlines()[:14] + ['   ...'] + tb.splitlines()[-6:])
            lines.append(f'<error output: ename={o.ename!r}>')
            lines.append(tb)
        elif o.output_type == 'stream':
            lines.append(f'<stream {o.name}> ' + o.text.rstrip())
        elif o.output_type == 'execute_result':
            lines.append(f"<execute_result count={o.execution_count}> " + o.data.get('text/plain', ''))
(out / 'q2b_outputs.txt').write_text('\n'.join(lines) + '\n')
print('done')
