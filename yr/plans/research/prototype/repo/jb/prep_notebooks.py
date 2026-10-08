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
"""
import json
import os
import re
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


ANSWER_HEADING = re.compile(r'\s*#### Answer\s*$')
HEADING = re.compile(r'\s*(#{1,6}) ')
RUN_CODE = re.compile(r'\s*run_code\("""\n(.*?)\n?"""\)\s*$', re.S)
SHOW_RUN_CELLS = os.environ.get('REVIEW_SHOW_RUN_CELLS') == '1'


def run_cell_as_block(source):
    """The code of an Answer's run cell, as a ```python block: without its first-line comment
    ('# The question's code ...') and without the run_code(\"\"\"...\"\"\") wrapper."""
    lines = source.strip().split('\n')
    if lines and lines[0].startswith('#'):
        lines = lines[1:]
    code = '\n'.join(lines)
    m = RUN_CODE.match(code)
    return f'```python\n{m.group(1) if m else code}\n```'


def answer_sections(cells):
    """Turn each '#### Answer' heading section (the heading and every cell under it, up to the next
    heading of level 4 or higher) into one collapsed dropdown, like the solutions. The Answer's code
    cells only re-run the question's code (shown just above, as a ```python block) so the reader can
    see its live output in Colab; the website does not execute the review pages, so they are left
    out (or, with REVIEW_SHOW_RUN_CELLS=1, shown as ```python blocks). The heading itself
    disappears, so it is not listed in the page's table of contents."""
    out, i = [], 0
    while i < len(cells):
        c = cells[i]
        if not (c['cell_type'] == 'markdown' and ANSWER_HEADING.match(c['source'])):
            out.append(c)
            i += 1
            continue
        parts, j = [], i + 1
        while j < len(cells):
            d = cells[j]
            m = d['cell_type'] == 'markdown' and HEADING.match(d['source'])
            if m and len(m.group(1)) <= 4:
                break
            if d['cell_type'] == 'markdown':
                parts.append(d['source'].strip())
            elif SHOW_RUN_CELLS and d['source'].strip():
                parts.append(run_cell_as_block(d['source']))
            j += 1
        body = '\n\n'.join(parts)
        cell = nbf.v4.new_markdown_cell(f':::{{admonition}} Answer\n:class: dropdown\n\n{body}\n:::\n')
        cell['id'] = c.get('id') or cell['id']
        out.append(cell)
        i = j
    return out


def process_review(path):
    ntbk = nbf.read(path, nbf.NO_CONVERT)
    ntbk.cells = [c for c in ntbk.cells
                  if not (c['cell_type'] == 'code' and c['source'].strip() == YOUR_CODE)]
    for cell in ntbk.cells:
        raw_pictures(cell)
        details_to_dropdown(cell)
    ntbk.cells = answer_sections(ntbk.cells)
    for cell in ntbk.cells:
        process_cell(cell)
    nbf.write(ntbk, path)


# Collect a list of the notebooks in the content folder
paths = glob("chap*.ipynb")

for path in sorted(paths):
    print('prepping', path)
    process_notebook(path)

for path in sorted(glob("yr/*.ipynb")):
    print('prepping', path)
    process_review(path)
