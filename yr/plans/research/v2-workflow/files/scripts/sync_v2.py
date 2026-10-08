"""Prototype of `review.sh sync` for the v2 layout: derive everything derivable, run the page, store outputs.

    python sync_v2.py NB [--kernel colablike] [--out OUT.ipynb] [--accept] [--force] [--static]

1. static normalize (no kernel; also what `review_cells.py normalize` would do):
   - run cells reconciled with the question's ~~~python run blocks: one per block, matched by the part letter
     in the title; a missing run cell is created (one block: right after '#### Answer'; several: right after
     its '**Part x:**' cell, which is created as '**Part x:** TODO' if missing, and lint fails until it is
     written); orphan run cells are deleted; multi-part run cells are moved right after their Part cell
   - a run cell whose code no longer equals its block is regenerated AND its outputs are cleared; titles and
     the wrap layout are made canonical (e.g. after Colab rewrote '#@title ... { display-mode: "both" }')
   - metadata Colab adds on save is dropped; run cells get exactly cellView=form + jupyter.source_hidden
   - the help note, Answer heading metadata and colab.collapsed_sections are rewritten
   - outputs and execution counts of non-run cells are cleared
2. run the page in a fresh kernel (default: the pinned Colab-like stack; TMPDIR=/tmp), allow_errors, tags
   ignored, with every run cell holding only the question's code (the REFERENCE run: what a student gets by
   pasting the code into a new cell); a run cell is wrapped exactly when that run raises or names a line;
   then run the page as it will be stored, and require that every run cell shows the same as in the
   reference run (so neither the title line nor the wrapper changes anything a student sees)
3. refuse (exit 2) if the kernel is not the pinned stack (unless --force), if an output is too long or contains
   a memory address, or if a run block uses Colab form markup / a cell magic
4. snapshot acceptance: a stored output that was not empty and changes is shown (semantic and byte diff) and
   NOT written, exit 1, unless --accept; new outputs are written and printed for the author to review
5. store the outputs of run cells only, normalized (review_v2.normalize_outputs), and the stamp
   metadata.yr_review = {code_sha1, outputs_sha1, stack}, which lint uses to detect stale or edited outputs
"""
import copy
import difflib
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

import nbformat as nbf
from nbclient import NotebookClient

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from review_v2 import (ANSWER_HEADING, HELP_CELL, PART_CELL, RUN_CELL_METADATA, STACK_PROBE, STAMP_KEY,
                       canon_outputs, make_stamp, needs_wrap, normalize_outputs, output_problems, parse_page,
                       parse_run_cell, render_run_cell, run_block_problems, semantic, source, stable_id,
                       stack_pinned)

V2 = HERE.parent
os.environ['JUPYTER_PATH'] = str(V2 / 'kernels')
JUPYTURTLE = '/root/.venvs/yrThinkPython/yr-cache/jupyturtle.py'
COLAB_KEYS = ('executionInfo', 'outputId', 'colab')


class Refused(Exception):
    pass


def run_cell_for(q, part, multi):
    """Index of the run cell for a block (by the part letter in its title), or None."""
    if not multi:
        return q['run_cells'][0] if q['run_cells'] else None
    return next((i for i in q['run_cells'] if q['run_part'][i] == part), None)


def new_md(text, cid):
    c = nbf.v4.new_markdown_cell(text)
    c.id = cid
    return c


def reconcile(nb, q, all_changes, errors):
    """Make the run cells of question q match its run blocks (see the module docstring)."""
    cells, changes = nb.cells, []
    blocks, multi = q['run_blocks'], len(q['run_blocks']) > 1
    t = q['title'][:40]
    if q['answer'] is None:
        if blocks:
            errors.append(f"{t}: run blocks but no '{ANSWER_HEADING}' heading")
        return
    for _, part, code in blocks:
        errors.extend(f'{t}: run block {part or ""}: {p}' for p in run_block_problems(code))
    if errors:
        return
    aid = cells[q['answer']].id
    region = cells[q['answer'] + 1:q['end']]
    run_cells = {id(cells[i]): i for i in q['run_cells']}
    keep = {}                                         # block index -> run cell (object)
    used = set()
    for k, (_, part, code) in enumerate(blocks):
        ri = run_cell_for(q, part, multi)
        if ri is not None and id(cells[ri]) not in used:
            keep[k] = cells[ri]
            used.add(id(cells[ri]))
    for c in region:
        if id(c) in run_cells and id(c) not in used:
            changes.append(f'{t}: orphan run cell {c.id} deleted (its run block is gone)')
    region = [c for c in region if id(c) not in run_cells or id(c) in used]
    for k, (_, part, code) in enumerate(blocks):
        p = part if multi else None
        c = keep.get(k)
        if c is None:
            c = nbf.v4.new_code_cell(render_run_cell(code, False, p))
            c.id = stable_id(aid, 'run', p or '-')
            c.metadata = nbf.from_dict(copy.deepcopy(RUN_CELL_METADATA))
            keep[k] = c
            changes.append(f'{t}: run cell {c.id} created for {"part " + p if p else "the run block"}')
            if not multi:
                region.insert(0, c)
            continue
        info = parse_run_cell(source(c))
        want = render_run_cell(code, info['wrapped'], p)
        if info['code'] != code:
            c.source, c.outputs, c.execution_count = want, [], None
            changes.append(f'{t}: run cell {c.id} regenerated from its edited run block; outputs cleared')
        elif source(c) != want:
            c.source = want
            changes.append(f'{t}: run cell {c.id}: title / layout made canonical')
        if dict(c.metadata) != RUN_CELL_METADATA:
            c.metadata = nbf.from_dict(copy.deepcopy(RUN_CELL_METADATA))
            changes.append(f'{t}: run cell {c.id}: metadata set to cellView=form + jupyter.source_hidden')
    if multi:                                        # run cell x goes right after its '**Part x:**' cell
        region = [c for c in region if id(c) not in {id(x) for x in keep.values()}]
        for k, (_, part, _) in enumerate(blocks):
            pi = next((n for n, c in enumerate(region) if c.cell_type == 'markdown'
                       and (m := PART_CELL.match(source(c))) and m.group('part') == part), None)
            if pi is None:
                if k == 0:
                    pos = next((n for n, c in enumerate(region) if c.cell_type == 'markdown'
                                and PART_CELL.match(source(c))), len(region))
                else:
                    pos = next(n for n, c in enumerate(region) if c is keep[k - 1]) + 1
                region.insert(pos, new_md(f'**Part {part}:** TODO', stable_id(aid, 'part', part)))
                changes.append(f'{t}: "**Part {part}:** TODO" cell created (write the explanation)')
                pi = pos
            region.insert(pi + 1, keep[k])
    old_order = [id(c) for c in cells[q['answer'] + 1:q['end']]]
    if [id(c) for c in region] != old_order:
        if not any('created' in x or 'deleted' in x for x in changes):
            changes.append(f'{t}: run cells moved right after their Part cells')
        cells[q['answer'] + 1:q['end']] = region
    all_changes.extend(changes)


def static_normalize(nb):
    """Returns (changes, errors). Changes nb in place."""
    changes, errors = [], []
    for c in nb.cells:
        heading = c.cell_type == 'markdown' and source(c).strip() == ANSWER_HEADING
        for k in COLAB_KEYS + (() if heading else ('id',)):
            if k in c.metadata:
                del c.metadata[k]
                changes.append(f'cell {c.id}: Colab metadata "{k}" dropped')
    for q in reversed(parse_page(nb)):              # bottom-up, so earlier indices stay valid
        reconcile(nb, q, changes, errors)
    run_ids = {nb.cells[i].id for q in parse_page(nb) for i in q['run_cells']}
    for c in nb.cells:
        if c.cell_type == 'code' and c.id not in run_ids and (c.outputs or c.execution_count is not None):
            c.outputs, c.execution_count = [], None
            changes.append(f'code cell {c.id}: outputs cleared (only run cells store output)')
    helps = [c for c in nb.cells if c.cell_type == 'markdown' and source(c).startswith('**Using this page')]
    for c in helps:
        if source(c) != HELP_CELL or c.metadata.get('tags') != ['remove-cell']:
            c.source = HELP_CELL
            c.metadata['tags'] = ['remove-cell']
            changes.append('help note rewritten')
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
    seen = set()
    for c in nb.cells:
        if c.id in seen:
            errors.append(f'duplicate cell id {c.id}')
        seen.add(c.id)
    return changes, errors


def execute(nb, kernel):
    """Run a copy of nb like Run all but without stopping (allow_errors), tags ignored, TMPDIR=/tmp.
    Returns (executed copy, {cell index: reply status}, kernel stack)."""
    run = copy.deepcopy(nb)
    for c in run.cells:
        c.metadata.pop('tags', None)
    run.cells.append(nbf.v4.new_code_cell(STACK_PROBE))
    status = {}

    def hook(cell, cell_index, execute_reply):
        status[cell_index] = execute_reply['content']['status']

    with tempfile.TemporaryDirectory() as tmp:
        shutil.copy(JUPYTURTLE, tmp)
        NotebookClient(run, kernel_name=kernel, timeout=600, allow_errors=True, record_timing=False,
                       on_cell_executed=hook, resources={'metadata': {'path': tmp}}).execute(
            env={**os.environ, 'TMPDIR': '/tmp'})
    probe = run.cells.pop()
    status.pop(len(run.cells), None)
    stack = json.loads(''.join(o.get('text', '') for o in probe.outputs if o.output_type == 'stream') or 'null')
    return run, status, stack


def run_cell_list(nb):
    """[(question, block part, run cell index)] in page order."""
    out = []
    for q in parse_page(nb):
        multi = len(q['run_blocks']) > 1
        for _, part, code in q['run_blocks']:
            out.append((q, part if multi else None, code, run_cell_for(q, part, multi)))
    return out


def byte_diff(old, new):
    a = json.dumps(json.loads(canon_outputs(old)), indent=1, ensure_ascii=False).splitlines()
    b = json.dumps(json.loads(canon_outputs(new)), indent=1, ensure_ascii=False).splitlines()
    d = list(difflib.unified_diff(a, b, 'stored', 'new', lineterm='', n=1))
    return '\n'.join(('        ' + x)[:170] for x in d[:40]) + ('\n        ...' if len(d) > 40 else '')


def sync(nb, kernel, accept=False, force=False):
    """Returns (report lines, refusals, not_accepted, bad_status). nb is changed in place only if nothing was
    refused and every changed output was accepted."""
    work = copy.deepcopy(nb)
    old = {c.id: copy.deepcopy(c.get('outputs', [])) for c in work.cells if c.cell_type == 'code'}
    report, errors = static_normalize(work)
    if errors:
        return report, errors, [], []
    # run 1, the reference: every run cell holds only the question's code -> which ones must be wrapped
    plain = copy.deepcopy(work)
    for q, part, code, ri in run_cell_list(plain):
        plain.cells[ri].source = code
    run1, status, stack = execute(plain, kernel)
    if not stack_pinned(stack) and not force:
        return report, [f'the kernel "{kernel}" runs {stack}, not the pinned Colab-like stack: stored outputs must '
                        f'come from it (ensure_colab_venv.sh); --force writes them anyway, and check will fail'], [], []
    wrap = {}
    for q, part, code, ri in run_cell_list(work):
        wrap[ri] = needs_wrap(run1.cells[ri].outputs)
        new = render_run_cell(code, wrap[ri], part)
        if new != source(work.cells[ri]):
            report.append(f"{q['title'][:40]}: run cell {work.cells[ri].id} "
                          f"{'wrapped in run_cell' if wrap[ri] else 'unwrapped'}")
            work.cells[ri].source = new
    run, status, stack = execute(work, kernel)      # run 2, as stored: must show what the reference run showed
    for q, part, code, ri in run_cell_list(work):
        a, b = semantic(run1.cells[ri].outputs), semantic(run.cells[ri].outputs)
        if a != b:
            errors.append(f"{q['title'][:40]}: run cell {work.cells[ri].id} {'wrapped' if wrap[ri] else 'with its title'} "
                          f"shows something else than the question's code alone (alone {a!r:.150}, stored form "
                          f"{b!r:.150}){'; a value shown by the last line is not displayed when wrapped: print it' if wrap[ri] else ''}")
    not_accepted, run_idx = [], set()
    for q, part, code, ri in run_cell_list(work):
        run_idx.add(ri)
        c = work.cells[ri]
        new = normalize_outputs(run.cells[ri].outputs, old.get(c.id, []))
        errors.extend(f"{q['title'][:40]}: run cell {c.id}: {p}" for p in output_problems(new))
        before = old.get(c.id, [])
        if before and canon_outputs(before) != canon_outputs(new):
            sem = '' if semantic(before) == semantic(new) else (
                f'\n      stored: {semantic(before)!r:.300}\n      new:    {semantic(new)!r:.300}')
            not_accepted.append(f"{q['title'][:40]}: stored output of run cell {c.id} changes{sem}\n"
                                f"{byte_diff(before, new)}")
        elif not before:
            report.append(f"{q['title'][:40]}: run cell {c.id}: new output {semantic(new)!r:.300}")
        c.outputs = [nbf.from_dict(o) for o in new]
        c.execution_count = None
    for i, c in enumerate(work.cells):
        if c.cell_type == 'code' and i not in run_idx:
            c.outputs, c.execution_count = [], None
    bad = [i for i, s in status.items() if s != 'ok']
    if errors or (not_accepted and not accept):
        return report, errors, not_accepted, bad
    work.metadata[STAMP_KEY] = make_stamp(work, stack)
    nb.cells, nb.metadata = work.cells, work.metadata
    return report + [f'ACCEPTED: {x}' for x in not_accepted], [], [], bad


def main(argv):
    path = Path(argv[0])
    kernel = argv[argv.index('--kernel') + 1] if '--kernel' in argv else 'colablike'
    out = Path(argv[argv.index('--out') + 1]) if '--out' in argv else path
    nb = nbf.read(path, as_version=4)
    if '--static' in argv:
        report, errors = static_normalize(nb)
        refused, not_accepted, bad = errors, [], []
    else:
        report, refused, not_accepted, bad = sync(nb, kernel, '--accept' in argv, '--force' in argv)
    for line in report:
        print('  -', line)
    if refused:
        print('REFUSED, nothing written:\n  ! ' + '\n  ! '.join(refused))
        return 2
    if not_accepted:
        print('NOT WRITTEN: these stored outputs would change. Reread the Answer prose; if it is still right, run '
              'again with --accept:\n  * ' + '\n  * '.join(not_accepted))
        return 1
    if bad:
        print(f'  ! cells with reply status "error" (Run all would stop there): {bad}')
    nbf.validate(nb)
    nbf.write(nb, out)
    print(f'{"normalized" if "--static" in argv else "synced"} {path} -> {out}'
          f'{"" if "--static" in argv else " with kernel " + kernel}: {len(report)} change(s)')
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
