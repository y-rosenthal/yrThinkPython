"""`review.sh sync`: write everything on a review page that can be derived, by running the code.

    python sync_review.py NB [--kernel colablike] [--out OUT] [--accept] [--force] [--static] [--cache DIR]

The author types each fact once (question code, helpers, solutions, example calls, fixes, prose values as
expressions); sync writes the rest (yr/README.md, "What sync writes"):

1. Static (no kernel): template cells (title, help note, helper cell, credits); one run cell per run block, in
   place, titled "Output of Question N[x]"; Answer headings saved collapsed; Colab's metadata dropped; outputs of
   other cells cleared; derived fixes (<!-- derive: ... -->); the "Start from this header" block; the import
   lines of Answer code blocks; "Then try:", "uses X from Question N" and "Run this cell to define X" lines.
2. Reference run on the pinned Colab-like kernel (fresh kernel, TMPDIR=/tmp, errors allowed, tags ignored),
   every run cell holding only the question's code: a run cell is wrapped in run_code exactly when its code
   raises or prints a line number.
3. Stored run (the page as it will be saved), which must show what the reference run showed. At the end of it,
   each snippet runs in a forked copy of the kernel (the state after Run all): example outputs, fix and "what if"
   outputs, values in prose; Concepts values run after the setup cells only.
4. Refusals (exit 2, nothing written): wrong kernel stack (unless --force), an output over the limits or with a
   memory address, a bad run block, solutions that disagree on an example, a value marker that fails.
5. Snapshot acceptance: a stored output, generated region or value that changes is shown and NOT written (exit 1)
   unless --accept. New ones are written and printed. A second sync changes nothing.
"""
import copy
import difflib
import json
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path

import nbformat as nbf

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import review_format as rf  # noqa: E402
from review_format import Tok, md_join, md_tokens, region_tok, source  # noqa: E402

COLAB_KEYS = ('executionInfo', 'outputId', 'colab')
DEFAULT_CACHE = Path(os.environ.get('YR_REVIEW_CACHE', Path.home() / '.venvs' / 'yrThinkPython' / 'yr-cache'))

# Run inside the kernel. Each job runs in a forked copy of the kernel process, so jobs can't affect each other or
# the page; outputs are captured the way a notebook cell shows them (printed text, the value of the last line,
# displays, drawings, the traceback as text).
KERNEL_LIB = r'''
def _yr_jobs(jobs_file, out_file):
    import json, os
    from IPython import get_ipython
    ip = get_ipython()
    with open(jobs_file) as f:
        jobs = json.load(f)
    results = {}
    for job in jobs:
        rfd, wfd = os.pipe()
        pid = os.fork()
        if pid == 0:
            os.close(rfd)
            try:
                res = _yr_child(ip, job)
            except BaseException as e:
                res = {'fatal': type(e).__name__ + ': ' + str(e)}
            with os.fdopen(wfd, 'wb') as f:
                f.write(json.dumps(res).encode())
            os._exit(0)
        os.close(wfd)
        with os.fdopen(rfd, 'rb') as f:
            data = f.read()
        os.waitpid(pid, 0)
        results[job['id']] = json.loads(data) if data else {'fatal': 'the snippet killed its process'}
    with open(out_file, 'w') as f:
        json.dump(results, f)


def _yr_child(ip, job):
    import io, signal, sys
    events = []

    class Out(io.TextIOBase):
        def __init__(self, name):
            self.name = name
        def writable(self):
            return True
        def write(self, s):
            if events and events[-1][0] == self.name:
                events[-1][1] += s
            else:
                events.append([self.name, s])
            return len(s)

    def publish(data, metadata=None, source=None, *, transient=None, update=False, **kw):
        html = data.get('text/html', '')
        did = (transient or {}).get('display_id')
        if isinstance(html, str) and html.lstrip().startswith('<svg'):
            for ev in events:
                if update and did and ev[0] == 'drawing' and ev[2] == did:
                    ev[1] = html
                    return
            events.append(['drawing', html, did])
        else:
            events.append(['display', {k: v for k, v in data.items() if isinstance(v, str)}])

    def hook(value):
        if value is not None:
            data, md = ip.display_formatter.format(value)
            events.append(['result', {k: v for k, v in data.items() if isinstance(v, str)}])

    def show_tb(etype, evalue, stb):
        events.append(['error', etype.__name__, ip.InteractiveTB.stb2text(getattr(stb, 'stb', stb))])

    def timeout(*args):
        raise TimeoutError('the snippet ran for more than 60 seconds')

    sys.stdout, sys.stderr = Out('stdout'), Out('stderr')
    ip.display_pub.publish = publish
    ip.display_pub.clear_output = lambda *a, **k: None
    ip.display_trap.hook = hook                  # the jobs cell is itself running: its trap is already set,
    sys.displayhook = hook                        # so nested cells use sys.displayhook as it is now
    ip._showtraceback = show_tb
    turtle = sys.modules.get('jupyturtle')
    if turtle is not None:
        turtle.TURTLE_DELAY = 0
    for name in job.get('remove', []):
        ip.user_ns.pop(name, None)
    signal.signal(signal.SIGALRM, timeout)
    signal.alarm(60)
    for code in job.get('prelude', []):
        ip.run_cell(code, store_history=False)
    prelude_errors = [ev[1] for ev in events if ev[0] == 'error']
    del events[:]
    for code in job['shown']:
        ip.run_cell(code, store_history=False)
    signal.alarm(0)
    return {'events': events, 'prelude_errors': prelude_errors}
'''
TURTLE_FAST = ("import sys as _yr_sys\nif 'jupyturtle' in _yr_sys.modules:\n"
               "    _yr_sys.modules['jupyturtle'].TURTLE_DELAY = 0")


class Refused(Exception):
    pass


def new_md(text, cid, meta=None):
    c = nbf.v4.new_markdown_cell(text)
    c.id = cid
    if meta:
        c.metadata.update(meta)
    return c


def new_code(text, cid, meta=None):
    c = nbf.v4.new_code_cell(text)
    c.id = cid
    if meta:
        c.metadata.update(copy.deepcopy(meta))
    return c


def set_source(cell, text, changes, why):
    if source(cell) != text:
        cell.source = text
        changes.append(why)


# ---------------------------------------------------------------- 1. static normalize

def template_cells(nb, path, changes):
    cells = nb.cells
    m = rf.TITLE_CELL_PARSE.match(source(cells[0])) if cells else None
    if m:
        set_source(cells[0], rf.title_cell(int(m.group('N')), m.group('TITLE')), changes, 'title cell rewritten')
    helps = [c for c in cells if rf.is_help_note(c)]
    if not helps:
        at = next((i for i, c in enumerate(cells) if c.cell_type == 'markdown'
                   and source(c).lstrip().startswith('## Questions')), None)
        if at is not None:
            cells.insert(at + 1, new_md(rf.HELP_NOTE, rf.stable_id(path.name, 'help'), {'tags': ['remove-cell']}))
            changes.append('help note added')
    for c in [c for c in cells if rf.is_help_note(c)]:
        set_source(c, rf.HELP_NOTE, changes, 'help note rewritten')
        if rf.tags(c) != ['remove-cell']:
            c.metadata['tags'] = ['remove-cell']
            changes.append('help note tagged remove-cell')
    first_q = next((i for i, c in enumerate(cells) if c.cell_type == 'markdown'
                    and rf.QUESTION_LINE.match(source(c))), len(cells))
    helper_meta = {'cellView': 'form', 'jupyter': {'source_hidden': True}, 'tags': ['setup']}
    helpers = [c for c in cells if rf.is_helper_cell(c)]
    if not helpers:
        setups = [i for i, c in enumerate(cells[:first_q]) if c.cell_type == 'code' and 'setup' in rf.tags(c)]
        anchor = setups[-1] if setups else next(i for i, c in enumerate(cells) if rf.is_help_note(c))
        cells.insert(anchor + 1, new_code(rf.HELPER_CELL, rf.stable_id(path.name, 'helper'), helper_meta))
        changes.append('helper cell (run_code) added')
    for c in [c for c in cells if rf.is_helper_cell(c)]:
        set_source(c, rf.HELPER_CELL, changes, 'helper cell rewritten')
        if dict(c.metadata) != helper_meta:
            c.metadata = nbf.from_dict(copy.deepcopy(helper_meta))
            changes.append('helper cell metadata set')
    last = cells[-1]
    if last.cell_type == 'markdown' and (source(last).startswith(rf.CREDITS_HEADING)
                                         or source(last).lstrip().startswith('*Summary and questions by')):
        set_source(last, rf.CREDITS, changes, 'credits rewritten')
    else:
        cells.append(new_md(rf.CREDITS, rf.stable_id(path.name, 'credits')))
        changes.append('credits added')


def reconcile(nb, q, changes, errors):
    """Make the run cells of question q match its run blocks: one per block, in place, canonical."""
    cells = nb.cells
    blocks, t = q['run_blocks'], q['title'][:40]
    if q['answer'] is None:
        if blocks:
            errors.append(f"{t}: run blocks but no '{rf.ANSWER_HEADING}' heading")
        return
    for _, part, code in blocks:
        errors.extend(f'{t}: run block {part or ""}: {p}' for p in rf.run_block_problems(code))
    labels = [p for _, p, _ in blocks]
    if (len(blocks) == 1 and labels != [None]) or (len(blocks) > 1 and labels != list('abcdefghij'[:len(blocks)])):
        errors.append(f'{t}: run block labels {labels} (one block: no label; several: **Part a**, **Part b**, ...)')
    if errors:
        return
    aid = cells[q['answer']].id
    region = cells[q['answer'] + 1:q['end']]
    run_ids = {id(cells[i]) for i in q['run_cells']}
    keep, used = {}, set()
    for k, (_, part, code) in enumerate(blocks):
        ri = rf.run_cell_for(q, part)
        if ri is not None and id(cells[ri]) not in used:
            keep[k] = cells[ri]
            used.add(id(cells[ri]))
    for c in region:
        if id(c) in run_ids and id(c) not in used:
            changes.append(f'{t}: orphan run cell {c.id} deleted (its run block is gone)')
    region = [c for c in region if id(c) not in run_ids or id(c) in used]
    for k, (_, part, code) in enumerate(blocks):
        p = part if rf.multi(q) else None
        c = keep.get(k)
        if c is None:
            c = new_code(rf.render_run_cell(code, False, q['number'], p), rf.stable_id(aid, 'run', p or '-'),
                         rf.RUN_CELL_METADATA)
            keep[k] = c
            changes.append(f'{t}: run cell {c.id} created for {"part " + p if p else "the run block"}')
            if not rf.multi(q):
                region.insert(0, c)
            continue
        info = rf.parse_run_cell(source(c))
        want = rf.render_run_cell(code, info['wrapped'], q['number'], p)
        if info['code'] != code:
            c.source, c.outputs, c.execution_count = want, [], None
            changes.append(f'{t}: run cell {c.id} regenerated from its edited run block; outputs cleared')
        elif source(c) != want:
            c.source = want
            changes.append(f'{t}: run cell {c.id}: title / layout made canonical')
        if dict(c.metadata) != rf.RUN_CELL_METADATA:
            c.metadata = nbf.from_dict(copy.deepcopy(rf.RUN_CELL_METADATA))
            changes.append(f'{t}: run cell {c.id}: metadata set to cellView=form + jupyter.source_hidden')
    if rf.multi(q):                                    # run cell x goes right after its '**Part x:**' cell
        region = [c for c in region if id(c) not in {id(x) for x in keep.values()}]
        for k, (_, part, _) in enumerate(blocks):
            pi = next((n for n, c in enumerate(region) if c.cell_type == 'markdown'
                       and (m := rf.PART_CELL.match(source(c))) and m.group('part') == part), None)
            if pi is None:
                if k == 0:
                    pos = next((n for n, c in enumerate(region) if c.cell_type == 'markdown'
                                and rf.PART_CELL.match(source(c))), len(region))
                else:
                    pos = next(n for n, c in enumerate(region) if c is keep[k - 1]) + 1
                region.insert(pos, new_md(f'**Part {part}:** TODO', rf.stable_id(aid, 'part', part)))
                changes.append(f'{t}: "**Part {part}:** TODO" cell created (write the explanation)')
                pi = pos
            region.insert(pi + 1, keep[k])
    if [id(c) for c in region] != [id(c) for c in cells[q['answer'] + 1:q['end']]]:
        if not any('created' in x or 'deleted' in x for x in changes):
            changes.append(f'{t}: run cells moved right after their Part cells')
        cells[q['answer'] + 1:q['end']] = region


def static_normalize(nb, path):
    """Template cells, run cells, metadata. Returns (changes, errors); changes nb in place."""
    changes, errors = [], []
    if rf.page_format(nb) == 'legacy':
        return [], ['this page is in the old format (<details> Answers): sync works only on converted pages; '
                    'use review.sh images / check for it']
    if rf.page_format(nb) == 'mixed':
        return [], ['this page mixes <details> Answers and #### Answer headings']
    for c in nb.cells:
        heading = c.cell_type == 'markdown' and source(c).strip() == rf.ANSWER_HEADING
        for k in COLAB_KEYS + (() if heading else ('id',)):
            if k in c.metadata:
                del c.metadata[k]
                changes.append(f'cell {c.id}: Colab metadata "{k}" dropped')
    template_cells(nb, path, changes)
    for q in reversed(rf.parse_page(nb)):              # bottom-up, so earlier indices stay valid
        reconcile(nb, q, changes, errors)
    run_ids = {nb.cells[i].id for q in rf.parse_page(nb) for i in q['run_cells']}
    for c in nb.cells:
        if c.cell_type == 'code' and c.id not in run_ids and (c.outputs or c.execution_count is not None):
            c.outputs, c.execution_count = [], None
            changes.append(f'code cell {c.id}: outputs cleared (only run cells store output)')
    ids = []
    for c in nb.cells:
        if c.cell_type == 'markdown' and source(c).strip() == rf.ANSWER_HEADING:
            want = {'id': c.id, 'jp-MarkdownHeadingCollapsed': True}
            if dict(c.metadata) != want:
                changes.append(f'Answer heading {c.id}: collapse metadata written')
                c.metadata = nbf.from_dict(want)
            ids.append(c.id)
    if nb.metadata.get('colab', {}).get('collapsed_sections') != ids:
        changes.append('colab.collapsed_sections rewritten')
        nb.metadata.setdefault('colab', {})['collapsed_sections'] = ids
    for k in ('colab',):
        extra = set(nb.metadata.get(k, {})) - {'collapsed_sections'}
        for e in extra:
            del nb.metadata[k][e]
            changes.append(f'notebook metadata colab.{e} dropped')
    seen = set()
    for c in nb.cells:
        if c.id in seen:
            errors.append(f'duplicate cell id {c.id}')
        seen.add(c.id)
    return changes, errors


# ---------------------------------------------------------------- 1b. static generation

def question_code(q):
    return [code for _, _, code in q['run_blocks']]


def solution_blocks(nb, q):
    """[(cell idx, token idx, code without generated imports, is_solution)] for the ```python blocks of an Answer."""
    out = []
    for i in q['answer_md']:
        toks = md_tokens(source(nb.cells[i]))
        for k, t in enumerate(toks):
            if rf.is_python(t):
                prev = toks[k - 1] if k else None
                not_sol = any(x.kind == 'marker' and x.name == 'not a solution' for x in toks[max(0, k - 2):k])
                n = int(prev.arg or 0) if prev is not None and prev.kind == 'marker' and prev.name == 'generated imports' else 0
                out.append((i, k, strip_imports(t.code, n), not not_sol))
    return out


def strip_imports(code, n):
    lines = code.split('\n')[n:]
    if n and lines and not lines[0].strip():
        lines = lines[1:]
    return '\n'.join(lines)


def prompt_examples(nb, q):
    """[(cell idx, token idx, code)] for the example blocks of a question's prompt: in a write-code question the
    ```python blocks after the **Examples** line; otherwise every ```python block (e.g. correct calls)."""
    out, after = [], q['placeholder'] is None
    for i in sorted(set(q['prompt_md']) | {q['heading']}):
        toks = md_tokens(source(nb.cells[i]))
        for k, t in enumerate(toks):
            if t.kind == 'text' and any(rf.is_examples_line(x) for x in t.lines):
                after = True
            if rf.is_python(t) and after:
                out.append((i, k, t.code))
    return out


def is_writecode(q):
    return q['placeholder'] is not None


def reference_solution(nb, q):
    sols = [s for s in solution_blocks(nb, q) if s[3]]
    return sols[0][2] if sols else None


def function_style(solution, example):
    """True if the example calls a function the solution defines (run the solution first); False for code
    that works on the example's variables (run the example's assignments first)."""
    return bool(set(rf.defined_functions(solution)) & set(rf.used_names(example)))


def provided_names(nb, qs):
    """{name: question number} for names bound by definition cells, in page order (first one wins)."""
    out = {}
    for q in qs:
        for i in q['defs']:
            for n in rf.module_bindings(source(nb.cells[i])):
                out.setdefault(n, q['number'])
    return out


def update_region(toks, at, kind, body, changes, why, insert=True):
    """Make toks[at] the region `kind` with `body`, inserting it at `at` if the token there is not that region."""
    if at < len(toks) and toks[at].kind == 'region' and toks[at].name == kind:
        if toks[at].code != body:
            toks[at] = region_tok(kind, body)
            changes.append(why)
        return
    if insert:
        toks.insert(at, region_tok(kind, body))
        changes.append(why)


def insert_before_examples(toks, new):
    """Insert tokens before the **Examples** line (splitting its text token), or at the end; returns the index."""
    for k, t in enumerate(toks):
        if t.kind == 'text':
            for j, line in enumerate(t.lines):
                if rf.is_examples_line(line):
                    before, after = t.lines[:j], t.lines[j:]
                    seq = ([Tok('text', before)] if before else []) + new + [Tok('text', [''] + after)]
                    if before and before[-1].strip():
                        seq.insert(1 if before else 0, Tok('text', ['']))
                    toks[k:k + 1] = seq
                    return k
    toks.extend([Tok('text', [''])] + new)
    return len(toks) - len(new)


def find_region(toks, kind):
    return next((k for k, t in enumerate(toks) if t.kind == 'region' and t.name == kind), None)


def and_list(items):
    items = list(items)
    return items[0] if len(items) == 1 else ', '.join(items[:-1]) + ' and ' + items[-1]


def static_generate(nb, imports, changes, errors):
    """Derived fixes, header blocks, import lines, "Then try:", "uses" and "Run this cell to define" lines."""
    qs = rf.parse_page(nb)
    by_number = {q['number']: q for q in qs}
    provided = provided_names(nb, qs)
    for q in qs:
        t = q['title'][:40]
        # derived fixes (E9): the next ```python block is another question's code with one change
        for i in q['answer_md'] + q['prompt_md']:
            toks = md_tokens(source(nb.cells[i]))
            dirty = False
            for k, tok in enumerate(toks):
                if tok.kind == 'marker' and tok.name == 'derive':
                    m = re.fullmatch(r'from=(?:Q(?P<q>\d+[a-z]?)(?P<part>:[a-z])?|(?P<sol>solution))\s+'
                                     r'replace="(?P<old>[^"]*)"\s+with="(?P<new>[^"]*)"', tok.arg)
                    nxt = toks[k + 1] if k + 1 < len(toks) else None
                    if not m or nxt is None or not rf.is_python(nxt):
                        errors.append(f'{t}: bad derive marker {tok.lines[0]!r} (it needs from=QN or from=solution, '
                                      f'replace="..." with="...", and a ```python block on the next line)')
                        continue
                    if m.group('sol'):
                        ref = reference_solution(nb, q)
                        blocks = [ref] if ref else []
                    else:
                        src_q = by_number.get(m.group('q'))
                        blocks = src_q and [c for _, p, c in src_q['run_blocks']
                                            if not m.group('part') or p == m.group('part')[1:]]
                        if src_q and len(blocks) == 1 and src_q['defs'] and not m.group('part'):
                            blocks = ['\n\n'.join([source(nb.cells[d]) for d in src_q['defs']] + blocks)]
                    if not blocks or len(blocks) != 1:
                        errors.append(f'{t}: derive marker: no single code block to derive from')
                        continue
                    old = m.group('old').replace('\\n', '\n')
                    if blocks[0].count(old) != 1:
                        errors.append(f'{t}: derive marker: "{old}" occurs {blocks[0].count(old)} times in the code '
                                      f'it derives from (it must occur exactly once)')
                        continue
                    want = blocks[0].replace(old, m.group('new').replace('\\n', '\n'))
                    if nxt.code != want:
                        toks[k + 1] = Tok('fence', ['```python'] + want.split('\n') + ['```'], info='python',
                                          code=want, name='`')
                        dirty = True
                        changes.append(f'{t}: derived fix written')
            if dirty:
                nb.cells[i].source = md_join(toks)
        if is_writecode(q):
            ref = reference_solution(nb, q)
            if ref is None:
                errors.append(f'{t}: a write-code question needs a ```python solution block in its Answer')
                continue
            # header block (E4)
            override = None
            for i in q['prompt_md'] + [q['heading']]:
                m = re.search(r'^<!-- header:\s*(.*?)\s*-->$', source(nb.cells[i]), re.M)
                if m:
                    override = m.group(1).split()
            names = override if override is not None else [n for n in rf.defined_functions(ref) if n not in provided]
            heads = rf.def_headers(ref, names)
            if override is not None and len(heads) != len(override):
                errors.append(f'{t}: <!-- header: {" ".join(override)} -->: the solution does not define all of them')
            body = ''
            if heads and not q['nosig']:
                body = ('Start from this header (replace `...` with the body):\n\n```python\n'
                        + '\n\n'.join(h + '\n    ...' for h in heads) + '\n```')
            prompt_cells = sorted(set(q['prompt_md']) | {q['heading']})
            found = False
            for i in prompt_cells:
                toks = md_tokens(source(nb.cells[i]))
                k = find_region(toks, 'header')
                if k is not None:
                    found = True
                    if body:
                        update_region(toks, k, 'header', body, changes, f'{t}: header block written')
                    else:
                        del toks[k]
                        changes.append(f'{t}: header block removed')
                    nb.cells[i].source = md_join(toks)
            if body and not found:
                i = next((i for i in prompt_cells if any(rf.is_examples_line(line) for line in
                                                         source(nb.cells[i]).split('\n'))), prompt_cells[-1])
                toks = md_tokens(source(nb.cells[i]))
                insert_before_examples(toks, [region_tok('header', body), Tok('text', [''])])
                nb.cells[i].source = md_join(toks).replace('\n\n\n', '\n\n')
                changes.append(f'{t}: header block written')
        # import lines of Answer code blocks (E5) and "Then try:" (E19)
        examples = prompt_examples(nb, q)
        first_solution = True
        for i in q['answer_md']:
            toks = md_tokens(source(nb.cells[i]))
            new, k = [], 0
            while k < len(toks):
                tok = toks[k]
                if tok.kind == 'marker' and tok.name == 'generated imports' and k + 1 < len(toks) and rf.is_python(toks[k + 1]):
                    k += 1
                    continue
                if rf.is_python(tok):
                    prev = toks[k - 1] if k else None
                    n = int(prev.arg or 0) if prev is not None and prev.kind == 'marker' and prev.name == 'generated imports' else 0
                    code = strip_imports(tok.code, n)
                    lines = rf.import_lines(code, imports)
                    if lines:
                        new.append(Tok('marker', [f'<!-- generated imports: {len(lines)} -->'], name='generated imports',
                                       arg=str(len(lines))))
                    full = '\n'.join(lines + [''] + [code]) if lines else code
                    new.append(Tok('fence', ['```python'] + full.split('\n') + ['```'], info='python', code=full, name='`')
                               if full != tok.code else tok)
                    if is_writecode(q) and first_solution and not q['nosig'] and examples \
                            and not any(x.kind == 'marker' and x.name == 'not a solution' for x in toks[max(0, k - 2):k]):
                        first_solution = False
                        calls = [c.strip() for c in examples[0][2].split('\n') if c.strip()]
                        body = 'Then try: ' + and_list(f'`{c}`' for c in calls) + '.'
                        if k + 1 < len(toks) and toks[k + 1].kind == 'region' and toks[k + 1].name == 'then-try':
                            new.append(region_tok('then-try', body))
                            k += 2
                            continue
                        new.append(region_tok('then-try', body))
                    k += 1
                    continue
                if tok.kind == 'region' and tok.name == 'then-try':
                    k += 1                                   # a stale one (sync writes it after the first solution)
                    continue
                new.append(tok)
                k += 1
            text = md_join(new)
            if text != source(nb.cells[i]):
                nb.cells[i].source = text
                changes.append(f'{t}: import lines / "Then try" line written')
        # "uses X from Question N" (E6)
        own = set()
        for i in q['defs']:
            own.update(rf.module_bindings(source(nb.cells[i])))
        used = []
        codes = question_code(q) + [c for _, _, c in examples] + [s[2] for s in solution_blocks(nb, q)]
        for code in codes:
            for n in rf.used_names(code):
                if n in provided and n not in own and provided[n] != q['number'] and n not in used \
                        and n not in imports:
                    used.append(n)
        body = ''
        if used:
            groups = {}
            for n in used:
                groups.setdefault(provided[n], []).append(f'`{n}`')
            body = 'This question uses ' + ', and '.join(f'{and_list(ns)} from Question {num}'
                                                         for num, ns in groups.items()) + '.'
        cell = nb.cells[q['heading']]
        toks = md_tokens(source(cell))
        k = find_region(toks, 'uses')
        if k is not None and not body:
            del toks[k]
            changes.append(f'{t}: "uses" line removed')
        elif k is not None:
            update_region(toks, k, 'uses', body, changes, f'{t}: "uses" line written')
        elif body:
            toks.extend([Tok('text', [''])] + [region_tok('uses', body)])
            changes.append(f'{t}: "uses" line written')
        cell.source = md_join(toks)
        # "Run this cell to define X" (E15)
        for i in q['defs']:
            src = source(nb.cells[i])
            fns = [n for n in rf.module_bindings(src) if n in rf.defined_functions(src)]
            assigned = rf.assigned_names(src)
            words = []
            if fns:
                words.append('define ' + and_list(f'`{n}`' for n in fns))
            if assigned:
                words.append('assign ' + and_list(f'`{n}`' for n in assigned))
            if not words:
                continue
            body = 'Run this cell to ' + ' and '.join(words) + '.'
            prev = nb.cells[i - 1]
            if prev.cell_type == 'markdown' and not rf.RUN_FENCE.match(source(prev)):
                toks = md_tokens(source(prev))
                k = find_region(toks, 'define')
                if k is None:
                    toks.extend([Tok('text', [''])] + [region_tok('define', body)])
                    changes.append(f'{t}: "Run this cell to define" line written')
                else:
                    update_region(toks, k, 'define', body, changes, f'{t}: "Run this cell to define" line written')
                prev.source = md_join(toks)
            else:
                nb.cells.insert(i, new_md(md_join([region_tok('define', body)]), rf.stable_id(nb.cells[i].id, 'define')))
                changes.append(f'{t}: "Run this cell to define" cell added')
                return static_generate(nb, imports, changes, errors)   # indices moved: start again
    return qs


# ---------------------------------------------------------------- 2. jobs

def collect_jobs(nb, qs):
    """The snippets sync runs after Run all, and where their results go. Returns (jobs, concept_jobs, sinks):
    sinks[job id] = (kind, cell index, ...) for filling in."""
    jobs, concept_jobs, sinks = [], [], {}

    def add(lst, sink, **job):
        job['id'] = f'j{len(sinks)}'
        sinks[job['id']] = sink
        lst.append(job)
        return job['id']

    q_of = {}
    for q in qs:
        for i in range(q['start'], q['end']):
            q_of[i] = q
    for q in qs:
        qcode = question_code(q)
        calls = '\n'.join(rf.calls_only(c) for c in qcode).strip()
        examples = prompt_examples(nb, q)
        ref = reference_solution(nb, q) if is_writecode(q) else None
        for i, k, code in examples:
            if is_writecode(q):
                if ref is None:
                    continue
                if function_style(ref, code):
                    add(jobs, ('example', i, k), prelude=[ref], shown=[code])
                else:
                    add(jobs, ('example', i, k), prelude=[], shown=[code, ref])
                for ci, ck, sol, is_sol in solution_blocks(nb, q):
                    if is_sol and sol != ref and set(rf.defined_functions(sol)) & set(rf.used_names(code)):
                        add(jobs, ('agree', i, k, ci, ck), prelude=[ref, sol], shown=[code])
                    elif is_sol and sol != ref and not rf.defined_functions(sol) and not function_style(ref, code):
                        add(jobs, ('agree', i, k, ci, ck), prelude=[], shown=[code, sol])
            else:
                add(jobs, ('example', i, k), prelude=qcode, shown=[code])
        for ci, ck, code, is_sol in solution_blocks(nb, q):
            if is_writecode(q) and is_sol:
                continue
            shown = [code] + ([calls] if calls and rf.only_definitions(code) else [])
            add(jobs, ('output', ci, ck), prelude=[] if is_writecode(q) else qcode, shown=shown)
    for i, c in enumerate(nb.cells):
        if c.cell_type != 'markdown':
            continue
        md = source(c)
        q = q_of.get(i)
        for n, (s, e, m, kind, expr) in enumerate(rf.inline_markers(md)):
            if kind != 'value' or not expr:
                continue
            dos = [mm.group(1).strip() for mm in re.finditer(r'^<!--\s*do:\s*(.*?)\s*-->$', md[:s], re.M)]
            if q is None:
                add(concept_jobs, ('value', i, n), prelude=dos, shown=[expr])
            else:
                add(jobs, ('value', i, n), prelude=question_code(q) + dos, shown=[expr])
    return jobs, concept_jobs, sinks


# ---------------------------------------------------------------- 3. running

def execute(nb, kernel, cache, jobs=None, concept_jobs=None):
    """Run a copy of nb like Run all but without stopping (errors allowed), tags ignored, TMPDIR=/tmp; then the
    jobs. Returns (executed copy, {cell index: reply status}, kernel stack, job results)."""
    from nbclient import NotebookClient
    run = copy.deepcopy(nb)
    for c in run.cells:
        c.metadata.pop('tags', None)
    n = len(run.cells)
    first_q = next((i for i, c in enumerate(run.cells) if c.cell_type == 'markdown'
                    and rf.QUESTION_LINE.match(source(c))), n)
    after_setup = max([i + 1 for i, c in enumerate(run.cells[:first_q]) if c.cell_type == 'code'] or [0])
    injected = [nbf.v4.new_code_cell(TURTLE_FAST), nbf.v4.new_code_cell(KERNEL_LIB)]
    if concept_jobs:
        injected.append(nbf.v4.new_code_cell("_yr_jobs('concept_jobs.json', 'concept_out.json')"))
    run.cells[after_setup:after_setup] = injected
    tail = []
    if jobs:
        tail.append(nbf.v4.new_code_cell("_yr_jobs('jobs.json', 'jobs_out.json')"))
    tail.append(nbf.v4.new_code_cell(rf.STACK_PROBE))
    run.cells.extend(tail)
    status = {}

    def hook(cell, cell_index, execute_reply):
        status[cell_index] = execute_reply['content']['status']

    results = {}
    with tempfile.TemporaryDirectory() as tmp:
        if cache.is_dir():
            for f in cache.iterdir():
                if f.is_file():
                    shutil.copy(f, tmp)
        before = set(os.listdir(tmp))
        Path(tmp, 'jobs.json').write_text(json.dumps(jobs or []))
        Path(tmp, 'concept_jobs.json').write_text(json.dumps(concept_jobs or []))
        NotebookClient(run, kernel_name=kernel, timeout=900, allow_errors=True, record_timing=False,
                       on_cell_executed=hook, resources={'metadata': {'path': tmp}}).execute(
            env={**os.environ, 'TMPDIR': '/tmp'})
        for name in ('jobs_out.json', 'concept_out.json'):
            p = Path(tmp, name)
            if p.exists():
                results.update(json.loads(p.read_text()))
        cache.mkdir(parents=True, exist_ok=True)
        for f in set(os.listdir(tmp)) - before - {'jobs.json', 'concept_jobs.json', 'jobs_out.json', 'concept_out.json'}:
            if Path(tmp, f).is_file() and not f.startswith('.'):
                shutil.copy(Path(tmp, f), cache)       # downloads (words.txt, ...) are kept for the next run
    probe = run.cells[-1]
    stack = json.loads(''.join(o.get('text', '') for o in probe.outputs if o.output_type == 'stream') or 'null')
    for c in injected + tail:
        k = run.cells.index(c)
        if status.get(k, 'ok') != 'ok':
            raise RuntimeError(f'sync\'s own helper cell failed: {c.outputs}')
    keep = [c for c in run.cells if all(c is not x for x in injected + tail)]
    remap = {}
    j = 0
    for k, c in enumerate(run.cells):
        if any(c is x for x in injected + tail):
            continue
        remap[k] = j
        j += 1
    run.cells = keep
    return run, {remap[k]: s for k, s in status.items() if k in remap}, stack, results


def run_cell_list(nb):
    """[(question, part, code, run cell index)] in page order."""
    out = []
    for q in rf.parse_page(nb):
        for _, part, code in q['run_blocks']:
            out.append((q, part if rf.multi(q) else None, code, rf.run_cell_for(q, part)))
    return out


# ---------------------------------------------------------------- 4. filling in

def result_md(res, old_body):
    if 'fatal' in res:
        raise Refused(f'the snippet could not run: {res["fatal"]}')
    return rf.snippet_markdown(res, rf.IMG_TAG.findall(old_body or ''))


def value_text(res):
    if 'fatal' in res:
        raise Refused(res['fatal'])
    errs = [ev for ev in res['events'] if ev[0] == 'error']
    if errs:
        raise Refused(rf.ANSI.sub('', errs[-1][2]).strip().split('\n')[-1])
    vals = [ev[1].get('text/plain', '') for ev in res['events'] if ev[0] == 'result']
    if not vals:
        raise Refused('the expression has no value (it displays nothing)')
    if '\n' in vals[-1]:
        raise Refused(f'the value {vals[-1][:40]!r} has more than one line')
    return vals[-1]


def fill(nb, qs, sinks, results, errors, report, not_accepted):
    """Write examples, outputs and values into the markdown; record changes for snapshot acceptance."""
    by_cell = {}
    for jid, sink in sinks.items():
        by_cell.setdefault(sink[1], []).append((jid, sink))
    q_of = {i: q for q in qs for i in range(q['start'], q['end'])}
    for i, items in sorted(by_cell.items()):
        cell = nb.cells[i]
        t = (q_of[i]['title'][:40] if i in q_of else f'cell {i}')
        md = source(cell)
        toks = md_tokens(md)
        values = {}
        inserts = []                                        # (token index, kind, body)
        agree = {}
        for jid, sink in items:
            res = results.get(jid)
            if res is None:
                errors.append(f'{t}: no result for a snippet (sync bug)')
                continue
            try:
                if sink[0] == 'value':
                    values[sink[2]] = value_text(res)
                elif sink[0] in ('example', 'output'):
                    k = sink[2]
                    old = toks[k + 1].code if k + 1 < len(toks) and toks[k + 1].kind == 'region' else ''
                    inserts.append((k, 'example' if sink[0] == 'example' else 'output', result_md(res, old)))
                elif sink[0] == 'agree':
                    agree[jid] = (sink, res)
            except Refused as e:
                errors.append(f'{t}: {sink[0]} {"value" if sink[0] == "value" else "block"}: {e}')
        for k, kind, body in sorted(inserts, reverse=True):
            nxt = toks[k + 1] if k + 1 < len(toks) else None
            if nxt is not None and nxt.kind == 'region' and nxt.name == kind:
                if nxt.code != body:
                    if nxt.code.strip() in ('', '?'):
                        report.append(f'{t}: new {kind} output:\n{indent(body)}')
                    else:
                        not_accepted.append(f'{t}: the generated {kind} output changes:\n{diff(nxt.code, body)}')
                    toks[k + 1] = region_tok(kind, body)
            else:
                toks.insert(k + 1, region_tok(kind, body))
                report.append(f'{t}: new {kind} output:\n{indent(body)}')
        text = md_join(toks)
        if values:
            marks = rf.inline_markers(text)
            for n, (s, e, m, kind, expr) in reversed(list(enumerate(marks))):
                if n in values:
                    old = m.group('val')
                    new = values[n]
                    if old != new:
                        if old.strip() == '?':
                            report.append(f'{t}: value of `{expr}` is `{new}`')
                        else:
                            not_accepted.append(f'{t}: the value of `{expr}` changes from `{old}` to `{new}`')
                        text = text[:s] + m.group(0)[:m.start('ticks') - m.start()] + rf.format_span(new) + text[e:]
        cell.source = text
        for jid, (sink, res) in agree.items():
            _, ei, ek, ci, ck = sink
            ex_toks = md_tokens(source(nb.cells[ei]))
            want = ex_toks[ek + 1].code if ek + 1 < len(ex_toks) and ex_toks[ek + 1].kind == 'region' else None
            got = rf.snippet_markdown(res, rf.IMG_TAG.findall(want or ''))
            if want is not None and got != want:
                errors.append(f'{t}: the solutions disagree: Answer block {ck} gives\n{indent(got)}\n    for an example '
                              f'whose reference output is\n{indent(want)}')
    # error names in prose (<!--=error-->): the error the part's run cell shows
    for q in qs:
        errs = {}
        for _, part, code, ri in [x for x in run_cell_list(nb) if x[0]['number'] == q['number']]:
            if ri is not None:
                errs[part] = rf.raised(nb.cells[ri].outputs)
        for i in q['answer_md']:
            md = source(nb.cells[i])
            marks = [x for x in rf.inline_markers(md) if x[3] == 'error']
            if not marks:
                continue
            part = part_of_cell(nb, q, i)
            names = errs.get(part) if part != 'summary' else sorted({n for v in errs.values() for n in v})
            if not names:
                errors.append(f'{q["title"][:40]}: <!--=error--> in {"the summary" if part == "summary" else "part " + str(part)}, '
                              f'but that code raises nothing')
                continue
            if len(set(names)) != 1:
                errors.append(f'{q["title"][:40]}: <!--=error--> in the summary, but the parts raise {names}')
                continue
            for s, e, m, kind, expr in reversed(marks):
                old = m.group('val')
                if old != names[-1]:
                    if old.strip() == '?':
                        report.append(f'{q["title"][:40]}: error name {names[-1]}')
                    else:
                        not_accepted.append(f'{q["title"][:40]}: the error name changes from {old} to {names[-1]}')
                    md = md[:s] + m.group(0)[:m.start('ticks') - m.start()] + rf.format_span(names[-1]) + md[e:]
            nb.cells[i].source = md


def part_of_cell(nb, q, i):
    """The part an Answer markdown cell explains (None for a one-block question), or 'summary'."""
    if not rf.multi(q):
        return None
    last_run = max(q['run_cells']) if q['run_cells'] else q['end']
    if i > last_run:
        return 'summary'
    cur = None
    for j in q['answer_md']:
        m = rf.PART_CELL.match(source(nb.cells[j]))
        cur = m.group('part') if m else cur
        if j == i:
            return cur
    return cur


def indent(s, pre='      '):
    return '\n'.join(pre + line for line in s.split('\n')[:40])


def diff(a, b):
    d = difflib.unified_diff(a.split('\n'), b.split('\n'), 'stored', 'new', lineterm='', n=1)
    return '\n'.join(('        ' + x)[:170] for x in list(d)[:40])


def byte_diff(old, new):
    a = json.dumps(json.loads(rf.canon_outputs(old)), indent=1, ensure_ascii=False).splitlines()
    b = json.dumps(json.loads(rf.canon_outputs(new)), indent=1, ensure_ascii=False).splitlines()
    d = list(difflib.unified_diff(a, b, 'stored', 'new', lineterm='', n=1))
    return '\n'.join(('        ' + x)[:170] for x in d[:40]) + ('\n        ...' if len(d) > 40 else '')


# ---------------------------------------------------------------- sync

class Result:
    def __init__(self):
        self.report, self.refused, self.not_accepted, self.bad = [], [], [], []
        self.nb = self.run = self.status = self.stack = None
        self.results = {}


def sync(nb, path, kernel='colablike', accept=False, force=False, cache=DEFAULT_CACHE, extra_jobs=()):
    """Sync a copy of nb. Returns a Result; result.nb is the synced notebook (None if refused or not accepted).
    extra_jobs (check C4) run with the generation jobs; their results are in result.results."""
    r = Result()
    work = copy.deepcopy(nb)
    old = {c.id: copy.deepcopy(c.get('outputs', [])) for c in work.cells if c.cell_type == 'code'}
    r.report, errors = static_normalize(work, Path(path))
    if not errors:
        imports = rf.setup_imports(work)
        static_generate(work, imports, r.report, errors)
    if errors:
        r.refused = errors
        return r
    # reference run: every run cell holds only the question's code -> which ones must be wrapped
    plain = copy.deepcopy(work)
    for q, part, code, ri in run_cell_list(plain):
        plain.cells[ri].source = code
    run1, _, stack, _ = execute(plain, kernel, cache)
    if not rf.stack_pinned(stack) and not force:
        r.refused = [f'the kernel "{kernel}" runs {stack}, not the pinned Colab-like stack {rf.PINNED_STACK}: '
                     f'stored outputs must come from it (yr/tools/ensure_colab_venv.sh); --force writes them anyway, '
                     f'and check will fail']
        return r
    wrap = {}
    for q, part, code, ri in run_cell_list(work):
        wrap[ri] = rf.needs_wrap(run1.cells[ri].outputs)
        new = rf.render_run_cell(code, wrap[ri], q['number'], part)
        if new != source(work.cells[ri]):
            r.report.append(f"{q['title'][:40]}: run cell {work.cells[ri].id} {'wrapped in run_code' if wrap[ri] else 'unwrapped'}")
            work.cells[ri].source = new
    qs = rf.parse_page(work)
    jobs, concept_jobs, sinks = collect_jobs(work, qs)
    extra = [dict(j) for j in extra_jobs]
    run, status, stack, results = execute(work, kernel, cache, jobs + extra, concept_jobs)
    r.run, r.status, r.stack, r.results = run, status, stack, results
    for q, part, code, ri in run_cell_list(work):
        a, b = rf.seen(run1.cells[ri].outputs), rf.seen(run.cells[ri].outputs)
        if a != b:
            errors.append(f"{q['title'][:40]}: run cell {work.cells[ri].id} {'wrapped' if wrap[ri] else 'with its title'} "
                          f"shows something else than the question's code alone (alone {a!r:.200}, stored form {b!r:.200})"
                          f"{'; a value shown by the last line is not displayed when wrapped: print it' if wrap[ri] else ''}")
    run_idx = set()
    for q, part, code, ri in run_cell_list(work):
        run_idx.add(ri)
        c = work.cells[ri]
        new = rf.normalize_outputs(run.cells[ri].outputs, old.get(c.id, []))
        errors.extend(f"{q['title'][:40]}: run cell {c.id}: {p}" for p in rf.output_problems(new))
        before = old.get(c.id, [])
        if before and rf.canon_outputs(before) != rf.canon_outputs(new):
            sem = '' if rf.seen(before) == rf.seen(new) else (
                f'\n      stored: {rf.seen(before)!r:.300}\n      new:    {rf.seen(new)!r:.300}')
            r.not_accepted.append(f"{q['title'][:40]}: stored output of run cell {c.id} changes{sem}\n{byte_diff(before, new)}")
        elif not before:
            r.report.append(f"{q['title'][:40]}: run cell {c.id}: new output {rf.seen(new)!r:.300}")
        c.outputs = [nbf.from_dict(o) for o in new]
        c.execution_count = None
    fill(work, qs, sinks, results, errors, r.report, r.not_accepted)
    r.bad = [i for i, s in status.items() if s != 'ok']
    if errors:
        r.refused = errors
        return r
    if r.not_accepted and not accept:
        return r
    work.metadata[rf.STAMP_KEY] = rf.make_stamp(work, stack)
    r.report += [f'ACCEPTED: {x}' for x in r.not_accepted]
    if accept:
        r.not_accepted = []
    r.nb = work
    return r


def main(argv):
    if not argv or argv[0].startswith('-'):
        sys.exit(__doc__)
    path = Path(argv[0])
    opt = lambda name, default: argv[argv.index(name) + 1] if name in argv else default  # noqa: E731
    kernel, out = opt('--kernel', 'colablike'), Path(opt('--out', path))
    cache = Path(opt('--cache', DEFAULT_CACHE))
    nb = nbf.read(path, as_version=4)
    if '--static' in argv:
        report, refused = static_normalize(nb, path)
        if not refused:
            static_generate(nb, rf.setup_imports(nb), report, refused)
        r = Result()
        r.report, r.refused, r.nb = report, refused, nb
    else:
        r = sync(nb, path, kernel, '--accept' in argv, '--force' in argv, cache)
    for line in r.report:
        print('  -', line)
    if r.refused:
        print('REFUSED, nothing written:\n  ! ' + '\n  ! '.join(r.refused))
        return 2
    if r.not_accepted:
        print('NOT WRITTEN: these would change. Reread the Answer prose; if it is still right, run again with '
              '--accept:\n  * ' + '\n  * '.join(r.not_accepted))
        return 1
    if r.bad:
        print(f'  ! cells with reply status "error" (Run all would stop there): {r.bad}')
    nbf.validate(r.nb)
    nbf.write(r.nb, out)
    print(f'{"normalized" if "--static" in argv else "synced"} {path} -> {out}: {len(r.report)} change(s)')
    return 1 if r.bad else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
