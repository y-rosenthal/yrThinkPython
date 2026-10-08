"""Prepare the notebook copies in jb/ for the Jupyter Book build.

- adds Downey's display tags from soln_overlay.json (remove-input, remove-cell, section_*
  labels, ...; see update_overlay.py), so pages show and hide the same cells as his site
- strips the %%expect cell magic so the site shows plain code (outputs, produced by
  execute_notebooks.py, are kept)
- turns 'chapter*' / 'section*' cell tags into MyST cross-reference labels
- handles '# Solution goes here' cells: if solutions/chapNN.ipynb exists and has a
  code cell with the same id, the solution is shown on the site inside a collapsed
  "Suggested solution" dropdown (readers click to reveal it); otherwise the cell is
  blanked as before. The notebooks in chapters/ (which Colab opens) are never touched.
- prepares the review pages copied from yr/ into jb/yr/ (see yr/README.md): markdown cells
  written as <details><summary>Title</summary> ... </details> become the same collapsible
  box the solutions use (collapsed; or shown, for <details open>), and '# Your code here'
  cells (space for the reader's own code in Colab) are dropped from the website.
  New-format pages (prototype v2): each '#### Answer' section becomes one collapsed "Answer" dropdown
  holding its explanation and the STORED outputs of its run cells (code hidden; tracebacks without paths),
  and a guard stops the build if any answer would be published openly, or if the stored outputs are not
  what `review.sh sync` wrote for the current code (the sync stamp), or are too long.
"""
import json
import re
import sys
from pathlib import Path
from glob import glob

import nbformat as nbf

SOLUTIONS_DIR = Path(__file__).resolve().parent.parent / 'solutions'
OVERLAY = Path(__file__).resolve().parent / 'soln_overlay.json'
PLACEHOLDER = '# Solution goes here'

SOLUTIONS_NOTE = (
    'Suggested solutions are available on this page: below each exercise, '
    'click **Suggested solution** to reveal one. Try to solve the exercise '
    'yourself before you look.'
)


def is_placeholder(cell):
    return cell['cell_type'] == 'code' and cell['source'].startswith('# Solution')


def load_solutions(path):
    """Map cell id -> solution source for the solutions notebook matching `path`."""
    soln_path = SOLUTIONS_DIR / Path(path).name
    if not soln_path.exists():
        return {}
    soln = nbf.read(soln_path, nbf.NO_CONVERT)
    return {
        cell.get('id'): cell['source']
        for cell in soln.cells
        if cell['cell_type'] == 'code'
        and cell.get('id')
        and cell['source'].strip()
        and not is_placeholder(cell)
    }


def solution_cell(sources):
    """A markdown cell with the solution code in a collapsed dropdown."""
    blocks = '\n\n'.join(f'```python\n{src}\n```' for src in sources)
    md = f':::{{admonition}} Suggested solution\n:class: dropdown\n\n{blocks}\n:::\n'
    return nbf.v4.new_markdown_cell(md, metadata={'tags': ['solution']})


def process_cell(cell):
    # get tags
    tags = cell['metadata'].get('tags', [])

    if cell['cell_type'] == 'code':
        source = cell['source']

        # remove solutions
        if source.startswith('# Solution') or 'solution' in tags:
            cell['source'] = []

        # remove %%expect cell magic
        if source.startswith('%%expect'):
            t = source.split('\n')[1:]
            cell['source'] = '\n'.join(t)

    # add reference label
    for tag in tags:
        if tag.startswith('chapter') or tag.startswith('section'):
            # print(tag)
            label = f'({tag})=\n'
            cell['source'] = label + cell['source']


def merge_solutions(cells, solutions):
    """Replace runs of placeholder cells that have solutions with one dropdown cell."""
    out = []
    i = 0
    while i < len(cells):
        cell = cells[i]
        if is_placeholder(cell) and cell.get('id') in solutions:
            sources = []
            while i < len(cells) and is_placeholder(cells[i]) and cells[i].get('id') in solutions:
                sources.append(solutions[cells[i]['id']])
                i += 1
            out.append(solution_cell(sources))
            continue
        out.append(cell)
        i += 1
    return out


def add_note(cells):
    """Insert the reader note right after the '## Exercises' heading."""
    for i, cell in enumerate(cells):
        if cell['cell_type'] == 'markdown' and cell['source'].lstrip().startswith('## Exercises'):
            cells.insert(i + 1, nbf.v4.new_markdown_cell(SOLUTIONS_NOTE))
            return


def add_overlay_tags(cells, path):
    """Add the display tags recorded for this chapter in soln_overlay.json (matched by cell id)."""
    if not OVERLAY.exists():
        return
    tags = json.loads(OVERLAY.read_text()).get(Path(path).stem, {}).get('tags', {})
    for cell in cells:
        extra = [t for t in tags.get(cell.get('id'), []) if t not in cell['metadata'].get('tags', [])]
        if extra:
            cell['metadata']['tags'] = cell['metadata'].get('tags', []) + extra


def process_notebook(path):
    ntbk = nbf.read(path, nbf.NO_CONVERT)
    add_overlay_tags(ntbk.cells, path)

    solutions = load_solutions(path)
    if solutions:
        ntbk.cells = merge_solutions(ntbk.cells, solutions)
        add_note(ntbk.cells)
        print(f'  {len(solutions)} solution cell(s) merged from {SOLUTIONS_DIR.name}/{Path(path).name}')

    for cell in ntbk.cells:
        process_cell(cell)

    nbf.write(ntbk, path)


DETAILS = re.compile(r'\s*<details( open)?>\s*<summary>(.*?)</summary>(.*)</details>\s*', re.S)
YOUR_CODE = '# Your code here'


def details_to_dropdown(cell):
    """Turn a markdown <details> answer into a collapsed MyST admonition (same look as solutions)."""
    m = DETAILS.fullmatch(cell['source'])
    if cell['cell_type'] == 'markdown' and m:
        shown, title, body = m.group(1), re.sub(r'<[^>]+>', '', m.group(2)).strip(), m.group(3).strip()
        classes = 'dropdown toggle-shown' if shown else 'dropdown'  # toggle-shown: open by default
        cell['source'] = f':::{{admonition}} {title}\n:class: {classes}\n\n{body}\n:::\n'


TURTLE_IMG = re.compile(r'<img\b[^>]*\bdata-turtle\b[^>]*>')


def raw_pictures(cell):
    """Wrap turtle pictures in a <div>, so they are passed through as plain HTML. (MyST would
    otherwise turn a lone <img> into a Sphinx image and wrap it in a link to the image data.)"""
    if cell['cell_type'] == 'markdown':
        cell['source'] = TURTLE_IMG.sub(lambda m: f'<div class="turtle-picture">{m.group(0)}</div>', cell['source'])


# The review-page format is defined once, in yr/tools/review_v2.py (stdlib only; the real version will be
# yr/tools/review_format.py): the same renderer and stamp rules as sync and check.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'yr' / 'tools'))
from review_v2 import (ANSWER_HEADING, output_problems, parse_run_cell, render_outputs, stamp_problems,
                       strip_error_comments, heading_level)

CREDITS_LINE = re.compile(r'\A## Credits\n+')
CREDIT_LINE = '*Summary and questions by'


def answer_sections(cells, problems):
    """Turn each '#### Answer' section (the heading and every cell under it, up to the next heading of level 4
    or higher) into ONE collapsed "Answer" dropdown, like the solutions: its markdown cells, in order (without
    the invisible '<!-- error: X -->' records), with each run cell replaced by its STORED outputs (the website
    does not execute review pages, and the run cell's code is the question's code shown above). The heading
    disappears, so it is not listed in the page's contents. Pages still in the <details> format have no such
    heading: nothing changes."""
    out, i = [], 0
    while i < len(cells):
        c = cells[i]
        if not (c['cell_type'] == 'markdown' and c['source'].strip() == ANSWER_HEADING):
            out.append(c)
            i += 1
            continue
        parts, j = [], i + 1
        while j < len(cells):
            d = cells[j]
            lev = heading_level(d['source']) if d['cell_type'] == 'markdown' else None
            if lev is not None and lev <= 4:
                break
            if d['cell_type'] == 'markdown':
                body = strip_error_comments(d['source']).strip()
            else:
                if parse_run_cell(d['source']) is None:
                    problems.append(f'cell {d.get("id")}: a code cell inside an Answer is not a run cell')
                problems.extend(f'run cell {d.get("id")}: {p}' for p in output_problems(d.get('outputs', [])))
                body = render_outputs(d.get('outputs', []))
            if body:
                parts.append(body)
            j += 1
        body = '\n\n'.join(parts)
        colons = ':' * max(3, 1 + max((len(m) for m in re.findall(r'^:+', body, re.M)), default=0))
        cell = nbf.v4.new_markdown_cell(f'{colons}{{admonition}} Answer\n:class: dropdown\n\n{body}\n{colons}\n')
        cell['id'] = c.get('id') or cell['id']
        out.append(cell)
        i = j
    return out


def review_guard(ntbk, cells, path, problems):
    """Stop the build if a review page would publish an answer openly, or a stale or missing output."""
    questions = [k for k, c in enumerate(cells) if c['cell_type'] == 'markdown' and c['source'].lstrip().startswith('### Question')]
    answers = [k for k, c in enumerate(cells) if c['cell_type'] == 'markdown'
               and re.match(r':{3,}\{admonition\} Answer\n:class: dropdown\n', c['source'])]
    if len(answers) != len(questions):
        problems.append(f'{len(questions)} questions but {len(answers)} "Answer" dropdowns')
    for k, c in enumerate(cells):
        if c['cell_type'] == 'markdown' and k not in answers and re.search(r'^#### Answer\s*$', c['source'], re.M):
            problems.append(f'cell {k}: an "#### Answer" heading survived')
    for k in answers:                      # nothing between an Answer and the next question / section / credits
        for d in cells[k + 1:]:
            if d['cell_type'] == 'markdown' and ((heading_level(d['source']) or 9) <= 3 or d['source'].startswith(CREDIT_LINE)):
                break
            problems.append(f'cell {d.get("id")}: content after an Answer dropdown, before the next question (would be '
                            f'shown openly)')
    for c in cells:
        if c['cell_type'] == 'code' and c.get('outputs') and 'remove-cell' not in c['metadata'].get('tags', []):
            problems.append(f'code cell {c.get("id")} has stored outputs and would show them openly')
    if problems:
        raise SystemExit(f'prep_notebooks.py: {path}: refusing to build:\n  ' + '\n  '.join(problems))


def process_review(path):
    ntbk = nbf.read(path, nbf.NO_CONVERT)
    problems = []
    if any(c['cell_type'] == 'markdown' and c['source'].strip() == ANSWER_HEADING for c in ntbk.cells):
        problems.extend(stamp_problems(ntbk))         # new-format page: outputs must be what sync wrote
    ntbk.cells = [c for c in ntbk.cells
                  if not (c['cell_type'] == 'code' and c['source'].strip() == YOUR_CODE)]
    ntbk.cells = answer_sections(ntbk.cells, problems)
    for cell in ntbk.cells:
        if cell['cell_type'] == 'markdown':
            cell['source'] = CREDITS_LINE.sub('', cell['source'])  # '## Credits' is for Colab/Jupyter only
        raw_pictures(cell)
        details_to_dropdown(cell)
        process_cell(cell)
    review_guard(ntbk, ntbk.cells, path, problems)
    nbf.write(ntbk, path)


# Collect a list of the notebooks in the content folder
paths = glob("chap*.ipynb")

for path in sorted(paths):
    print('prepping', path)
    process_notebook(path)

for path in sorted(glob("yr/*.ipynb")):
    print('prepping', path)
    process_review(path)
