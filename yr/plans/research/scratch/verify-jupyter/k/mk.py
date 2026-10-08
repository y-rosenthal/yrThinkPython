import sys, json, nbformat as nbf
from nbclient import NotebookClient

SETUP = r'''
import sys, linecache, IPython
print(sys.version.split()[0], IPython.__version__)
def rc_show(code, **kw):
    try:
        exec(code, globals())
    except Exception:
        get_ipython().showtraceback(**kw)

def rc_cell(code):
    get_ipython().run_cell(code, store_history=False)

def rc_stderr(code):
    ip = get_ipython()
    try:
        exec(code, globals())
    except Exception:
        print(ip.InteractiveTB.stb2text(ip.InteractiveTB.structured_traceback(*sys.exc_info())), file=sys.stderr)

def rc_linecache(code):
    name = '<run_code>'
    linecache.cache[name] = (len(code), None, code.splitlines(True), name)
    try:
        exec(compile(code, name, 'exec'), globals())
    except SyntaxError:
        get_ipython().showsyntaxerror()
    except Exception:
        et, ev, tb = sys.exc_info()
        get_ipython().showtraceback((et, ev, tb.tb_next))

def rc_plain(code):
    exec(code, globals())
'''
SYN = '"""\nx = 5\nif x = 5:\n    print(\'five\')\n"""'
RT = '"""\ndef f(n):\n    return n / 0\nprint(\'start\')\nf(3)\n"""'
NAME = '"""\nprint(total)\n"""'
EXPR = '"""\nprice = 4\nprice * 3\n"""'
cells = [('setup', SETUP), ('normal_syntax', "x = 5\nif x = 5:\n    print('five')"),
         ('normal_rt', "def f(n):\n    return n / 0\nprint('start')\nf(3)")]
for h in ['rc_show', 'rc_cell', 'rc_stderr', 'rc_linecache']:
    for nm, s in [('syn', SYN), ('rt', RT), ('name', NAME), ('expr', EXPR)]:
        cells.append((f'{h}_{nm}', f'{h}({s})'))
cells += [('rc_show_off1_rt', f'rc_show({RT}, tb_offset=1)'),
          ('normal_expr', 'price = 4\nprice * 3'),
          ('magic_def', "from IPython.core.magic import register_cell_magic\nQ={}\n@register_cell_magic\ndef question(line, cell):\n    Q[line.strip()] = cell\n"),
          ('magic_use', "%%question q1\nx = 5\nif x = 5:\n    print('five')\n"),
          ('magic_check', "print(repr(Q['q1']))\nrc_cell(Q['q1'])"),
          ('unknown_magic', "%%questoin q2\nprint(1)\n"),
          ('last', "print('reached last cell')")]
nb = nbf.v4.new_notebook()
for cid, src in cells:
    c = nbf.v4.new_code_cell(src); c.id = cid; nb.cells.append(c)
statuses = {}
def hook(cell, cell_index, execute_reply):
    statuses[cell.id] = execute_reply['content']['status']
# allow_errors=True so all run; but record statuses. Separate run with allow_errors False below.
client = NotebookClient(nb, timeout=120, kernel_name='python3', allow_errors=True, on_cell_executed=hook)
client.execute()
import re
ANSI = re.compile(r'\x1b\[[0-9;]*m')
for c in nb.cells:
    print('=' * 20, c.id, 'status=', statuses.get(c.id))
    for o in c.outputs:
        if o.output_type == 'stream':
            print(f'[stream {o.name}]', ANSI.sub('', o.text)[:1500])
        elif o.output_type == 'error':
            print('[error]', o.ename, '|', ANSI.sub('', o.evalue))
            print(ANSI.sub('', '\n'.join(o.traceback))[:1500])
        else:
            print(f'[{o.output_type}]', o.get('execution_count'), dict(o.get('data', {})).get('text/plain'))
