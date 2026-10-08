"""Prototype of `review.sh check` for the v2 layout (stored outputs, hidden-code run cells).

    python check_v2.py NB [--kernel colablike|bookvenv] [--static]

Static rules (no kernel):
  S1  one '#### Answer' heading per question, saved collapsed (jp-MarkdownHeadingCollapsed, metadata.id);
      colab.collapsed_sections == the Answer heading ids, in page order
  S2  no other heading inside a question (ATX, setext, HTML <hN>; outside code fences)
  S3  run blocks only before the Answer; 2+ blocks are labelled **Part a**, **Part b**, ...; 1 block: no label
  S4  one run cell per run block, in order, whose code is exactly the block's code (sync was run)
  S5  run cells hide their code: '# @title Output[ of part x] { display-mode: "form" }', cellView form,
      jupyter.source_hidden
  S6  multi-part Answers: one '**Part x:**' cell per part, in order; run cell x right after it
  S7  code cells before an Answer: definition cells (def/class/import/assignment) and '# Your code here'
      only; in an Answer: run cells only; outside questions: setup cells only
  S8  stored outputs only on run cells, none on other cells; every execution_count is null
  S9  no duplicated output: no ```text block / error line / data-turtle picture in an Answer that repeats
      what a run cell of the question shows
  S10 error names: each error a run cell raises is named in its part's prose, and every error name in an
      Answer's prose is raised by that part's run cell (summary cells: by any run cell of the question)
  S11 wrapped in run_code exactly when the stored output is an error
  S12 managed cells (help note, run_code) are exact; tags only setup / remove-cell / no-signature;
      the page ends with '## Credits'; no (c) (r) (tm) +- in prose
  S13 write-code questions: header block + 2 or more examples, no run block; wrong-call questions: 2+
      correct calls with output; Answer ```python blocks run on their own as .py files
Runtime rules (one fresh run, allow_errors=True, tags ignored):
  R1  Run all reaches the end: no cell replies "error"
  R2  after the run nothing is visible outside collapsed Answers except setup cells' stdout
  R3  stored outputs == the fresh run: byte-identical after normalization on the stack that wrote them
      (colablike), the same semantically (text, error kind and message, displayed data) on the other
  R4  wrapped exactly when the fresh run raises; definition cells display nothing and raise nothing
Exit status 1 if any problem is found.
"""
import ast
import copy
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import nbformat as nbf

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from review_v2 import (ANSWER_HEADING, CREDITS_HEADING, HELP_CELL, PLACEHOLDER, RUN_CELL_METADATA, RUN_CODE_CELL,
                       collapsed_sections_hidden, error_names, heading_level, normalize_outputs, parse_page,
                       parse_run_cell, semantic, source, strip_fences, title_for)

os.environ['JUPYTER_PATH'] = str(HERE.parent / 'kernels')
JUPYTURTLE = '/root/.venvs/yrThinkPython/yr-cache/jupyturtle.py'
TEXT_BLOCK = re.compile(r'```text\n(.*?)\n```', re.S)
PY_BLOCK = re.compile(r'```python\n(.*?)```', re.S)
EXAMPLE = re.compile(r'```python\n.*?```\s*(```text\n|<img\b[^>]*\bdata-turtle)', re.S)
SIGNATURE = re.compile(r'```python\n(?:\s*def \w+\(.*\):\n\s+\.\.\.\n)+')
HAZARD = re.compile(r'\((c|r|tm)\)|\+-', re.I)
ALLOWED_TAGS = {'setup', 'remove-cell', 'no-signature'}


def stored_errors(cell):
    return {o['ename'] for o in cell.get('outputs', []) if o['output_type'] == 'error'}


def stdout_of(cell):
    return ''.join(s[1] for s in semantic(cell.get('outputs', [])) if s[0] == 'stream:stdout').rstrip('\n')


def has_drawing(cell):
    return any(s[0] == 'drawing' for s in semantic(cell.get('outputs', [])))


def part_prose(nb, q):
    """{part: markdown text of that part} ({None: ...} for a single run block), plus 'summary': the markdown
    cells after the last run cell of a multi-part Answer."""
    cells = nb.cells
    md = [i for i in range(q['answer'] + 1, q['end']) if cells[i].cell_type == 'markdown']
    if len(q['run_blocks']) <= 1:
        return {None: '\n\n'.join(source(cells[i]) for i in md), 'summary': ''}
    out, cur, last_run = {'summary': ''}, None, q['run_cells'][-1] if q['run_cells'] else q['end']
    for i in md:
        m = re.match(r'\*\*Part ([a-z]):\*\*', source(cells[i]))
        cur = m.group(1) if m else cur
        key = 'summary' if i > last_run else cur
        out[key] = out.get(key, '') + '\n\n' + source(cells[i])
    return out


def definition_only(src):
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return False
    return all(isinstance(s, (ast.FunctionDef, ast.ClassDef, ast.Import, ast.ImportFrom, ast.Assign)) for s in tree.body)


def static_checks(nb, problems):
    cells = nb.cells
    qs = parse_page(nb)
    heads = [c.id for c in cells if c.cell_type == 'markdown' and source(c).strip() == ANSWER_HEADING]
    # S12 managed cells, tags, credits, hazards
    if sum(source(c) == HELP_CELL and c.metadata.get('tags') == ['remove-cell'] for c in cells) != 1:
        problems.append('S12: the help note is missing or edited (must be exactly review_v2.HELP_CELL, tag remove-cell)')
    if sum(source(c) == RUN_CODE_CELL and c.metadata.get('tags') == ['setup', 'remove-cell'] for c in cells) != 1:
        problems.append('S12: the run_code cell is missing or edited (must be exactly review_v2.RUN_CODE_CELL)')
    for i, c in enumerate(cells):
        bad = set(c.metadata.get('tags', [])) - ALLOWED_TAGS
        if bad:
            problems.append(f'S12: cell {i} has tags {sorted(bad)} (allowed: {sorted(ALLOWED_TAGS)})')
        if c.cell_type == 'markdown':
            for m in HAZARD.finditer(re.sub(r'`[^`]*`', '', strip_fences(source(c)))):
                problems.append(f'S12: cell {i}: "{m.group(0)}" would be shown as a symbol on the website')
    # S2 page-level headings: a heading cell must be the title, a known section or a question heading
    known = re.compile(r'(# \S|## (Concepts covered|Questions|Credits)\s*(\n|$)|### Question \d+ \((easy|medium|hard)\): )')
    for i, c in enumerate(cells):
        lev = heading_level(source(c)) if c.cell_type == 'markdown' else None
        if lev is not None and lev <= 3 and not (known.match(source(c)) and heading_level(
                source(c).split('\n', 1)[1] if '\n' in source(c) else '') in (None, 4, 5, 6)):
            problems.append(f'S2: cell {i} ({c.id}) has an unexpected heading (level {lev}): it would end a question '
                            f'or an Answer early')
    credit = [c for c in cells if c.cell_type == 'markdown' and source(c).startswith(CREDITS_HEADING + '\n')]
    if not credit or cells[-1] is not credit[0]:
        problems.append("S12: the page must end with a '## Credits' cell")
    # S1 collapse metadata
    for c in cells:
        if c.cell_type == 'markdown' and source(c).strip() == ANSWER_HEADING and \
                dict(c.metadata) != {'id': c.id, 'jp-MarkdownHeadingCollapsed': True}:
            problems.append(f'S1: Answer heading {c.id} is not saved collapsed (metadata {dict(c.metadata)})')
    if nb.metadata.get('colab', {}).get('collapsed_sections') != heads:
        problems.append('S1: colab.collapsed_sections is not exactly the Answer heading ids in page order')
    in_question = set()
    for q in qs:
        t = q['title'][:40]
        in_question.update(range(q['start'], q['end']))
        n_heads = sum(1 for i in range(q['start'], q['end']) if cells[i].cell_type == 'markdown'
                      and source(cells[i]).strip() == ANSWER_HEADING)
        if n_heads != 1:
            problems.append(f'S1: {t}: {n_heads} Answer headings (need exactly 1)')
        # S2 headings
        for i in range(q['start'] + 1, q['end']):
            c = cells[i]
            if c.cell_type == 'markdown' and source(c).strip() != ANSWER_HEADING and heading_level(source(c)):
                problems.append(f'S2: {t}: cell {i} contains a heading (it would end or split the Answer)')
        if q['answer'] is None:
            continue
        # S3 labels
        parts = [p for _, p, _ in q['run_blocks']]
        n = len(parts)
        if n == 1 and parts[0] or n > 1 and parts != [chr(97 + k) for k in range(n)]:
            problems.append(f'S3: {t}: run block labels {parts} (1 block: none; 2+: a, b, c, ...)')
        for i in range(q['answer'], q['end']):
            if cells[i].cell_type == 'markdown' and '```python run' in source(cells[i]):
                problems.append(f'S3: {t}: a run block inside the Answer (cell {i})')
        # S4/S5 run cells
        if len(q['run_cells']) != n:
            problems.append(f'S4: {t}: {n} run blocks but {len(q["run_cells"])} run cells (run sync)')
        for (bi, part, code), ri in zip(q['run_blocks'], q['run_cells']):
            c = cells[ri]
            title, rcode, wrapped = parse_run_cell(source(c))
            if rcode != code:
                problems.append(f'S4: {t}: run cell {c.id} does not run its run block\'s code (run sync)')
            if title != title_for(part if n > 1 else None):
                problems.append(f'S5: {t}: run cell {c.id} title "{title}" (want "{title_for(part if n > 1 else None)}")')
            if dict(c.metadata) != RUN_CELL_METADATA:
                problems.append(f'S5: {t}: run cell {c.id} does not hide its code (metadata {dict(c.metadata)})')
            # S11 wrapped iff stored error
            if bool(stored_errors(c)) != wrapped:
                problems.append(f'S11: {t}: run cell {c.id} is {"" if wrapped else "not "}wrapped in run_code but its '
                                f'stored output {"has no" if wrapped else "is an"} error')
        # S6 placement of multi-part run cells
        if n > 1:
            pc = q['part_cells']
            if sorted(pc) != parts or [pc[p] for p in parts] != sorted(pc.values()):
                problems.append(f'S6: {t}: the Answer needs one "**Part x:**" cell per part, in order (has {sorted(pc)})')
            else:
                for k, ri in enumerate(q['run_cells']):
                    if ri != pc[parts[k]] + 1:
                        problems.append(f'S6: {t}: the run cell for part {parts[k]} must come right after the '
                                        f'"**Part {parts[k]}:**" cell')
        # S7 code cells
        for i in q['other_code']:
            c = cells[i]
            if i > q['answer']:
                problems.append(f'S7: {t}: code cell {i} inside the Answer is not a run cell')
            elif source(c).strip() != PLACEHOLDER and not definition_only(source(c)):
                problems.append(f'S7: {t}: code cell {i} before the Answer is neither "# Your code here" nor a '
                                f'definition cell (def/class/import/assignment only): question code belongs in a '
                                f'```python run block')
        # S9 duplicated output
        answer_md = '\n'.join(source(cells[i]) for i in q['answer_md'])
        blocks = [b.strip() for b in TEXT_BLOCK.findall(answer_md)]
        for ri in q['run_cells']:
            out = stdout_of(cells[ri])
            if out and out in blocks:
                problems.append(f'S9: {t}: a ```text block in the Answer repeats the output of run cell {cells[ri].id}')
            for o in cells[ri].get('outputs', []):
                if o['output_type'] == 'error':
                    line = f"{o['ename']}: {semantic([o])[0][2]}"
                    if any(line in b for b in blocks):
                        problems.append(f'S9: {t}: a ```text block in the Answer repeats the error "{line[:50]}"')
            if has_drawing(cells[ri]) and re.search(r'<img\b[^>]*\bdata-turtle', strip_fences(answer_md)) and \
                    not PY_BLOCK.search(answer_md):
                problems.append(f'S9: {t}: a data-turtle picture in the Answer repeats the drawing of run cell {cells[ri].id}')
        # S10 error names, per part
        prose = part_prose(nb, q)
        keys = [None] if n == 1 else parts
        all_err = set().union(*[stored_errors(cells[ri]) for ri in q['run_cells']]) if q['run_cells'] else set()
        for k, ri in zip(keys, q['run_cells']):
            raised = stored_errors(cells[ri])
            named = error_names(prose.get(k, ''))
            for e in sorted(raised - named):
                problems.append(f'S10: {t}: {"part " + k if k else "the code"} raises {e}, but the Answer\'s prose '
                                f'{"for part " + k if k else ""} does not name it')
            for e in sorted(named - raised):
                problems.append(f'S10: {t}: the Answer\'s prose {"for part " + k if k else ""} names {e}, but '
                                f'{"part " + k if k else "the code"} does not raise it')
        for e in sorted(error_names(prose.get('summary', '')) - all_err):
            problems.append(f'S10: {t}: the summary names {e}, which no part raises')
        if n == 0 and q['run_cells']:
            problems.append(f'S4: {t}: run cells but no run block')
        # S13 write-code / wrong calls
        question = '\n'.join(source(cells[i]) for i in range(q['start'], q['answer']) if cells[i].cell_type == 'markdown')
        placeholders = [i for i in q['other_code'] if source(cells[i]).strip() == PLACEHOLDER]
        n_examples = len(EXAMPLE.findall(question))
        if placeholders:
            if n:
                problems.append(f'S13: {t}: a write-code question must not have run blocks')
            if n_examples < 2:
                problems.append(f'S13: {t}: write-code question shows {n_examples} example(s) with output; needs 2+')
            if not SIGNATURE.search(question) and not any('no-signature' in cells[i].metadata.get('tags', [])
                                                           for i in placeholders):
                problems.append(f'S13: {t}: write-code question does not show the function header')
        defines = any(re.search(r'^\s*def ', source(cells[i]), re.M) for i in q['other_code'] if i < q['answer'])
        if defines and all_err and n_examples < 2:
            problems.append(f'S13: {t}: wrong-call question shows {n_examples} correct call(s) with output; needs 2+')
    # S7/S8 outside questions and outputs
    for i, c in enumerate(cells):
        if c.cell_type != 'code':
            continue
        is_run = any(i in q['run_cells'] for q in qs)
        if c.get('execution_count') is not None or any(o.get('execution_count') is not None for o in c.outputs):
            problems.append(f'S8: cell {i}: execution_count is stored (must be null)')
        if c.outputs and not is_run:
            problems.append(f'S8: cell {i} ({c.id}) has stored output but is not a run cell')
        if i not in in_question and 'setup' not in c.metadata.get('tags', []):
            problems.append(f'S7: code cell {i} outside the questions is not a setup cell')
    return qs


def answer_blocks_standalone(nb, qs, problems):
    with tempfile.TemporaryDirectory() as tmp:
        shutil.copy(JUPYTURTLE, tmp)
        for q in qs:
            md = ''.join(source(nb.cells[i]) for i in q['answer_md'])
            for k, block in enumerate(PY_BLOCK.findall(md), 1):
                f = Path(tmp) / f'answer_{k}.py'
                f.write_text(block)
                r = subprocess.run([sys.executable, f.name], cwd=tmp, capture_output=True, text=True, timeout=120)
                if r.returncode:
                    problems.append(f"S13: {q['title'][:40]}: Answer code block {k} does not run on its own: "
                                    f"{(r.stderr.strip().splitlines() or ['?'])[-1]}")


def runtime_checks(nb, qs, kernel, problems):
    from nbclient import NotebookClient
    run = copy.deepcopy(nb)
    for c in run.cells:
        c.metadata.pop('tags', None)
    status = {}
    with tempfile.TemporaryDirectory() as tmp:
        shutil.copy(JUPYTURTLE, tmp)
        NotebookClient(run, kernel_name=kernel, timeout=600, allow_errors=True, record_timing=False,
                       resources={'metadata': {'path': tmp}},
                       on_cell_executed=lambda cell, cell_index, execute_reply: status.__setitem__(
                           cell_index, execute_reply['content']['status'])).execute()
    for i, s in sorted(status.items()):
        if s != 'ok':
            problems.append(f'R1: Run all would stop at cell {i} ({nb.cells[i].id}): reply status "{s}"')
    hidden = collapsed_sections_hidden(nb)
    for i, c in enumerate(run.cells):
        if c.cell_type == 'code' and c.outputs and i not in hidden:
            setup_stdout = 'setup' in nb.cells[i].metadata.get('tags', []) and all(
                o['output_type'] == 'stream' and o['name'] == 'stdout' for o in c.outputs)
            if not setup_stdout:
                problems.append(f'R2: cell {i} ({c.id}) shows output outside a collapsed Answer after Run all')
    for q in qs:
        t = q['title'][:40]
        for ri in q['run_cells']:
            stored = nb.cells[ri].outputs
            fresh = normalize_outputs(run.cells[ri].outputs, stored)
            if kernel == 'colablike':
                if json.dumps(stored, sort_keys=True) != json.dumps(fresh, sort_keys=True):
                    problems.append(f'R3: {t}: stored output of run cell {nb.cells[ri].id} differs from a fresh run '
                                    f'(run sync): stored {semantic(stored)!r:.120} fresh {semantic(fresh)!r:.120}')
            elif semantic(stored) != semantic(fresh):
                problems.append(f'R3: {t}: stored output of run cell {nb.cells[ri].id} differs semantically from a '
                                f'fresh run on {kernel}: stored {semantic(stored)!r:.150} fresh {semantic(fresh)!r:.150}')
            _, _, wrapped = parse_run_cell(source(nb.cells[ri]))
            if wrapped != any(o['output_type'] == 'error' for o in fresh):
                problems.append(f'R4: {t}: run cell {nb.cells[ri].id} wrapped={wrapped} but the fresh run '
                                f'{"raises" if not wrapped else "does not raise"}')
        for i in q['other_code']:
            if i < q['answer'] and source(nb.cells[i]).strip() != PLACEHOLDER and run.cells[i].outputs:
                problems.append(f'R4: {t}: definition cell {i} displays or raises something')


def check(nb, kernel='colablike', static_only=False):
    problems = []
    qs = static_checks(nb, problems)
    if not static_only:
        answer_blocks_standalone(nb, qs, problems)
        runtime_checks(nb, qs, kernel, problems)
    return problems


def main(argv):
    path = argv[0]
    kernel = argv[argv.index('--kernel') + 1] if '--kernel' in argv else 'colablike'
    nb = nbf.read(path, as_version=4)
    problems = check(nb, kernel, '--static' in argv)
    for p in problems:
        print('  -', p)
    print(f'{"OK" if not problems else str(len(problems)) + " problem(s)"}: {path} [{kernel}{", static" if "--static" in argv else ""}]')
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
