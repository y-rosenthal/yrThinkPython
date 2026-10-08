"""A small Colab test page that shows Question 8's three errors two ways, each under a closed Answer heading:
  A  a normal error output (what chap05_review.ipynb uses; Colab adds its red icon and 'Explain error' button)
  B  the same traceback printed as text on stderr (variant B of the plan, section 10: no error output at all)
Outputs are stored (Colab-like stack), so A and B can be compared before and after Run all.

    python make_ab_demo.py OUT.ipynb
"""
import copy
import os
import sys
from pathlib import Path

import nbformat as nbf
from nbclient import NotebookClient

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from review_v2 import RUN_CELL_METADATA, normalize_outputs, quote, render_run_cell, stable_id

os.environ['JUPYTER_PATH'] = str(HERE.parent / 'kernels')
PARTS = {'a': "x = 5\nif x = 5:\n    print('five')", 'b': "x = 5\nif x > 0\n    print('positive')", 'c': 'x = 5\n y = 6'}
HELPER_B = '''# @title Helper for B
def run_code_b(code):
    """Run code as a cell of its own; print an error's traceback as text (stderr) instead of an error output."""
    import sys
    from IPython import get_ipython
    ip = get_ipython()
    if ip is None:
        exec(code, globals())
        return

    def to_stderr(etype, evalue, stb):
        stb = getattr(stb, 'stb', stb)           # Colab passes a ColabTraceback for import errors
        print(ip.InteractiveTB.stb2text(stb), file=sys.stderr)

    ip._showtraceback = to_stderr
    try:
        ip.run_cell(code, store_history=False)
    finally:
        del ip._showtraceback'''


def md(text, cid, **meta):
    c = nbf.v4.new_markdown_cell(text)
    c.id = cid
    c.metadata.update(meta)
    return c


def code(src, cid, hidden=True):
    c = nbf.v4.new_code_cell(src)
    c.id = cid
    if hidden:
        c.metadata = nbf.from_dict(copy.deepcopy(RUN_CELL_METADATA))
    return c


cells = [md('# Error display test (prototype v2)\n\n'
            'Question 8 of the chapter 5 review page shows three errors. This page shows them two ways, each under a '
            'closed **Answer**:\n\n'
            '- **A**: a normal error, as on the review page. Colab adds its red error icon and **Explain error** button.\n'
            '- **B**: the same traceback printed as text. Colab has nothing to flag, so neither appears.\n\n'
            'Look at both Answers before running anything, then use **Runtime → Run all** (choose **Run anyway** if asked) '
            'and look again. The last cell prints END. Which do you prefer?', 'ab000001'),
         md('### A: a normal error', 'ab000002'),
         md('#### Answer', 'ab0000a0', id='ab0000a0', **{'jp-MarkdownHeadingCollapsed': True})]
for p, src in PARTS.items():
    cells += [md(f'**Part {p}:**', stable_id('ab', 'A', p)), code(render_run_cell(src, True, p), stable_id('ab', 'Arun', p))]
cells += [md('### B: the traceback as text', 'ab000003'),
          code(HELPER_B, 'ab0000h1'),
          md('#### Answer', 'ab0000b0', id='ab0000b0', **{'jp-MarkdownHeadingCollapsed': True})]
for p, src in PARTS.items():
    cells += [md(f'**Part {p}:**', stable_id('ab', 'B', p)),
              code(f'# @title Output of part {p}\nrun_code_b(\n{quote(src)})', stable_id('ab', 'Brun', p))]
cells += [md('### End\n\nThe cell below also shows which Python and IPython this Colab session runs.', 'ab000004'),
          code("import sys, IPython, ipykernel\nprint('END: Run all reached the end. Python', sys.version.split()[0], "
               "'| IPython', IPython.__version__, '| ipykernel', ipykernel.__version__)", 'ab0000e1', hidden=False)]
nb = nbf.v4.new_notebook(cells=cells)
nb.metadata = nbf.from_dict({'colab': {'collapsed_sections': ['ab0000a0', 'ab0000b0']},
                             'kernelspec': {'display_name': 'Python 3 (ipykernel)', 'language': 'python', 'name': 'python3'},
                             'language_info': {'name': 'python'}})
run = copy.deepcopy(nb)
status = []
NotebookClient(run, kernel_name='colablike', timeout=120, allow_errors=False,
               on_cell_executed=lambda cell, cell_index, execute_reply: status.append(execute_reply['content']['status'])
               ).execute(env={**os.environ, 'TMPDIR': '/tmp'})
assert set(status) == {'ok'}, status
for c, r in zip(nb.cells, run.cells):
    if c.cell_type == 'code' and 'Output of part' in c.source:
        c.outputs = [nbf.from_dict(o) for o in normalize_outputs(r.outputs)]
nbf.validate(nb)
nbf.write(nb, sys.argv[1])
print(f'wrote {sys.argv[1]}: Run all on the Colab-like kernel reached the end ({len(status)} cells, all status ok)')
for c in nb.cells:
    if c.cell_type == 'code' and c.outputs:
        print(f'  {c.id}: ' + ', '.join(o["output_type"] + (":" + o.get("name", o.get("ename", ""))) for o in c.outputs))
