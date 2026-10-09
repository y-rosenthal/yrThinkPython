#!/usr/bin/env python3
"""Create review notebooks and add, list or renumber their questions. Stdlib only.

  review_cells.py new NN "Chapter title"            create yr/chapNN_review.ipynb (skeleton; then review.sh sync)
  review_cells.py list NOTEBOOK                      list the questions
  review_cells.py next NOTEBOOK [--before N]         print the number for a new question (at the end, or before
                                                     Question N: e.g. 3b between Questions 3 and 4)
  review_cells.py add NOTEBOOK SPEC [--before N]     insert the cells in SPEC (default: after the
                                                     last question; --before 7: before Question 7)
  review_cells.py renumber NOTEBOOK                  number the questions 1, 2, 3, ... in order:
                                                     ONLY between semesters (see below)

Question numbers stay fixed during a semester, because homework is assigned by number. A question
inserted between Questions 3 and 4 is numbered 3b (then 3c, ...); no other number changes, and no tool
renumbers on its own (review.sh check fails if a published number disappears). Run renumber only when
starting a new semester, to go back to 1, 2, 3, ...: it also rewrites "Question N" in the text, derive
markers and run-cell titles, and records the date so check knows the page was renumbered.

SPEC is a text file of cells, each starting with a line "%%% <kind>" (see yr/README.md, "Adding a question"):

  %%% markdown                     a markdown cell: the heading, the prompt, examples (```python blocks)
  %%% run [a]                      a run block: the question's code (Part a, b, ... with a letter)
  %%% code                         a definition cell (defines or assigns only; e.g. a helper the question provides)
  %%% placeholder [no-signature]   a "# Your code here" cell (write-code questions)
  %%% answer                       the "#### Answer" heading; markdown that follows becomes the first Answer cell
  %%% part a                       an Answer cell explaining part a (starts with "**Part a:**")

Example: a new question (then run review.sh sync, which writes its output and values, and review.sh check)

  %%% markdown
  ### Question 3b (easy): what is displayed?

  Predict what this code displays, then open the Answer to check.
  %%% run
  print(7 / 2)
  %%% answer
  `/` always produces a float: `7 / 2` is <!--=-->`?`.
"""
import datetime
import json
import re
import secrets
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import review_format as rf  # noqa: E402  (stdlib only)

QUESTION = re.compile(r'(\s*### Question )(\d+[a-z]?)\b')


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def save(nb, path):
    Path(path).write_text(json.dumps(nb, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')


def text(cell):
    return ''.join(cell['source'])


def lines(s):
    parts = s.strip('\n').split('\n')
    return [p + '\n' for p in parts[:-1]] + [parts[-1]]


def fresh_id(used):
    while True:
        i = secrets.token_hex(4)
        if i not in used:
            used.add(i)
            return i


def md_cell(s, used):
    return {'cell_type': 'markdown', 'id': fresh_id(used), 'metadata': {}, 'source': lines(s)}


def code_cell(s, used, tags=()):
    return {'cell_type': 'code', 'execution_count': None, 'id': fresh_id(used),
            'metadata': {'tags': list(tags)} if tags else {}, 'outputs': [], 'source': lines(s)}


def parse_spec(spec, used, new_format):
    cells = []
    for chunk in re.split(r'^%%% ', Path(spec).read_text(encoding='utf-8'), flags=re.M)[1:]:
        head, _, body = chunk.partition('\n')
        kind, *args = head.split()
        if kind == 'markdown':
            cells.append(md_cell(body, used))
        elif kind == 'code':
            if new_format and args:
                sys.exit(f'{spec}: new-format pages take no tags on code cells (definition cells only)')
            cells.append(code_cell(body, used, args))
        elif kind == 'placeholder':
            cells.append(code_cell(rf.PLACEHOLDER, used, [a for a in args if a == 'no-signature']))
        elif kind == 'run' and new_format:
            label = f'**Part {args[0]}**\n\n' if args else ''
            cells.append(md_cell(f'{label}~~~python\n{body.strip(chr(10))}\n~~~', used))
        elif kind == 'answer' and new_format:
            cells.append(md_cell(rf.ANSWER_HEADING, used))
            if body.strip():
                cells.append(md_cell(body, used))
        elif kind == 'part' and new_format and args:
            cells.append(md_cell(f'**Part {args[0]}:** {body.strip()}', used))
        else:
            sys.exit(f'unknown cell kind in {spec}: {kind!r} (see review_cells.py --help)')
    return cells


def question_starts(nb):
    return [i for i, c in enumerate(nb['cells']) if c['cell_type'] == 'markdown' and QUESTION.match(text(c))]


def numbers(nb):
    return [QUESTION.match(text(nb['cells'][i])).group(2) for i in question_starts(nb)]


def cmd_list(path):
    nb = load(path)
    for i in question_starts(nb):
        print(f'cell {i:3}: {text(nb["cells"][i]).strip().splitlines()[0][4:]}')


def next_number(nb, before=None):
    """The number for a new question: one more than the last at the end; before Question N, the previous
    question's number with the next free letter (3b, 3c, ...)."""
    nums = numbers(nb)
    if before is None:
        last = max((int(re.match(r'\d+', n).group(0)) for n in nums), default=0)
        return str(last + 1)
    if before not in nums:
        sys.exit(f'no Question {before}')
    k = nums.index(before)
    if k == 0:
        sys.exit(f'Question {before} is the first one: add the new question at the end, or renumber between semesters')
    prev = nums[k - 1]
    base = re.match(r'\d+', prev).group(0)
    start = prev[-1] if prev[-1].isalpha() else 'a'
    for letter in 'bcdefghijklmnopqrstuvwxyz':
        if letter > start and base + letter not in nums:
            return base + letter
    sys.exit('no free letter')


def cmd_add(path, spec, before=None):
    nb = load(path)
    used = {c.get('id') for c in nb['cells']}
    new_format = rf.page_format(nb) in ('v3', 'empty')
    if not new_format:
        sys.exit(f'{path} has <details> Answers, the old format: write Answers as "#### Answer" headings')
    new = parse_spec(spec, used, new_format)
    have = set(numbers(nb))
    for c in new:
        m = QUESTION.match(text(c))
        if m and m.group(2) in have:
            sys.exit(f'Question {m.group(2)} already exists: numbers stay fixed during a semester. Use '
                     f'Question {next_number(nb, before)} (review_cells.py next {path}'
                     f'{" --before " + before if before else ""})')
    starts = question_starts(nb)
    if before is not None:
        at = next((i for i in starts if QUESTION.match(text(nb['cells'][i])).group(2) == str(before)), None)
        if at is None:
            sys.exit(f'no Question {before} in {path}')
    else:
        # after the last question: just before the closing credit cell (the last cell), if any
        at = len(nb['cells'])
        if starts and nb['cells'][-1]['cell_type'] == 'markdown' and at - 1 > starts[-1]:
            at -= 1
    nb['cells'][at:at] = new
    save(nb, path)
    print(f'inserted {len(new)} cell(s) at position {at} in {path}')
    print('next: review.sh sync, then review.sh check')


def cmd_renumber(path):
    nb = load(path)
    mapping = {old: str(n) for n, old in enumerate(numbers(nb), 1)}
    parts = {i: (q['run_part'][i] if q['run_part'][i] is not False else None)
             for q in rf.parse_page(nb) for i in q['run_cells']}       # before the numbers change

    def ref(m):
        return m.group(1) + mapping.get(m.group(2), m.group(2))

    for c in nb['cells']:
        if c['cell_type'] == 'markdown':
            s = re.sub(r'(\bQuestions? )(\d+[a-z]?)\b', ref, text(c))     # headings and "Question N" in the text
            s = re.sub(r'(\bfrom=Q)(\d+[a-z]?)\b', ref, s)                 # derive markers
            c['source'] = lines(s) if s else []
    for q in rf.parse_page(nb):                 # run-cell titles name the question: rewrite them
        for i in q['run_cells']:
            info = rf.parse_run_cell(text(nb['cells'][i]))
            nb['cells'][i]['source'] = lines(rf.render_run_cell(info['code'], info['wrapped'], q['number'], parts[i]))
    stamp = nb['metadata'].setdefault(rf.STAMP_KEY, {})
    stamp['renumbered'] = datetime.date.today().isoformat()
    save(nb, path)
    changed = {o: n for o, n in mapping.items() if o != n}
    print(f'renumbered {len(mapping)} questions in {path}: {changed or "no number changed"}')
    print('"Question N" in the text and derive markers were rewritten too; check them, then run review.sh sync')


SKELETON = [
    ('md', rf.TITLE_CELL),
    ('md', '## Concepts covered'),
    ('md', '''<details open>
<summary><strong>Python Syntax and Semantics</strong></summary>

**TODO group label**

- TODO

</details>'''),
    ('md', '''<details open>
<summary><strong>Definitions, etc.</strong></summary>

**Definitions**

- DEFINITION: **TODO** is ...

**Other ideas**

- TODO

</details>'''),
    ('md', '''## Questions

The setup cell below imports `math`.'''),
    ('setup', '''# Setup for the questions below (imports, downloads of helper files, ...)
import math'''),
    ('md', rf.CREDITS),
]


def cmd_new(nn, title):
    nn = f'{int(nn):02d}'
    path = ROOT / 'yr' / f'chap{nn}_review.ipynb'
    if path.exists():
        sys.exit(f'{path} already exists')
    used = set()
    cells = []
    for kind, s in SKELETON:
        s = s.replace('{NN}', nn).replace('{N}', str(int(nn))).replace('{TITLE}', title)
        cells.append(code_cell(s, used, ['setup']) if kind == 'setup' else md_cell(s, used))
    meta = {'kernelspec': {'display_name': 'Python 3 (ipykernel)', 'language': 'python', 'name': 'python3'},
            'language_info': {'name': 'python'}}
    save({'cells': cells, 'metadata': meta, 'nbformat': 4, 'nbformat_minor': 5}, path)
    print(f'created {path.relative_to(ROOT)}; add questions, then run yr/tools/review.sh sync on it')


if __name__ == '__main__':
    a = sys.argv[1:]
    before = a[a.index('--before') + 1] if '--before' in a else None
    if a[:1] == ['new'] and len(a) == 3:
        cmd_new(a[1], a[2])
    elif a[:1] == ['list'] and len(a) == 2:
        cmd_list(a[1])
    elif a[:1] == ['next'] and len(a) in (2, 4):
        print(next_number(load(a[1]), before))
    elif a[:1] == ['renumber'] and len(a) == 2:
        cmd_renumber(a[1])
    elif a[:1] == ['add'] and len(a) in (3, 5) and (len(a) == 3 or a[3] == '--before'):
        cmd_add(a[1], a[2], before)
    else:
        sys.exit(__doc__)
