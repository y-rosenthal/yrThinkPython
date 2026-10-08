"""Run the chapter notebooks copied into jb/ so the website shows their outputs.

The chapters/ notebooks are committed without outputs, and Jupyter Book's own execution is off
(_config.yml), so this step produces the outputs, as Downey's site has them. For each jb/chapNN.ipynb:

1. Make a scratch copy in which each '# Solution goes here' cell holds a solution: ours from
   solutions/chapNN.ipynb if there is one, otherwise Downey's from soln_overlay.json. Then the
   exercise test cells work and draw their example pictures. The solution code is never shown:
   only outputs of the other cells are kept.
2. Execute it in a scratch folder that holds this repo's helper files (thinkpython.py,
   diagram.py, ...), a copy of jupyturtle.py that does not pause between steps, and an input()
   stub, so the download() cells find their files and nothing waits.
3. Copy the outputs back into jb/chapNN.ipynb, cell by cell (matched by id). An error output is
   kept only where it is meant to be (%%expect cells and cells tagged raises-exception);
   other errors are dropped and reported.

If a notebook cannot be executed at all, it is left without outputs and a warning is printed;
the build goes on. Run from jb/, after copying the chapters and before prep_notebooks.py:

    python execute_notebooks.py [chapNN.ipynb ...]      (default: every chap*.ipynb in jb/)
"""
import copy
import json
import os
import shutil
import sys
import tempfile
import time
import urllib.request
from glob import glob
from pathlib import Path

import nbformat as nbf
from nbclient import NotebookClient

JB = Path(__file__).resolve().parent
ROOT = JB.parent
HELPERS = ['thinkpython.py', 'diagram.py', 'structshape.py', 'words.txt', 'photos.zip']
JUPYTURTLE = 'https://github.com/ramalho/jupyturtle/releases/download/2024-03/jupyturtle.py'
GITHUB = os.environ.get('GITHUB_ACTIONS') == 'true'

FAKE_INPUT = '''
# ipykernel re-binds builtins.input to Kernel.raw_input before every cell, so patch the method.
from ipykernel.kernelbase import Kernel
def _fake_raw_input(self, prompt=""):
    print(prompt, end="")
    return "an African or a European swallow?"
Kernel.raw_input = _fake_raw_input
Kernel.getpass = _fake_raw_input
'''


def warn(msg):
    print(f'::warning::{msg}' if GITHUB else f'  WARNING: {msg}')


def is_placeholder(cell):
    return cell.cell_type == 'code' and cell.source.startswith('# Solution')


def our_solutions(name):
    path = ROOT / 'solutions' / name
    if not path.exists():
        return {}
    return {c.get('id'): c.source for c in nbf.read(path, nbf.NO_CONVERT).cells
            if c.cell_type == 'code' and c.source.strip() and not is_placeholder(c)}


def prepare_workdir(work):
    for f in HELPERS:
        if (ROOT / f).exists():
            shutil.copy(ROOT / f, work)
    with urllib.request.urlopen(JUPYTURTLE) as r:
        src = r.read().decode()
    # no pause after each step: same drawing, much faster
    (work / 'jupyturtle.py').write_text(src.replace('time.sleep(self.delay)', 'pass'))
    startup = work / 'ipython' / 'profile_default' / 'startup'
    startup.mkdir(parents=True)
    (startup / '00-fake-input.py').write_text(FAKE_INPUT)
    os.environ['IPYTHONDIR'] = str(work / 'ipython')


def execute(path, work, overlay):
    nb = nbf.read(path, nbf.NO_CONVERT)
    name = Path(path).name
    entry = overlay.get(Path(path).stem, {})
    tags = entry.get('tags', {})
    solutions = {**entry.get('solutions', {}), **our_solutions(name)}

    run = copy.deepcopy(nb)
    for cell in run.cells:
        if is_placeholder(cell) and cell.get('id') in solutions:
            cell.source = solutions[cell['id']]

    start = time.time()
    try:
        NotebookClient(run, timeout=600, kernel_name='python3', allow_errors=True,
                       resources={'metadata': {'path': str(work)}}).execute()
    except Exception as e:  # kernel died, a cell timed out, ...
        warn(f'{name}: not executed ({type(e).__name__}: {e}); the page will have no outputs')
        return

    ran = {c.get('id'): c for c in run.cells}
    dropped = []
    for cell in nb.cells:
        if cell.cell_type != 'code' or is_placeholder(cell) or cell.get('id') not in ran:
            continue
        expected = cell.source.startswith('%%expect') or 'raises-exception' in (
            cell.metadata.get('tags', []) + tags.get(cell.get('id'), []))
        outputs = []
        for o in ran[cell['id']].get('outputs', []):
            if o.output_type == 'error' and not expected:
                dropped.append(f"{cell['id']} ({o.ename})")
                continue
            outputs.append(o)
        if '%xmode' in cell.source:
            outputs = []  # "Exception reporting mode: ..." is noise on a web page
        cell.outputs = outputs
        cell.execution_count = ran[cell['id']].get('execution_count')
    nbf.write(nb, path)
    print(f'  {name}: executed in {time.time() - start:.0f}s')
    if dropped:
        warn(f'{name}: dropped unexpected error output in {len(dropped)} cell(s): {", ".join(dropped)}')


def main(paths):
    overlay_path = JB / 'soln_overlay.json'
    overlay = json.loads(overlay_path.read_text()) if overlay_path.exists() else {}
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        prepare_workdir(work)
        for path in paths:
            print('executing', path)
            execute(path, work, overlay)


if __name__ == '__main__':
    os.chdir(JB)
    main(sys.argv[1:] or sorted(glob('chap*.ipynb')))
