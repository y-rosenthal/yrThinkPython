"""One-off converter (prototype v2): old <details> review page -> v2 layout. Static: no kernel needed.

    python convert_v2.py OLD.ipynb NEW.ipynb REMOVED.json

- question code cells -> '```python run' markdown cells (same id); part labels folded in;
  definition-only cells and '# Your code here' cells stay code cells
- <details> Answer -> '#### Answer' heading (old id, saved collapsed) + explanation cells; each run block
  gets ONE hidden-code run cell, placed where the Answer's expected-output block (```text block or
  data-turtle picture) was. That block is removed (it would duplicate the stored real output) and
  written to REMOVED.json, so verify_removed.py can prove it equalled the real output.
- multi-part Answers are split at '**Part x:**' paragraphs (interleaved) and the summary paragraph
  goes into its own cell after the last run cell
- page edits: title sentence, intro, help note, managed run_code cell, '## Credits', wording edits
Run cells get no outputs here: sync_v2.py runs the page, wraps exactly the raising run cells in
run_code(...) and stores the outputs.
"""
import ast
import copy
import json
import re
import sys

import nbformat as nbf

sys.path.insert(0, __import__('os').path.dirname(__file__))
from review_v2 import (ANSWER_HEADING, CREDITS_HEADING, HELP_CELL, PLACEHOLDER, RUN_CELL_METADATA, RUN_CODE_CELL,
                       render_run_cell, source, stable_id)

DETAILS = re.compile(r'\s*<details>\s*<summary>Answer</summary>\s*(.*?)\s*</details>\s*$', re.S)
OLD_RUN_CODE = re.compile(r'^\s*run_code\(')
PART_LINE = re.compile(r'\n*\*\*Part (?P<part>[a-z])\*\*\s*$')
PART_PARA = re.compile(r'^\*\*Part [a-z]:\*\*', re.M)
CREDIT = '*Summary and questions by'
EXPECTED = re.compile(r'```text\n.*?\n```|<img\b[^>]*\bdata-turtle\b[^>]*>', re.S)

# Page-specific text edits: (old, new); each must match exactly once on the page.
TITLE_EDIT = ('Each question has a suggested answer: click **Answer** to reveal it, but try the question yourself first.',
              'Each question has a suggested answer under **Answer**. Try the question first, then open the Answer.')
INTRO_DELETE = re.compile(r'\n*Some questions show their code inside `run_code.*?prediction\.\n*', re.S)
INTRO_EDIT = ('Run the next cell first: it downloads `jupyturtle`, imports those functions, and defines `run_code`.',
              'The setup cell below downloads `jupyturtle` and imports those functions.')
QUESTION_EDITS = [
    ('Predict what this code displays, then run it to check.', 'Predict what this code displays, then open the Answer to check.'),
    ('Each cell has one mistake. Predict the error for each, then run the cells to check.',
     'Each part has one mistake. Predict the error for each, then open the Answer to check.'),
    ('Describe what it draws, then run the cell to check.', 'Describe what it draws, then open the Answer to check.'),
]
# Answer prose: the removed ```text block named the error; the prose now names it (checked by check_v2.py)
ANSWER_EDITS = [
    ('**Part a:** `=` assigns; comparing needs `==`:',
     '**Part a:** `=` assigns; comparing needs `==`, so this is a `SyntaxError`:'),
    ('**Part b:** The header of an `if` statement must end with a colon:',
     '**Part b:** The header of an `if` statement must end with a colon, so this is a `SyntaxError`:'),
    ('**Part c:** The second line is indented by one space, but it is not inside a block:',
     '**Part c:** The second line is indented by one space, but it is not inside a block, so this is an `IndentationError`:'),
    ('All three are found before the cell runs, so nothing is displayed or assigned.',
     'Each is found before any of that part\'s code runs, so nothing is displayed or assigned.'),
    ('This is infinite recursion. It ends when there are too many frames on the stack:',
     'This is infinite recursion. It ends with a `RecursionError` when there are too many frames on the stack:'),
]
# Summary paragraphs of multi-part Answers (explicit list, read by hand; text after ANSWER_EDITS)
SUMMARY_STARTS = ["Each is found before any of that part's code runs"]

used = {}


def edit(text, old, new):
    if old in text:
        used[old] = used.get(old, 0) + text.count(old)
        return text.replace(old, new)
    return text


def md_cell(text, cid, **meta):
    c = nbf.v4.new_markdown_cell(text.strip('\n'))
    c.id = cid
    c.metadata.update(meta)
    return c


def run_cell(code, wrapped, part, cid):
    c = nbf.v4.new_code_cell(render_run_cell(code, wrapped, part))
    c.id = cid
    c.metadata = copy.deepcopy(RUN_CELL_METADATA)
    return c


def old_code(src):
    """The question's code: the old run_code(\"\"\"...\"\"\") wrapper removed with ast."""
    if OLD_RUN_CODE.match(src):
        arg = ast.parse(src).body[0].value.args[0].value
        return arg.strip('\n'), True
    return src.strip('\n'), False


def definition_only(cell):
    if 'raises-exception' in cell.metadata.get('tags', []) or OLD_RUN_CODE.match(cell.source):
        return False
    try:
        tree = ast.parse(cell.source)
    except SyntaxError:
        return False
    return all(isinstance(s, (ast.FunctionDef, ast.ClassDef, ast.Import, ast.ImportFrom, ast.Assign)) for s in tree.body)


def split_expected(segment):
    """(before, block, after): the first expected-output block not preceded by a ```python block."""
    m = EXPECTED.search(segment)
    if not m or '```python' in segment[:m.start()]:
        return segment, None, ''
    return segment[:m.start()], m.group(0), segment[m.end():]


def convert_answer(answer, runs, title, removed):
    """Cells for one Answer: heading, then explanation cells with the run cells interleaved."""
    aid = answer.id
    head = md_cell(ANSWER_HEADING, aid, id=aid, **{'jp-MarkdownHeadingCollapsed': True})
    body = DETAILS.match(answer.source).group(1)
    for old, new in ANSWER_EDITS:
        body = edit(body, old, new)
    out, k = [head], 0

    def add_md(text):
        nonlocal k
        if text.strip():
            out.append(md_cell(text, stable_id(aid, 'md', str(k))))
            k += 1

    if not runs:
        add_md(body)
        return out
    summary = ''
    for start in SUMMARY_STARTS:
        pos = body.find(start)
        if pos >= 0 and len(runs) > 1:
            body, summary = body[:pos], body[pos:]
    if len(runs) == 1:
        segments = [body]
    else:
        starts = [m.start() for m in PART_PARA.finditer(body)]
        if len(starts) != len(runs):
            sys.exit(f'{title}: {len(runs)} run blocks but {len(starts)} "**Part x:**" paragraphs')
        add_md(body[:starts[0]])
        segments = [body[a:b] for a, b in zip(starts, starts[1:] + [len(body)])]
    for (part, code, wrapped), seg in zip(runs, segments):
        before, block, after = split_expected(seg)
        add_md(before)
        out.append(run_cell(code, wrapped, part, stable_id(aid, 'run', part or '-')))
        if block is not None:
            removed.append({'question': title, 'part': part, 'block': block if block.startswith('```') else '<img data-turtle ...>'})
        add_md(after)
    add_md(summary)
    return out


def main(src, dst, removed_path):
    nb = nbf.read(src, as_version=4)
    cells, out, collapsed, removed = nb.cells, [], [], []
    i = 0
    while i < len(cells):
        c = cells[i]
        s = c.source
        if i == 0:
            c.source = edit(s, *TITLE_EDIT)
        if c.cell_type == 'markdown' and s.lstrip().startswith('## Questions'):
            c.source = edit(INTRO_DELETE.sub('\n\n', s), *INTRO_EDIT).strip('\n')
            out.append(c)
            out.append(md_cell(HELP_CELL, stable_id('help-note'), tags=['remove-cell']))
            i += 1
            continue
        if c.cell_type == 'code' and 'setup' in c.metadata.get('tags', []):
            c.source = re.sub(r'\n*def run_code\(code\):.*', '', s, flags=re.S).rstrip('\n')
            out.append(c)
            rc = nbf.v4.new_code_cell(RUN_CODE_CELL)
            rc.id = stable_id('run-code-cell')
            rc.metadata['tags'] = ['setup', 'remove-cell']
            out.append(rc)
            i += 1
            continue
        if c.cell_type == 'markdown' and s.lstrip().startswith(CREDIT):
            c.source = CREDITS_HEADING + '\n\n' + s
        if not (c.cell_type == 'markdown' and s.lstrip().startswith('### ')):
            out.append(c)
            i += 1
            continue
        # one question: up to the next heading of level <= 3 or the credit line
        j = i + 1
        while j < len(cells) and not (cells[j].cell_type == 'markdown' and (
                re.match(r'\s*#{1,3} ', cells[j].source) or cells[j].source.lstrip().startswith(CREDIT))):
            j += 1
        title = s.lstrip('# ').split('\n')[0]
        label, runs, answer = None, [], None
        for g in cells[i:j]:
            if g.cell_type == 'markdown' and DETAILS.match(g.source):
                answer = g
                continue
            if g.cell_type == 'markdown':
                t = g.source
                for old, new in QUESTION_EDITS:
                    t = edit(t, old, new)
                m = PART_LINE.search(t)
                if m:
                    label, t = m.group('part'), t[:m.start()]
                if t.strip():
                    g.source = t.rstrip('\n')
                    out.append(g)
                continue
            if g.source.strip() == PLACEHOLDER or definition_only(g):
                out.append(g)
                continue
            code, wrapped = old_code(g.source)
            wrapped = wrapped or 'raises-exception' in g.metadata.get('tags', [])
            text = (f'**Part {label}**\n\n' if label else '') + f'```python run\n{code}\n```'
            out.append(md_cell(text, g.id))
            runs.append((label, code, wrapped))
            label = None
        if len(runs) == 1 and runs[0][0]:
            sys.exit(f'{title}: a single run block must not have a part label')
        if len(runs) > 1 and [r[0] for r in runs] != [chr(ord('a') + k) for k in range(len(runs))]:
            sys.exit(f'{title}: run blocks need labels a, b, c, ...: {[r[0] for r in runs]}')
        if answer is None:
            sys.exit(f'{title}: no <details> Answer')
        new = convert_answer(answer, runs, title, removed)
        collapsed.append(new[0].id)
        out.extend(new)
        i = j

    for old, new in [TITLE_EDIT, INTRO_EDIT] + QUESTION_EDITS + ANSWER_EDITS:
        if used.get(old) is None:
            print(f'WARNING: edit did not match: {old[:70]}')
    nb.cells = out
    nb.metadata['colab'] = {'collapsed_sections': collapsed}
    nbf.validate(nb)
    nbf.write(nb, dst)
    json.dump(removed, open(removed_path, 'w'), indent=1)
    print(f'wrote {dst}: {len(out)} cells, {len(collapsed)} collapsed Answers, {len(removed)} expected-output blocks removed')
    # wording that may refer to cells / running (review by hand)
    for k, cell in enumerate(out):
        if cell.cell_type == 'markdown':
            for m in re.finditer(r'[^\n]*(\bcells?\b|\brun (it|this)\b|run_code)[^\n]*', cell.source):
                print(f'  review wording, cell {k}: {m.group(0)[:110]}')


if __name__ == '__main__':
    main(*sys.argv[1:4])
