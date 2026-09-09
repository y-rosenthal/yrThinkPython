"""Prepare the notebook copies in jb/ for the Jupyter Book build.

- strips the %%expect cell magic so the site shows plain code
- turns 'chapter*' / 'section*' cell tags into MyST cross-reference labels
- handles '# Solution goes here' cells: if solutions/chapNN.ipynb exists and has a
  code cell with the same id, the solution is shown on the site inside a collapsed
  "Suggested solution" dropdown (readers click to reveal it); otherwise the cell is
  blanked as before. The notebooks in chapters/ (which Colab opens) are never touched.
"""
from pathlib import Path
from glob import glob

import nbformat as nbf

SOLUTIONS_DIR = Path(__file__).resolve().parent.parent / 'solutions'
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


def process_notebook(path):
    ntbk = nbf.read(path, nbf.NO_CONVERT)

    solutions = load_solutions(path)
    if solutions:
        ntbk.cells = merge_solutions(ntbk.cells, solutions)
        add_note(ntbk.cells)
        print(f'  {len(solutions)} solution cell(s) merged from {SOLUTIONS_DIR.name}/{Path(path).name}')

    for cell in ntbk.cells:
        process_cell(cell)

    nbf.write(ntbk, path)


# Collect a list of the notebooks in the content folder
paths = glob("chap*.ipynb")

for path in sorted(paths):
    print('prepping', path)
    process_notebook(path)
