"""Q4: a cell magic that stores the cell body without running it; answer cell runs it.
Usage: python run_q4.py OUTDIR"""
import sys, re
from pathlib import Path
import nbformat
from nbclient import NotebookClient

out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
ANSI = re.compile(r'\x1b\[[0-9;]*m')

SETUP = r'''
import sys, IPython
from IPython.core.magic import register_cell_magic
print('IPython', IPython.__version__, 'Python', sys.version.split()[0])

questions = {}

@register_cell_magic
def question(line, cell):
    """%%question NAME: remember this cell's code under NAME without running it."""
    questions[line.strip()] = cell

def run_question(name):
    """Run the code remembered by %%question NAME, as if it were a cell of its own."""
    ip = get_ipython()
    ip.execution_count -= 1          # so tracebacks say Cell In[N] for this cell's own N (IPython 8+)
    try:
        ip.run_cell(questions[name], store_history=False)
    finally:
        ip.execution_count += 1
'''

cells = [
    ('magic_syntax', "%%question q1\nx = 5\nif x = 5:\n    print('five')\n", []),
    ('show_stored', "print(repr(questions['q1']))", []),
    ('answer_syntax', "run_question('q1')", []),
    ('magic_indent', "%%question q2\nx = 5\n y = 6\n", []),
    ('answer_indent', "run_question('q2')", []),
    ('magic_runtime', "%%question q3\nx = 10\ny = 0\nprint('before')\nprint(x / y)\n", []),
    ('answer_runtime', "run_question('q3')", []),
    ('magic_expr', "%%question q4\nx = 3\nx * 2\n", []),
    ('answer_expr', "run_question('q4')", []),
    ('magic_with_magics_inside', "%%question q5\n%time y = 1\nprint(y)\n", []),
    ('answer_with_magics_inside', "run_question('q5')", []),
    ('magic_empty_line_name', "%%question\nprint('no name')\n", []),
    ('unknown_magic', "%%questoin q6\nprint('typo in magic name')\n", ['raises-exception']),
    ('after_all', "print('last cell reached'); print(sorted(questions))", []),
]

nb = nbformat.v4.new_notebook()
nb.cells.append(nbformat.v4.new_code_cell(SETUP))
for label, src, tags in cells:
    c = nbformat.v4.new_code_cell(src); c.metadata['tags'] = tags; c.metadata['label'] = label
    nb.cells.append(c)
replies = {}
client = NotebookClient(nb, timeout=180, kernel_name='python3', allow_errors=False,
                        on_cell_executed=lambda cell, cell_index, execute_reply: replies.__setitem__(cell_index, execute_reply['content']['status']))
client.execute()
nbformat.write(nb, out / 'q4_executed.ipynb')
lines = [nb.cells[0].outputs[0].text]
for i, cell in enumerate(nb.cells[1:], start=1):
    lines.append('=' * 78)
    lines.append(f"[{cell.metadata['label']}] In[{cell.execution_count}] tags={cell.metadata['tags']} execute_reply.status={replies.get(i)}")
    lines.append(cell.source)
    lines.append('--- outputs:' + ('' if cell.outputs else ' (none)'))
    for o in cell.outputs:
        if o.output_type == 'error':
            lines.append(f'<error output: ename={o.ename!r}>')
            lines.append(ANSI.sub('', '\n'.join(o.traceback)))
        elif o.output_type == 'stream':
            lines.append(f'<stream {o.name}> ' + o.text.rstrip())
        elif o.output_type == 'execute_result':
            lines.append(f"<execute_result count={o.execution_count}> " + o.data.get('text/plain', ''))
(out / 'q4_outputs.txt').write_text('\n'.join(lines) + '\n')
print('done')
