#!/usr/bin/env python3
"""Create review notebooks and add, list or renumber their questions. Stdlib only.

  review_cells.py new NN "Chapter title"            create yr/chapNN_review.ipynb (skeleton)
  review_cells.py list NOTEBOOK                      list the questions
  review_cells.py add NOTEBOOK SPEC [--before N]     insert the cells in SPEC (default: after the
                                                     last question; --before 7: before Question 7)
  review_cells.py renumber NOTEBOOK                  number the questions 1, 2, 3, ... in order

SPEC is a text file of cells, each starting with a line "%%% <kind>":

  %%% markdown                     a markdown cell (the text that follows)
  %%% code [tag ...]               a code cell, e.g. "%%% code raises-exception"
  %%% placeholder                  a "# Your code here" cell (no text follows)
  %%% answer                       a collapsible Answer (markdown that follows goes inside it)

Example: a new question

  %%% markdown
  ### Question 20 (medium): what is displayed?
  %%% code
  print(7 / 2)
  %%% answer
  ```text
  3.5
  ```

  `/` always produces a float.

After adding questions with turtle pictures, run `yr/tools/review.sh images NOTEBOOK`, then
`yr/tools/review.sh check NOTEBOOK`. See yr/README.md for the format and style rules.
"""
import json
import re
import secrets
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
QUESTION = re.compile(r'(\s*### Question )(\d+)\b')


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
            'metadata': {'tags': list(tags)}, 'outputs': [], 'source': lines(s)}


def parse_spec(spec, used):
    cells = []
    for chunk in re.split(r'^%%% ', Path(spec).read_text(encoding='utf-8'), flags=re.M)[1:]:
        head, _, body = chunk.partition('\n')
        kind, *tags = head.split()
        if kind == 'markdown':
            cells.append(md_cell(body, used))
        elif kind == 'code':
            cells.append(code_cell(body, used, tags))
        elif kind == 'placeholder':
            cells.append(code_cell('# Your code here', used))
        elif kind == 'answer':
            cells.append(md_cell(f'<details>\n<summary>Answer</summary>\n\n{body.strip()}\n\n</details>', used))
        else:
            sys.exit(f'unknown cell kind in {spec}: {kind!r}')
    return cells


def question_starts(nb):
    return [i for i, c in enumerate(nb['cells']) if c['cell_type'] == 'markdown' and QUESTION.match(text(c))]


def cmd_list(path):
    nb = load(path)
    for i in question_starts(nb):
        print(f'cell {i:3}: {text(nb["cells"][i]).strip().splitlines()[0][4:]}')


def cmd_add(path, spec, before=None):
    nb = load(path)
    used = {c.get('id') for c in nb['cells']}
    new = parse_spec(spec, used)
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


def cmd_renumber(path):
    nb = load(path)
    for n, i in enumerate(question_starts(nb), 1):
        cell = nb['cells'][i]
        cell['source'] = lines(QUESTION.sub(lambda m: f'{m.group(1)}{n}', text(cell), count=1))
    save(nb, path)
    refs = [i for i, c in enumerate(nb['cells'])
            if re.search(r'\bQuestion \d+\b', text(c)) and not QUESTION.match(text(c))]
    print(f'renumbered {len(question_starts(nb))} questions in {path}')
    if refs:
        print('check these cells, which mention "Question N" in their text:', refs)


SKELETON = [
    ('md', '''# {NN}b. Prof. Rosenthal's Review

A review of [Chapter {N}: {TITLE}](https://y-rosenthal.github.io/yrThinkPython/chap{NN}.html),
for students who have already studied the chapter.
Use the two lists under **Concepts covered** as a checklist (click a list's title to hide it), then work through the **Questions**, which go from easy to hard.
Each question has a suggested answer: click **Answer** to reveal it, but try the question yourself first.

[Run this page on Colab](https://colab.research.google.com/github/y-rosenthal/yrThinkPython/blob/v3/yr/chap{NN}_review.ipynb)'''),
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

Run the next cell first.'''),
    ('setup', '''# Setup for the questions below (imports, downloads of helper files, ...)
import math'''),
    ('md', '''*Summary and questions by Prof. Y. Rosenthal, based on*
[Think Python: 3rd Edition](https://allendowney.github.io/ThinkPython/index.html) *by Allen B. Downey.*
*Text license:* [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International](https://creativecommons.org/licenses/by-nc-sa/4.0/)'''),
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
    print(f'created {path.relative_to(ROOT)}')


if __name__ == '__main__':
    a = sys.argv[1:]
    if a[:1] == ['new'] and len(a) == 3:
        cmd_new(a[1], a[2])
    elif a[:1] == ['list'] and len(a) == 2:
        cmd_list(a[1])
    elif a[:1] == ['renumber'] and len(a) == 2:
        cmd_renumber(a[1])
    elif a[:1] == ['add'] and len(a) in (3, 5) and (len(a) == 3 or a[3] == '--before'):
        cmd_add(a[1], a[2], int(a[4]) if len(a) == 5 else None)
    else:
        sys.exit(__doc__)
