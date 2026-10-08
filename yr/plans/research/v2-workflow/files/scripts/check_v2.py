"""Prototype of `review.sh check` for the v2 layout (stored outputs, hidden-code run cells).

    python check_v2.py NB [--kernel colablike|bookvenv] [--static] [--semantic]

Static rules (no kernel; what check_notebooks.py / CI / the prep guard can run):
  S1  one '#### Answer' heading per question, saved collapsed (jp-MarkdownHeadingCollapsed, metadata.id);
      colab.collapsed_sections == the Answer heading ids, in page order
  S2  no other heading inside a question (ATX, setext, HTML <hN>; outside code fences); known page headings
  S3  run blocks only before the Answer; 2+ blocks are labelled **Part a**, **Part b**, ...; 1 block: no label
  S4  one run cell per run block (matched by the part letter in its title), no orphans; its code is exactly
      the block's code and its source is in sync's canonical form
  S5  run cells hide their code: first line '# @title Output' / '# @title Output of part x', metadata
      cellView=form and jupyter.source_hidden=true, and no other metadata (Colab adds some on save)
  S6  multi-part Answers: one '**Part x:**' cell per part, in order; run cell x right after it
  S7  code cells before an Answer: definition cells (def/class/import/assignment) and '# Your code here'
      only; in an Answer: run cells only; outside questions: setup cells only
  S8  stored outputs only on run cells; every execution_count is null
  S9  output belongs in the run cell: in an Answer of a question with run blocks, every non-python block
      (any fenced block, indented code, <pre>, data-turtle picture) must directly follow a ```python block
      in the same cell (at most one short line between them, e.g. "That displays:")
  S10 error names: each error a run cell raises is named in its part's prose or in the summary (visible, or
      in the author's invisible '<!-- error: Name -->' record); every name in a part's prose is raised by that
      part; a part's '<!-- error: -->' record lists exactly the errors it raises; summary names are raised
  S11 wrapped in run_cell exactly when the stored output is an error or names a line number
  S12 the help note is exact; tags only setup / remove-cell (help note) / no-signature; the page ends with
      '## Credits'; no (c) (r) (tm) +- in prose
  S13 write-code questions: header block + 2 or more examples, no run block; wrong-call questions: 2+
      correct calls with output; Answer ```python blocks run on their own as .py files, and a ```text block
      right after one equals its output
  S14 the sync stamp matches: no code changed since the last sync, stored outputs are exactly what it wrote,
      written on the pinned Colab-like stack; a run cell without output is allowed only then
  S15 run-cell output at most 8000 characters / 60 lines, and no memory address (changes every run)
  S16 run blocks: no Colab form markup (#@title/#@param/#@markdown), no %% cell magic, no ~~~ line,
      quotable for run_cell
  S17 stored drawings: PNG intact (png_sha1), a real PNG, twice the display size
  S18 a name that a run cell's NameError reports is not bound at module level by another cell or run block
  S19 fences: no old '```python run' marker; '~~~' fences only in run-block cells
  S20 no 'TODO' left in an Answer (sync writes '**Part x:** TODO' for a new part)
Runtime rules (fresh runs, allow_errors=True, tags ignored, TMPDIR=/tmp):
  R0  the kernel is the pinned Colab-like stack; elsewhere the byte check is impossible: the run is reported
      WEAK and fails unless --semantic is given
  R1  Run all reaches the end: no cell replies "error"
  R2  after the run nothing is visible outside collapsed Answers except setup cells' stdout
  R3  stored outputs == the fresh run: byte-identical after normalization on the pinned stack (drawings
      re-rendered unless the stored PNG is intact), the same semantically elsewhere
  R4  wrapped exactly when the fresh run raises or names a line number; definition cells display nothing
  R5  wrapping is invisible: a second run with every run cell plain shows the same (semantically)
Exit status 1 if any problem is found.
"""
import ast
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
from review_v2 import (ANSWER_HEADING, CREDITS_HEADING, ERROR_COMMENT, HELP_CELL, PLACEHOLDER, RUN_CELL_METADATA,
                       RUN_FENCE, canon_outputs, collapsed_sections_hidden, drawing_problems, error_names, errors_of,
                       heading_level, needs_wrap, normalize_outputs, output_problems, parse_page, parse_run_cell,
                       render_run_cell, run_block_problems, semantic, source, stack_pinned, stamp_problems,
                       strip_fences, title_for)
from sync_v2 import execute, run_cell_list

JUPYTURTLE = '/root/.venvs/yrThinkPython/yr-cache/jupyturtle.py'
EXAMPLE = re.compile(r'```python\n.*?```\s*(```text\n|<img\b[^>]*\bdata-turtle)', re.S)
SIGNATURE = re.compile(r'```python\n(?:\s*def \w+\(.*\):\n\s+\.\.\.\n)+')
HAZARD = re.compile(r'\((c|r|tm)\)|\+-', re.I)
ALLOWED_TAGS = {'setup', 'remove-cell', 'no-signature'}
FENCE_OPEN = re.compile(r'^ {0,3}(`{3,}|~{3,})(.*)$')


def stored_errors(cell):
    return set(errors_of(cell.get('outputs', [])))


def part_prose(nb, q):
    """{part: markdown text of that part} ({None: ...} for a single run block), plus 'summary': the markdown
    cells after the last run cell of a multi-part Answer."""
    cells = nb.cells
    md = [i for i in range(q['answer'] + 1, q['end']) if cells[i].cell_type == 'markdown']
    if len(q['run_blocks']) <= 1:
        return {None: '\n\n'.join(source(cells[i]) for i in md), 'summary': ''}
    out, cur, last_run = {'summary': ''}, None, max(q['run_cells']) if q['run_cells'] else q['end']
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


def answer_items(md):
    """Blocks of an Answer markdown cell, in order: (kind, first line, last line, info, text); kind is 'python'
    (a ```python block), 'tilde' (a ~~~ fence) or 'output' (any other fenced block, indented code, <pre>, a
    data-turtle picture)."""
    lines, items, i = md.split('\n'), [], 0
    while i < len(lines):
        line = lines[i]
        m = FENCE_OPEN.match(line)
        if m:
            fence, info = m.group(1), m.group(2).strip()
            j = i + 1
            while j < len(lines) and not re.match(r'^ {0,3}' + re.escape(fence[0]) + '{' + str(len(fence)) + r',}\s*$', lines[j]):
                j += 1
            kind = 'tilde' if fence[0] == '~' else ('python' if info.split()[:1] == ['python'] else 'output')
            items.append((kind, i, j, info, '\n'.join(lines[i + 1:j])))
            i = j + 1
            continue
        if re.search(r'<img\b[^>]*\bdata-turtle|<pre\b', line, re.I):
            items.append(('output', i, i, 'html', line))
            i += 1
            continue
        if re.match(r'^( {4}|\t)\S', line) and i > 0 and not lines[i - 1].strip():
            k = i - 1
            while k >= 0 and not lines[k].strip():
                k -= 1
            if k < 0 or not (re.match(r'^\s*([-*+]|\d+[.)])\s', lines[k]) or re.match(r'^( {2,}|\t)', lines[k])):
                j = i
                while j + 1 < len(lines) and (re.match(r'^( {4}|\t)', lines[j + 1]) or not lines[j + 1].strip()):
                    j += 1
                items.append(('output', i, j, 'indented', '\n'.join(lines[i:j + 1])))
                i = j + 1
                continue
        i += 1
    return items, lines


def python_text_pairs(md):
    """(python code, text) for each ```text block directly after a ```python block (S9's allowed layout)."""
    items, lines = answer_items(md)
    pairs = []
    for prev, it in zip(items, items[1:]):
        if prev[0] == 'python' and it[0] == 'output' and it[3] == 'text' and short_gap(lines, prev, it):
            pairs.append((prev[4], it[4]))
    return pairs


def short_gap(lines, prev, it):
    gap = [l for l in lines[prev[2] + 1:it[1]] if l.strip()]
    return len(gap) <= 1 and all(len(l) <= 100 for l in gap)


def module_bindings(src):
    """Names bound at module level by Python source (or an empty set if it does not parse)."""
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return set()
    names = set()
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(node.name)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            names.update((a.asname or a.name).split('.')[0] for a in node.names)
        else:
            for t in ast.walk(node):
                if isinstance(t, ast.Name) and isinstance(t.ctx, ast.Store):
                    names.add(t.id)
    return names


def static_checks(nb, problems):
    cells = nb.cells
    qs = parse_page(nb)
    heads = [c.id for c in cells if c.cell_type == 'markdown' and source(c).strip() == ANSWER_HEADING]
    # S12 managed cell, tags, credits, hazards
    helps = [c for c in cells if c.cell_type == 'markdown' and 'remove-cell' in c.metadata.get('tags', [])]
    if len(helps) != 1 or source(helps[0]) != HELP_CELL or helps[0].metadata.get('tags') != ['remove-cell']:
        problems.append('S12: the help note is missing or edited (must be exactly review_v2.HELP_CELL, tag remove-cell; '
                        'run sync)')
    for i, c in enumerate(cells):
        bad = set(c.metadata.get('tags', [])) - ALLOWED_TAGS
        if bad:
            problems.append(f'S12: cell {i} has tags {sorted(bad)} (allowed: {sorted(ALLOWED_TAGS)})')
        if c.cell_type == 'code' and 'remove-cell' in c.metadata.get('tags', []):
            problems.append(f'S12: code cell {i} is tagged remove-cell (only the help note is)')
        if c.cell_type == 'markdown':
            for m in HAZARD.finditer(re.sub(r'`[^`]*`', '', strip_fences(source(c)))):
                problems.append(f'S12: cell {i}: "{m.group(0)}" would be shown as a symbol on the website')
            if '```python run' in source(c):
                problems.append(f'S19: cell {i} uses the old "```python run" marker (run blocks are ~~~python fences)')
            if re.search(r'^\s{0,3}~~~', source(c), re.M) and not RUN_FENCE.match(source(c)):
                problems.append(f'S19: cell {i} ({c.id}) has a ~~~ fence but is not a run-block cell (~~~ marks run '
                                f'blocks; use ``` for other code)')
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
    # S14 stamp
    stamp = stamp_problems(nb)
    problems.extend('S14: ' + p for p in stamp)
    in_question, all_run = set(), set()
    blocks_code = {i: code for q in qs for i, _, code in q['run_blocks']}
    for q in qs:
        t = q['title'][:40]
        in_question.update(range(q['start'], q['end']))
        all_run.update(q['run_cells'])
        n_heads = sum(1 for i in range(q['start'], q['end']) if cells[i].cell_type == 'markdown'
                      and source(cells[i]).strip() == ANSWER_HEADING)
        if n_heads != 1:
            problems.append(f'S1: {t}: {n_heads} Answer headings (need exactly 1)')
        for i in range(q['start'] + 1, q['end']):
            c = cells[i]
            if c.cell_type == 'markdown' and source(c).strip() != ANSWER_HEADING and heading_level(source(c)):
                problems.append(f'S2: {t}: cell {i} contains a heading (it would end or split the Answer)')
        if q['answer'] is None:
            continue
        # S3 labels, S16 hazards
        parts = [p for _, p, _ in q['run_blocks']]
        n, multi = len(parts), len(parts) > 1
        if n == 1 and parts[0] or multi and parts != [chr(97 + k) for k in range(n)]:
            problems.append(f'S3: {t}: run block labels {parts} (1 block: none; 2+: a, b, c, ...)')
        for _, part, code in q['run_blocks']:
            problems.extend(f'S16: {t}: run block {part or ""}: {p}' for p in run_block_problems(code))
        # S4/S5/S11 run cells
        matched = set()
        for _, part, code in q['run_blocks']:
            p = part if multi else None
            cands = [i for i in q['run_cells'] if not multi or q['run_part'][i] == part]
            if not cands:
                problems.append(f'S4: {t}: no run cell for {"part " + part if p else "the run block"} (run sync)')
                continue
            ri = cands[0]
            matched.add(ri)
            c = cells[ri]
            info = parse_run_cell(source(c))
            if info['code'] != code:
                problems.append(f'S4: {t}: run cell {c.id} does not run its run block\'s code (run sync)')
            elif not run_block_problems(code) and source(c) != render_run_cell(code, info['wrapped'], p):
                problems.append(f'S5: {t}: run cell {c.id} is not in canonical form, e.g. its title "{info["title_line"]}" '
                                f'(Colab rewrites titles when the view changes; run sync)')
            meta = dict(c.metadata)
            if meta.get('cellView') != 'form' or dict(meta.get('jupyter', {})) != {'source_hidden': True}:
                problems.append(f'S5: {t}: run cell {c.id} does not hide its code (needs cellView=form and '
                                f'jupyter.source_hidden=true; has {meta})')
            elif meta != RUN_CELL_METADATA:
                problems.append(f'S5: {t}: run cell {c.id} has metadata sync would remove '
                                f'{sorted(set(meta) - set(RUN_CELL_METADATA))} (saved by Colab?): run sync')
            if needs_wrap(c.get('outputs', [])) != info['wrapped']:
                problems.append(f'S11: {t}: run cell {c.id} is {"" if info["wrapped"] else "not "}wrapped in run_cell but '
                                f'its stored output {"neither raises nor names a line" if info["wrapped"] else "raises or names a line number"}')
            problems.extend(f'S15: {t}: run cell {c.id}: {x}' for x in output_problems(c.get('outputs', [])))
            for o in c.get('outputs', []):
                if 'review_drawing' in o.get('metadata', {}):
                    problems.extend(f'S17: {t}: run cell {c.id}: {x}' for x in drawing_problems(o))
            if not c.get('outputs') and stamp:
                problems.append(f'S14: {t}: run cell {c.id} has no stored output (run sync)')
        for ri in q['run_cells']:
            if ri not in matched:
                problems.append(f'S4: {t}: run cell {cells[ri].id} has no run block (orphan; run sync)')
        # S6 placement of multi-part run cells
        if multi:
            pc = q['part_cells']
            if sorted(pc) != parts or [pc[p] for p in parts] != sorted(pc.values()):
                problems.append(f'S6: {t}: the Answer needs one "**Part x:**" cell per part, in order (has {sorted(pc)})')
            else:
                for p in parts:
                    nxt = pc[p] + 1
                    if not (nxt < len(cells) and nxt in q['run_cells'] and q['run_part'][nxt] == p):
                        problems.append(f'S6: {t}: the run cell for part {p} must come right after the '
                                        f'"**Part {p}:**" cell (run sync)')
        # S7 code cells
        for i in q['other_code']:
            c = cells[i]
            if i > q['answer']:
                problems.append(f'S7: {t}: code cell {i} inside the Answer is not a run cell')
            elif source(c).strip() != PLACEHOLDER and not definition_only(source(c)):
                problems.append(f'S7: {t}: code cell {i} before the Answer is neither "# Your code here" nor a '
                                f'definition cell (def/class/import/assignment only): question code belongs in a '
                                f'~~~python run block')
        for i in range(q['answer'], q['end']):
            if cells[i].cell_type == 'markdown' and RUN_FENCE.match(source(cells[i])):
                problems.append(f'S3: {t}: a run block inside the Answer (cell {i})')
            if cells[i].cell_type == 'markdown' and re.search(r'\bTODO\b', source(cells[i])):
                problems.append(f'S20: {t}: cell {i} still says TODO (write the explanation)')
        # S9 output belongs in the run cell
        if n:
            for i in q['answer_md']:
                items, lines = answer_items(source(cells[i]))
                for k, it in enumerate(items):
                    if it[0] != 'output':
                        continue
                    prev = items[k - 1] if k else None
                    if not (prev and prev[0] == 'python' and short_gap(lines, prev, it)):
                        problems.append(f'S9: {t}: cell {i} ({cells[i].id}) has an output block ("{it[4][:40]}") that does '
                                        f'not follow a ```python block: the question\'s output is shown by its run cell, '
                                        f'so delete the block')
        # S10 error names, per part
        prose = part_prose(nb, q)
        all_err = set().union(*[stored_errors(cells[ri]) for ri in q['run_cells']]) if q['run_cells'] else set()
        summary_names = error_names(prose.get('summary', ''))
        for _, part, code in q['run_blocks']:
            p = part if multi else None
            ri = next((i for i in q['run_cells'] if not multi or q['run_part'][i] == part), None)
            if ri is None:
                continue
            raised, text = stored_errors(cells[ri]), prose.get(p, '')
            named = error_names(text)
            where = f'part {p}' if p else 'the code'
            for e in sorted(raised - named - summary_names):
                problems.append(f'S10: {t}: {where} raises {e}, but the Answer does not name it (in the prose, or as '
                                f'"<!-- error: {e} -->")')
            for e in sorted(named - raised):
                problems.append(f'S10: {t}: the Answer\'s text for {where} names {e}, but {where} does not raise it')
            for m in ERROR_COMMENT.finditer(text):
                rec = set(re.split(r'[\s,]+', m.group('names').strip()))
                if rec != raised:
                    problems.append(f'S10: {t}: the record "{m.group(0)}" for {where} does not match the errors it '
                                    f'raises {sorted(raised) or "(none)"}')
        for e in sorted(summary_names - all_err):
            problems.append(f'S10: {t}: the summary names {e}, which no part raises')
        # S18 NameError names stay unbound
        for ri in q['run_cells']:
            for o in cells[ri].get('outputs', []):
                m = o['output_type'] == 'error' and o['ename'] == 'NameError' and re.search(r"name '(\w+)'", o['evalue'])
                if not m:
                    continue
                name = m.group(1)
                for j, c in enumerate(cells):
                    if j == ri or j in q['run_cells']:
                        continue
                    src = blocks_code.get(j) if c.cell_type == 'markdown' else (
                        parse_run_cell(source(c)) or {'code': source(c)})['code'] if c.cell_type == 'code' else None
                    if src and name in module_bindings(src):
                        problems.append(f'S18: {t}: run cell {cells[ri].id}\'s answer is "NameError: {name}", but cell '
                                        f'{j} ({c.id}) defines {name}, so after Run all the answer would change')
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
        if c.get('execution_count') is not None or any(o.get('execution_count') is not None for o in c.outputs):
            problems.append(f'S8: cell {i}: execution_count is stored (must be null)')
        if c.outputs and i not in all_run:
            problems.append(f'S8: cell {i} ({c.id}) has stored output but is not a run cell')
        if i not in in_question and 'setup' not in c.metadata.get('tags', []):
            problems.append(f'S7: code cell {i} outside the questions is not a setup cell')
    return qs


def answer_blocks_standalone(nb, qs, problems):
    with tempfile.TemporaryDirectory() as tmp:
        shutil.copy(JUPYTURTLE, tmp)
        for q in qs:
            k = 0
            for i in q['answer_md']:
                md = source(nb.cells[i])
                pairs = dict(python_text_pairs(md))
                for it in answer_items(md)[0]:
                    if it[0] != 'python':
                        continue
                    k += 1
                    f = Path(tmp) / f'answer_{k}.py'
                    f.write_text(it[4])
                    r = subprocess.run([sys.executable, f.name], cwd=tmp, capture_output=True, text=True, timeout=120)
                    if r.returncode:
                        problems.append(f"S13: {q['title'][:40]}: Answer code block {k} does not run on its own: "
                                        f"{(r.stderr.strip().splitlines() or ['?'])[-1]}")
                    elif it[4] in pairs and r.stdout.rstrip('\n') != pairs[it[4]].rstrip('\n'):
                        problems.append(f"S13: {q['title'][:40]}: the ```text block after Answer code block {k} is not "
                                        f"what it displays ({r.stdout.strip()[:60]!r})")


def runtime_checks(nb, qs, kernel, problems, semantic_ok=False):
    run, status, stack = execute(nb, kernel)
    pinned = stack_pinned(stack)
    if not pinned:
        msg = (f'R0: WEAK: kernel "{kernel}" runs {stack}, not the pinned Colab-like stack: outputs compared '
               f'semantically only (tracebacks and line numbers not verified)')
        if semantic_ok:
            print('  note:', msg)
        else:
            problems.append(msg + '; pass --semantic to accept this')
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
    for q, part, code, ri in run_cell_list(nb):
        if ri is None:
            continue
        t = q['title'][:40]
        stored = nb.cells[ri].outputs
        fresh = normalize_outputs(run.cells[ri].outputs, stored)
        if pinned and canon_outputs(stored) != canon_outputs(fresh):
            problems.append(f'R3: {t}: stored output of run cell {nb.cells[ri].id} differs from a fresh run on the '
                            f'pinned stack: stored {semantic(stored)!r:.120} fresh {semantic(fresh)!r:.120} '
                            f'(run sync, and read its diff)')
        elif not pinned and semantic(stored) != semantic(fresh):
            problems.append(f'R3: {t}: stored output of run cell {nb.cells[ri].id} differs semantically from a fresh '
                            f'run on {kernel}: stored {semantic(stored)!r:.150} fresh {semantic(fresh)!r:.150}')
        wrapped = parse_run_cell(source(nb.cells[ri]))['wrapped']
        if wrapped != needs_wrap(fresh):
            problems.append(f'R4: {t}: run cell {nb.cells[ri].id} wrapped={wrapped} but the fresh run '
                            f'{"neither raises nor names a line" if wrapped else "raises or names a line number"}')
    for q in qs:
        for i in q['other_code']:
            if q['answer'] is not None and i < q['answer'] and source(nb.cells[i]).strip() != PLACEHOLDER \
                    and run.cells[i].outputs:
                problems.append(f"R4: {q['title'][:40]}: definition cell {i} displays or raises something")
    # R5: the same page with every run cell plain
    plain = nbf.from_dict(json.loads(json.dumps(nb)))
    wrapped_any = False
    for q, part, code, ri in run_cell_list(plain):
        if ri is not None and parse_run_cell(source(plain.cells[ri]))['wrapped']:
            plain.cells[ri].source = render_run_cell(code, False, part)
            wrapped_any = True
    if wrapped_any:
        run2, _, _ = execute(plain, kernel)
        for q, part, code, ri in run_cell_list(nb):
            if ri is not None and semantic(nb.cells[ri].outputs) != semantic(run2.cells[ri].outputs):
                problems.append(f"R5: {q['title'][:40]}: run cell {nb.cells[ri].id} shows something else when it is "
                                f"not wrapped: stored {semantic(nb.cells[ri].outputs)!r:.120} plain "
                                f"{semantic(run2.cells[ri].outputs)!r:.120}")


def check(nb, kernel='colablike', static_only=False, semantic_ok=False):
    problems = []
    qs = static_checks(nb, problems)
    if not static_only:
        answer_blocks_standalone(nb, qs, problems)
        runtime_checks(nb, qs, kernel, problems, semantic_ok)
    return problems


def main(argv):
    path = argv[0]
    kernel = argv[argv.index('--kernel') + 1] if '--kernel' in argv else 'colablike'
    nb = nbf.read(path, as_version=4)
    problems = check(nb, kernel, '--static' in argv, '--semantic' in argv)
    for p in problems:
        print('  -', p)
    mode = ', static' if '--static' in argv else (', semantic accepted' if '--semantic' in argv else '')
    print(f'{"OK" if not problems else str(len(problems)) + " problem(s)"}: {path} [{kernel}{mode}]')
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
