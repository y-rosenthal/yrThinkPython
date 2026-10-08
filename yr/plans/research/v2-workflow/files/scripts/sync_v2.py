"""Prototype of `review.sh sync` for the v2 layout: derive everything derivable, run the page, store outputs.

    python sync_v2.py NB [--kernel colablike] [--out OUT.ipynb]

1. static normalize: each Answer's run cells are regenerated from the question's ```python run blocks
   (same order; title 'Output' or 'Output of part x'; hidden-code metadata for Colab and JupyterLab);
   Answer headings saved collapsed; colab.collapsed_sections = the Answer heading ids, in page order
2. run the page in a fresh kernel (default: the Colab-like stack), with allow_errors=True, ignoring tags
3. wrap exactly the run cells whose code raised in run_code(r\"\"\"...\"\"\"), unwrap the others; if that
   changed anything, run again
4. store the outputs of the run cells only (setup and other cells: none), normalized so that a re-run
   gives byte-identical JSON: no execution counts, no kernel PID in paths, 'Cell In[1]'
5. print which stored outputs changed (for the author to review), write the notebook
"""
import copy
import os
import shutil
import sys
import tempfile
from pathlib import Path

import nbformat as nbf
from nbclient import NotebookClient

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from review_v2 import (ANSWER_HEADING, RUN_CELL_METADATA, normalize_outputs, parse_page, parse_run_cell,
                       render_run_cell, semantic, source)

V2 = HERE.parent
os.environ['JUPYTER_PATH'] = str(V2 / 'kernels')
JUPYTURTLE = '/root/.venvs/yrThinkPython/yr-cache/jupyturtle.py'


def static_normalize(nb):
    changes = []
    for q in parse_page(nb):
        if q['answer'] is None:
            sys.exit(f"{q['title']}: no '{ANSWER_HEADING}' heading")
        if len(q['run_cells']) != len(q['run_blocks']):
            sys.exit(f"{q['title']}: {len(q['run_blocks'])} run blocks but {len(q['run_cells'])} run cells in the Answer")
        for (bi, part, code), ri in zip(q['run_blocks'], q['run_cells']):
            cell = nb.cells[ri]
            _, _, wrapped = parse_run_cell(source(cell))
            new = render_run_cell(code, wrapped, part if len(q['run_blocks']) > 1 else None)
            if source(cell) != new:
                changes.append(f"{q['title']}: run cell {cell.id} regenerated from its run block")
                cell.source = new
            meta = copy.deepcopy(RUN_CELL_METADATA)
            if dict(cell.metadata) != meta:
                cell.metadata = nbf.from_dict(meta)
    ids = []
    for c in nb.cells:
        if c.cell_type == 'markdown' and source(c).strip() == ANSWER_HEADING:
            want = {'id': c.id, 'jp-MarkdownHeadingCollapsed': True}
            if dict(c.metadata) != want:
                changes.append(f'Answer heading {c.id}: collapse metadata written')
                c.metadata = nbf.from_dict(want)
            ids.append(c.id)
    if nb.metadata.get('colab', {}).get('collapsed_sections') != ids:
        changes.append('colab.collapsed_sections rewritten')
        nb.metadata.setdefault('colab', {})['collapsed_sections'] = ids
    return changes


def execute(nb, kernel):
    """Run a copy of nb like Run all but without stopping (allow_errors), tags ignored.
    Returns (executed copy, {cell index: reply status})."""
    run = copy.deepcopy(nb)
    for c in run.cells:
        c.metadata.pop('tags', None)
    status = {}

    def hook(cell, cell_index, execute_reply):
        status[cell_index] = execute_reply['content']['status']

    with tempfile.TemporaryDirectory() as tmp:
        shutil.copy(JUPYTURTLE, tmp)
        NotebookClient(run, kernel_name=kernel, timeout=600, allow_errors=True, record_timing=False,
                       on_cell_executed=hook, resources={'metadata': {'path': tmp}}).execute()
    return run, status


def raised(cell):
    return any(o['output_type'] == 'error' for o in cell.outputs)


def sync(nb, kernel):
    report = static_normalize(nb)
    questions = parse_page(nb)
    for attempt in range(3):
        run, status = execute(nb, kernel)
        rewrapped = False
        for q in questions:
            multi = len(q['run_blocks']) > 1
            for (bi, part, code), ri in zip(q['run_blocks'], q['run_cells']):
                _, _, wrapped = parse_run_cell(source(nb.cells[ri]))
                r = raised(run.cells[ri])
                if r != wrapped:
                    nb.cells[ri].source = render_run_cell(code, r, part if multi else None)
                    report.append(f"{q['title']}: run cell {nb.cells[ri].id} {'wrapped in run_code' if r else 'unwrapped'}")
                    rewrapped = True
        if not rewrapped:
            break
    else:
        sys.exit('wrapping did not settle after 3 runs')
    run_cells = {ri for q in questions for ri in q['run_cells']}
    for i, (c, r) in enumerate(zip(nb.cells, run.cells)):
        if c.cell_type != 'code':
            continue
        new = normalize_outputs(r.outputs) if i in run_cells else []
        if i in run_cells and semantic(c.get('outputs', [])) != semantic(new):
            report.append(f'stored output of run cell {c.id} changed:\n      old {semantic(c.get("outputs", []))}'
                          f'\n      new {semantic(new)}'[:600])
        c.outputs = [nbf.from_dict(o) for o in new]
        c.execution_count = None
    bad = [i for i, s in status.items() if s != 'ok']
    return report, bad


def main(argv):
    path = Path(argv[0])
    kernel = argv[argv.index('--kernel') + 1] if '--kernel' in argv else 'colablike'
    out = Path(argv[argv.index('--out') + 1]) if '--out' in argv else path
    nb = nbf.read(path, as_version=4)
    report, bad = sync(nb, kernel)
    for line in report:
        print('  -', line)
    if bad:
        print(f'  ! cells with reply status "error" (Run all would stop there): {bad}')
    nbf.validate(nb)
    nbf.write(nb, out)
    print(f'synced {path} -> {out} with kernel {kernel}: {len(report)} change(s)')
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
