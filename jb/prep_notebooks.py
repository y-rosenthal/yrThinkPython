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
- prepares the review pages copied from yr/ into jb/yr/ (see yr/README.md): each Answer (its
  explanation and the stored outputs of its run cells, without their code) becomes one closed
  dropdown; the concept lists, written as <details open><summary>Title</summary> ... </details>,
  become the same collapsible box the solutions use, shown; '# Your code here' cells (space for
  the reader's own code in Colab), the helper cell and the "Credits" heading are dropped; sync's
  markers are removed (values stay).
"""
import json
import re
import sys
from pathlib import Path
from glob import glob

import nbformat as nbf

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'yr' / 'tools'))
import review_format  # noqa: E402

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


def answer_dropdown(cells):
    """One closed dropdown cell for an Answer: its markdown and its run cells' stored outputs, in order."""
    parts = []
    for c in cells:
        if c['cell_type'] == 'markdown':
            parts.append(review_format.strip_markers(c['source']).strip('\n'))
        elif review_format.parse_run_cell(c['source']):
            parts.append(review_format.render_outputs(c.get('outputs', [])))
    body = '\n\n'.join(p for p in parts if p.strip())
    cell = nbf.v4.new_markdown_cell(f':::{{admonition}} Answer\n:class: dropdown\n\n{body}\n:::\n')
    raw_pictures(cell)
    return cell


def process_review_v3(ntbk, path):
    cells, out, expected = ntbk.cells, [], 0
    questions = {q['answer']: q['end'] for q in review_format.parse_page(ntbk) if q['answer'] is not None}
    i = 0
    while i < len(cells):
        c = cells[i]
        if i in questions:
            out.append(answer_dropdown(cells[i + 1:questions[i]]))
            expected += 1
            i = questions[i]
            continue
        i += 1
        if (c['cell_type'] == 'code' and c['source'].strip() == YOUR_CODE) or review_format.is_helper_cell(c):
            continue
        if c['cell_type'] == 'markdown':
            c['source'] = review_format.strip_markers(c['source'])
            if c['source'].startswith(review_format.CREDITS_HEADING):
                c['source'] = c['source'][len(review_format.CREDITS_HEADING):].lstrip('\n')
            raw_pictures(c)
            details_to_dropdown(c)
        process_cell(c)
        out.append(c)
    ntbk.cells = out
    # guard: one closed Answer dropdown per question, and nothing of the notebook machinery left
    dropdowns = sum(1 for c in out if c['cell_type'] == 'markdown' and c['source'].startswith(':::{admonition} Answer\n'))
    leftovers = [m for c in out if c['cell_type'] == 'markdown'
                 for m in re.findall(r'<!--|@title|run_code\(|ipykernel_[1-9]', c['source'])]
    if dropdowns != expected or leftovers:
        sys.exit(f'prep_notebooks: {path}: {dropdowns} Answer dropdowns for {expected} Answers, '
                 f'left over: {sorted(set(leftovers))}')


def process_review(path):
    ntbk = nbf.read(path, nbf.NO_CONVERT)
    if review_format.page_format(ntbk) != 'v3':
        sys.exit(f'prep_notebooks: {path}: review pages need "#### Answer" headings (yr/README.md)')
    process_review_v3(ntbk, path)
    nbf.write(ntbk, path)


# Collect a list of the notebooks in the content folder
paths = glob("chap*.ipynb")

for path in sorted(paths):
    print('prepping', path)
    process_notebook(path)

for path in sorted(glob("yr/*.ipynb")):
    print('prepping', path)
    process_review(path)
