"""`review.sh check`: verify a review page. Fails if `sync` would change anything, or a format rule is broken.

    python check_review.py NB [JUPYTURTLE] [--kernel colablike] [--static] [--renumbered] [--cache DIR]

Pages in the old format (<details> Answers) are checked by legacy_check_review.py, as before.

For converted pages (yr/README.md, "Format rules"; the numbers are the rule numbers there):
Static (no kernel; --static runs only these):
  1  question headings "### Question N (level): kind"; N is digits and an optional letter, unique on the page
  2  stable numbers: every question number of the published page (git: v3) is still there, on the same question,
     unless the page was renumbered with `review_cells.py renumber`; no "Nb" while Question N has a part b
  3  one Answer heading per question, saved collapsed; no other heading inside a question
  4  run blocks (~~~python) only before the Answer; one block: no label; several: **Part a**, **Part b**, ...
  5  code cells before an Answer: definition cells (define or assign only) and '# Your code here'
  6  code cells inside an Answer: run cells only (hidden code, canonical title and metadata)
  7  in a question, a ```text block or a picture appears only inside a generated region
  8  every error a run cell shows is named by <!--=error--> in its part's prose or the summary; any other error
     name in a part's prose is one that part raises
  9  stored outputs only on run cells; the sync stamp matches (no hand edits); limits; drawings intact
  10 markers well formed: inline value markers never start a line; block markers alone on their line; no `?` left
  13 a NameError answer stays true: no other cell binds that name
  14 the page ends with the credits; tags only setup, no-signature, and remove-cell on the help note
  16 no TODO left; no (c) (r) (tm) +- in prose (the website would turn them into symbols)
Runtime (a fresh sync on the pinned kernel, not written):
  11 sync would change nothing: run cells, stored outputs, generated regions, import lines, values, the stamp
  R1 Run all reaches the end (no cell replies "error")
  R2 after Run all nothing is visible outside closed Answers except the setup cells' printed lines
  R4 definition cells display nothing
  12 C4: every ```python block of an Answer imports the names it uses from the setup cell (static), and, copied
     into a new cell after Run all, runs and shows what the page says: a solution reproduces every example of the
     functions it defines; a fix or "what if" block shows its generated output; a doctest prints no failure
Notes (printed, not failures): names that more than one question assigns (a fix that uses one keeps its own
input line, E10).
Exit status 1 if any problem is found.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

import nbformat as nbf

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import review_format as rf  # noqa: E402
import sync_review as sr  # noqa: E402
from review_format import md_tokens, source  # noqa: E402

ALLOWED_TAGS = {'setup', 'remove-cell', 'no-signature'}
HAZARD = re.compile(r'\((c|r|tm)\)|\+-', re.I)
KNOWN_HEADINGS = ('## Concepts covered', '## Questions', rf.CREDITS_HEADING)


def published_numbers(path):
    """{number: heading cell id} of the page as published on v3, or None if unknown (no git, a new page)."""
    try:
        root = Path(subprocess.run(['git', '-C', str(path.parent), 'rev-parse', '--show-toplevel'],
                                   capture_output=True, text=True, check=True).stdout.strip())
        rel = path.resolve().relative_to(root)
        for ref in ('v3', 'origin/v3'):
            r = subprocess.run(['git', '-C', str(root), 'show', f'{ref}:{rel}'], capture_output=True, text=True)
            if r.returncode == 0:
                nb = json.loads(r.stdout)
                return {q['number']: nb['cells'][q['heading']].get('id') for q in rf.parse_page(nb)}, nb
    except (subprocess.CalledProcessError, ValueError, FileNotFoundError):
        pass
    return None, None


def static_checks(nb, path, problems, renumbered=False):
    cells = nb['cells']
    qs = rf.parse_page(nb)
    # 14: tags, credits, help note
    for i, c in enumerate(cells):
        bad = set(rf.tags(c)) - ALLOWED_TAGS
        if bad:
            problems.append(f'14: cell {i} has tags {sorted(bad)} (allowed: {sorted(ALLOWED_TAGS)})')
        if 'remove-cell' in rf.tags(c) and not rf.is_help_note(c):
            problems.append(f'14: cell {i} is tagged remove-cell (only the help note is)')
    if not cells or source(cells[-1]) != rf.CREDITS:
        problems.append('14: the page must end with the credits cell exactly (run sync)')
    if [c for c in cells if rf.is_help_note(c) and source(c) == rf.HELP_NOTE] == []:
        problems.append('14: the help note is missing or edited (run sync)')
    if [c for c in cells if rf.is_helper_cell(c) and source(c) == rf.HELPER_CELL] == []:
        problems.append('14: the helper cell (run_code) is missing or edited (run sync)')
    # 16, 10: prose rules and markers
    for i, c in enumerate(cells):
        if c['cell_type'] != 'markdown':
            continue
        md = source(c)
        prose = re.sub(r'`[^`\n]*`', '', rf.strip_fences(md))
        for m in HAZARD.finditer(re.sub(r'<[^>]+>', '', prose)):
            problems.append(f'16: cell {i}: "{m.group(0)}" would be shown as a symbol on the website')
        problems.extend(f'10: cell {i} ({c.get("id")}): {p}' for p in rf.marker_problems(md))
        for s, e, m, kind, expr in rf.inline_markers(md):
            if m.group('val').strip() == '?':
                problems.append(f'10: cell {i}: a value marker still shows `?` (run sync)')
        if re.search(r'```python run\b', md):
            problems.append(f'4: cell {i} uses the old "```python run" marker (run blocks are ~~~python fences)')
        if re.search(r'^ {0,3}~~~', md, re.M) and not rf.RUN_FENCE.match(md):
            problems.append(f'4: cell {i} ({c.get("id")}) has a ~~~ fence but is not a run-block cell')
        lev = rf.heading_level(md)
        first = md.lstrip().split('\n')[0]
        if lev is not None and lev <= 3 and i > 0 and not first.startswith(KNOWN_HEADINGS) \
                and not rf.QUESTION_LINE.match(first):
            problems.append(f'3: cell {i} ({c.get("id")}) has an unexpected heading (level {lev}): it would end a question')
    # 1, 2: question numbers
    numbers = [q['number'] for q in qs]
    for q in qs:
        if not rf.QUESTION_HEADING.match(q['title'].join(['### ', ''])):
            problems.append(f'1: heading "{q["title"][:50]}" is not "### Question N (level): kind"')
    for n in sorted({n for n in numbers if numbers.count(n) > 1}):
        problems.append(f'1: Question {n} appears {numbers.count(n)} times')
    for q in qs:
        n = q['number']
        if n[-1].isalpha():
            base = next((x for x in qs if x['number'] == n[:-1]), None)
            if base and any(p == n[-1] for _, p, _ in base['run_blocks']):
                problems.append(f'2: Question {n} clashes with Part {n[-1]} of Question {n[:-1]} '
                                f'("Output of Question {n}" would name both): use another letter')
    pub, pub_nb = published_numbers(Path(path))
    if pub is not None and not renumbered:
        if (pub_nb or {}).get('metadata', {}).get(rf.STAMP_KEY, {}).get('renumbered') != \
                nb['metadata'].get(rf.STAMP_KEY, {}).get('renumbered'):
            print('  note: the page was renumbered since it was published; stable-number check skipped')
        else:
            now = {q['number']: cells[q['heading']].get('id') for q in qs}
            for n, hid in pub.items():
                if n not in now:
                    problems.append(f'2: published Question {n} is gone (numbers stay fixed during a semester; '
                                    f'renumber only between semesters: review_cells.py renumber)')
                elif hid and now[n] != hid:
                    problems.append(f'2: Question {n} is now a different question (its heading cell changed from '
                                    f'{hid} to {now[n]}); give the new question a new number (e.g. {n}b)')
    # 3-8 per question
    for q in qs:
        t = q['title'][:40]
        heads = [i for i in range(q['start'] + 1, q['end']) if cells[i]['cell_type'] == 'markdown'
                 and source(cells[i]).strip() == rf.ANSWER_HEADING]
        if len(heads) != 1:
            problems.append(f'3: {t}: {len(heads)} Answer headings (need exactly 1)')
        for i in range(q['start'] + 1, q['end']):
            c = cells[i]
            if c['cell_type'] == 'markdown' and source(c).strip() != rf.ANSWER_HEADING and rf.heading_level(source(c)):
                problems.append(f'3: {t}: cell {i} contains a heading (it would end or split the Answer)')
        if q['answer'] is not None and (cells[q['answer']]['metadata'].get('jp-MarkdownHeadingCollapsed') is not True
                                        or cells[q['answer']].get('id') not in
                                        nb['metadata'].get('colab', {}).get('collapsed_sections', [])):
            problems.append(f'3: {t}: the Answer is not saved collapsed (run sync)')
        for i in q['defs']:
            if not rf.definition_cell_ok(source(cells[i])):
                problems.append(f'5: {t}: code cell {i} before the Answer is neither "# Your code here" nor a definition '
                                f'cell (only def, class, import and assignments; put the question\'s code in a ~~~python block)')
        for i in q['other_code']:
            problems.append(f'6: {t}: code cell {i} inside the Answer is not a run cell')
        for i in q['run_cells']:
            if dict(cells[i]['metadata']) != rf.RUN_CELL_METADATA:
                problems.append(f'6: {t}: run cell {i} metadata is not cellView=form + jupyter.source_hidden only (run sync)')
            if q['run_part'][i] is False:
                problems.append(f'6: {t}: run cell {i}\'s title names another question (run sync)')
        if q['answer'] is not None:
            for i in range(q['answer'] + 1, q['end']):
                if cells[i]['cell_type'] == 'markdown' and rf.RUN_FENCE.match(source(cells[i])):
                    problems.append(f'4: {t}: a run block inside the Answer (cell {i})')
        labels = [p for _, p, _ in q['run_blocks']]
        if (len(labels) == 1 and labels != [None]) or (len(labels) > 1 and labels != list('abcdefghij'[:len(labels)])):
            problems.append(f'4: {t}: run block labels {labels} (one block: none; several: a, b, c, ...)')
        for i in list(range(q['start'], q['end'])):
            c = cells[i]
            if c['cell_type'] != 'markdown':
                continue
            for tok in md_tokens(source(c)):
                if tok.kind == 'fence' and not rf.is_python(tok) and tok.name == '`':
                    problems.append(f'7: {t}: cell {i} has a ```{tok.info} block outside a generated region (outputs '
                                    f'are written by sync: remove it, sync writes the output after the ```python block)')
                if tok.kind == 'text' and rf.IMG_TAG.search('\n'.join(tok.lines)):
                    problems.append(f'7: {t}: cell {i} has a turtle picture outside a generated region')
                if tok.kind == 'text' and re.search(r'\bTODO\b', '\n'.join(tok.lines)):
                    problems.append(f'16: {t}: cell {i} still says TODO')
        # 8: error names
        prose = rf.answer_prose(nb, q)
        named = {}
        for key, md in prose.items():
            named[key] = {m.group('val').strip('`') for s, e, m, kind, expr in rf.inline_markers(md) if kind == 'error'}
        raised_by = {}
        for _, part, _ in q['run_blocks']:
            ri = rf.run_cell_for(q, part)
            if ri is not None:
                raised_by[part if rf.multi(q) else None] = set(rf.raised(cells[ri].get('outputs', [])))
        for key, errs in raised_by.items():
            for e in errs:
                if e not in named.get(key, set()) and e not in named.get('summary', set()):
                    where = f'part {key}' if key else 'its code'
                    problems.append(f'8: {t}: {where} raises {e}, but the Answer does not name it with <!--=error-->')
        for key, md in prose.items():
            if key == 'summary':
                continue
            text = re.sub(r'<!--.*?-->`[^`]*`', '', rf.strip_fences(md))
            for e in set(rf.ERROR_NAME.findall(text)) - raised_by.get(key, set()):
                if raised_by:
                    problems.append(f'8: {t}: the Answer for {"part " + key if key else "the code"} names {e}, '
                                    f'which that code does not raise')
    c4_imports(nb, qs, problems)
    # 9: outputs and stamp
    for q in qs:
        for _, part, code in q['run_blocks']:
            ri = rf.run_cell_for(q, part)
            if ri is None:
                problems.append(f'9: {q["title"][:40]}: no run cell for {"part " + part if part else "the run block"} (run sync)')
            elif rf.parse_run_cell(source(cells[ri]))['code'] != code:
                problems.append(f'9: {q["title"][:40]}: the run cell does not run its run block\'s code: the block was '
                                f'edited (run sync)')
    run_idx = {i for q in qs for i in q['run_cells']}
    for i, c in enumerate(cells):
        if c['cell_type'] == 'code':
            if c.get('execution_count') is not None:
                problems.append(f'9: cell {i}: an execution count is stored (run sync)')
            if c.get('outputs') and i not in run_idx:
                problems.append(f'9: cell {i} ({c.get("id")}) has stored output but is not a run cell (run sync)')
            if i in run_idx:
                problems.extend(f'9: cell {i}: {p}' for p in rf.output_problems(c.get('outputs', [])))
                for o in c.get('outputs', []):
                    if o.get('metadata', {}).get('review_drawing'):
                        problems.extend(f'9: cell {i}: {p}' for p in rf.drawing_problems(o))
                if not c.get('outputs'):
                    problems.append(f'9: run cell {i} has no stored output (run sync)')
    problems.extend('9: ' + p for p in rf.stamp_problems(nb))
    # 13: NameError answers stay true
    bound = {}
    for i, c in enumerate(cells):
        codes = [source(c)] if c['cell_type'] == 'code' and i not in run_idx else []
        if c['cell_type'] == 'markdown':
            m = rf.RUN_FENCE.match(source(c))
            codes = [m.group('code')] if m else []
        for code in codes:
            for n in rf.module_bindings(code):
                bound.setdefault(n, []).append(i)
    for q in qs:
        for i in q['run_cells']:
            err = rf.ANSI.sub('', rf.stream_text(cells[i].get('outputs', []), 'stderr'))
            for name in re.findall(r"^NameError: name '(\w+)' is not defined", err, re.M):
                others = [j for j in bound.get(name, []) if not (q['start'] <= j < q['end'])]
                if others:
                    problems.append(f'13: {q["title"][:40]}: the answer is "NameError: {name}", but cell(s) {others} '
                                    f'bind {name}: after Run all the code would not raise')
    return qs


def name_reuse_notes(nb, qs):
    who = {}
    for q in qs:
        codes = sr.question_code(q) + [source(nb['cells'][i]) for i in q['defs']]
        for n in {n for code in codes for n in rf.assigned_names(code)}:
            who.setdefault(n, []).append(q['number'])
    return [f'{n} is assigned by Questions {", ".join(v)}' for n, v in sorted(who.items()) if len(v) > 1]


# ---------------------------------------------------------------- C4

def c4_imports(nb, qs, problems):
    """C4, static part: every Answer code block imports the setup cell's names it uses. (Removing the setup
    imports from the namespace at run time would also break the page's helper functions, which use them.)"""
    imports = rf.setup_imports(nb)
    for q in qs:
        for ci, ck, code, is_sol in sr.solution_blocks(nb, q):
            full = md_tokens(source(nb['cells'][ci]))[ck].code
            have = rf.module_bindings(full)
            missing = [n for n in rf.used_names(code) if n in imports and n not in have]
            if missing:
                problems.append(f'12: {q["title"][:40]}: Answer block {ck} uses {", ".join(missing)} but does not '
                                f'import it (run sync, which writes the import lines)')


def c4_jobs(nb, qs):
    """C4, run-time part: jobs that run every Answer code block as a student would after Run all."""
    jobs, expect = [], {}
    for q in qs:
        calls = '\n'.join(rf.calls_only(c) for c in sr.question_code(q)).strip()
        examples = sr.prompt_examples(nb, q)
        for ci, ck, code, is_sol in sr.solution_blocks(nb, q):
            full = md_tokens(source(nb['cells'][ci]))[ck].code        # as shown, with its import lines
            if sr.is_writecode(q) and is_sol:
                for ei, ek, ex in examples:
                    if rf.defined_functions(code) and not set(rf.defined_functions(code)) & set(rf.used_names(ex)):
                        continue
                    shown = [full, ex] if sr.function_style(code, ex) else [ex, full]
                    toks = md_tokens(source(nb['cells'][ei]))
                    want = toks[ek + 1].code if ek + 1 < len(toks) and toks[ek + 1].kind == 'region' else None
                    jid = f'c4_{len(jobs)}'
                    jobs.append({'id': jid, 'prelude': [], 'shown': shown})
                    expect[jid] = (q, ck, want, 'example')
            else:
                shown = [full] + ([calls] if calls and rf.only_definitions(code) else [])
                toks = md_tokens(source(nb['cells'][ci]))
                want = toks[ck + 1].code if ck + 1 < len(toks) and toks[ck + 1].kind == 'region' else None
                jid = f'c4_{len(jobs)}'
                jobs.append({'id': jid, 'prelude': [], 'shown': shown})
                expect[jid] = (q, ck, want, 'output')
    return jobs, expect


def c4_problems(results, expect):
    out = []
    for jid, (q, ck, want, kind) in expect.items():
        t = q['title'][:40]
        res = results.get(jid)
        if res is None or 'fatal' in res:
            out.append(f'12: {t}: Answer block {ck} could not run ({(res or {}).get("fatal", "no result")})')
            continue
        errs = [ev for ev in res['events'] if ev[0] == 'error']
        got = rf.snippet_markdown(res, rf.IMG_TAG.findall(want or ''))
        if errs and (want is None or errs[-1][1] not in want):
            last = rf.ANSI.sub('', errs[-1][2]).strip().split('\n')[-1]
            out.append(f'12: {t}: Answer block {ck}, copied into a new cell after Run all, raises {last}'
                       f'{" (it needs its own import or input line)" if errs[-1][1] in ("NameError", "ImportError") else ""}')
            continue
        text = ''.join(ev[1] for ev in res['events'] if ev[0] in ('stdout', 'stderr'))
        if 'Failed example:' in text and 'Failed example:' not in (want or ''):
            out.append(f'12: {t}: Answer block {ck}: a doctest fails')
            continue
        if want is not None and got != want:
            out.append(f'12: {t}: Answer block {ck}, copied into a new cell after Run all, shows\n'
                       f'{sr.indent(got)}\n      but the page says ({kind})\n{sr.indent(want)}')
    return out


# ---------------------------------------------------------------- runtime

def runtime_checks(nb, path, qs, kernel, cache, problems):
    jobs, expect = c4_jobs(nb, qs)
    r = sr.sync(nbf.from_dict(json.loads(json.dumps(nb))), path, kernel, accept=True, cache=cache, extra_jobs=jobs)
    if r.refused:
        problems.extend('11: sync refuses: ' + p for p in r.refused)
        return
    if not rf.stack_pinned(r.stack):
        problems.append(f'R0: kernel "{kernel}" runs {r.stack}, not the pinned stack {rf.PINNED_STACK}')
    want = json.loads(json.dumps(r.nb))
    have = json.loads(json.dumps(nb))
    if want != have:
        changes = [x for x in r.report if not x.startswith('ACCEPTED: ')] + \
                  [x[len('ACCEPTED: '):] for x in r.report if x.startswith('ACCEPTED: ')]
        problems.append('11: sync would change the page (run review.sh sync and read its report):\n    '
                        + '\n    '.join(x[:400] for x in changes[:30] or ['(metadata or cell layout)']))
    for i, s in sorted(r.status.items()):
        if s != 'ok':
            problems.append(f'R1: Run all would stop at cell {i} ({r.run.cells[i].id}): reply status "{s}"')
    hidden = rf.collapsed_sections_hidden(r.nb)
    for i, c in enumerate(r.run.cells):
        if c.cell_type == 'code' and c.outputs and i not in hidden:
            setup_stdout = 'setup' in rf.tags(r.nb.cells[i]) and all(
                o['output_type'] == 'stream' and o['name'] == 'stdout' for o in c.outputs)
            if not setup_stdout:
                problems.append(f'R2: cell {i} ({c.id}) shows output outside a closed Answer after Run all')
    for q in rf.parse_page(r.nb):
        for i in q['defs']:
            if r.run.cells[i].outputs:
                problems.append(f'R4: {q["title"][:40]}: definition cell {i} displays or raises something')
    problems.extend(c4_problems(r.results, expect))


def check(path, kernel='colablike', static_only=False, renumbered=False, cache=sr.DEFAULT_CACHE):
    nb = nbf.read(path, as_version=4)
    problems = []
    qs = static_checks(nb, path, problems, renumbered)
    for note in name_reuse_notes(nb, qs):
        print('  note:', note)
    if not static_only:
        runtime_checks(nb, path, qs, kernel, cache, problems)
    return problems


def main(argv):
    if not argv or argv[0].startswith('-'):
        sys.exit(__doc__)
    path = Path(argv[0])
    nb = json.loads(path.read_text(encoding='utf-8'))
    fmt = rf.page_format(nb)
    if fmt == 'legacy':
        import legacy_check_review
        jt = next((a for a in argv[1:] if not a.startswith('-') and a.endswith('.py')), None)
        if jt is None:
            sys.exit('old-format page: pass the path of jupyturtle.py (review.sh does)')
        legacy_check_review.problems.clear()
        return legacy_check_review.main(path, Path(jt))
    if fmt == 'mixed':
        print(f'1 problem(s):\n  - {path} mixes <details> Answers and #### Answer headings')
        return 1
    opt = lambda name, default: argv[argv.index(name) + 1] if name in argv else default  # noqa: E731
    problems = check(path, opt('--kernel', 'colablike'), '--static' in argv, '--renumbered' in argv,
                     Path(opt('--cache', sr.DEFAULT_CACHE)))
    if problems:
        print(f'{len(problems)} problem(s):')
        for p in problems:
            print('  -', p)
        return 1
    print(f'OK: {path}{" (static checks only)" if "--static" in argv else ""}')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
