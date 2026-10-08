"""Check a review notebook's questions and answers by running them.

Usage (through the wrapper, which sets up the venv):
    yr/tools/review.sh check yr/chap04_review.ipynb

What it checks (a question starts at a '### ' heading; see yr/README.md for the format):
  1. The notebook runs top to bottom. A code cell may raise only if it is tagged "raises-exception".
  2. "What is displayed" answers are right: whatever a question's code cell prints must appear,
     exactly, as one of the ```text blocks in its Answer; an error it raises ("TypeError: ...")
     must appear in one of them too.
  3. Every ```python block in an Answer runs on its own, unchanged, as a .py file in an empty
     folder (with only jupyturtle.py next to it). So answers carry their own imports and
     helper functions.
  4. Every "write code" question (one with a '# Your code here' cell) shows the header of each
     function to write (a ```python block "def name(params):" with "..." as its body; tag the
     '# Your code here' cell "no-signature" for a question that is about writing the header),
     and at least two examples: ```python blocks in the question, each followed by its output
     (a ```text block or a data-turtle picture). So does every question about wrong calls
     (a cell tagged "raises-exception" in a question whose code defines a function): it shows
     at least two correct calls with their output first.
  5. No empty data-turtle pictures (run `review.sh images` to draw them).
  6. A cell that raises a SyntaxError or IndentationError puts its code in a string run by run_code(...),
     so that Colab's editor does not underline the mistake before the student predicts it.
  7. No text that the website would turn into a symbol: (c) (r) (tm) +- become © ® ™ ±
     (MyST "replacements"). Write "part c" or "**c.**" instead.
Exit status 1 if any problem is found.
"""
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import nbformat as nbf
from nbclient import NotebookClient

TEXT_BLOCK = re.compile(r'```text\n(.*?)```', re.S)
PY_BLOCK = re.compile(r'```python\n(.*?)```', re.S)
EXAMPLE = re.compile(r'```python\n.*?```\s*(```text\n|<img\b[^>]*\bdata-turtle)', re.S)
ANSI = re.compile(r'\x1b\[[0-9;]*m')
HAZARD = re.compile(r'\((c|r|tm)\)|\+-', re.I)
PLACEHOLDER = '# Your code here'
SIGNATURE = re.compile(r'```python\n(?:\s*def \w+\(.*\):\n\s+\.\.\.\n)+')

problems = []
METRICS = {}


def is_answer(cell):
    return cell.cell_type == 'markdown' and re.match(r'\s*<details>\s*<summary>Answer</summary>', cell.source)


def groups_of(cells):
    groups, current = [], None
    for c in cells:
        if c.cell_type == 'markdown' and c.source.lstrip().startswith('### '):
            current = []
            groups.append(current)
        elif c.cell_type == 'markdown' and c.source.lstrip().startswith(('# ', '## ')):
            current = None
        if current is not None:
            current.append(c)
    return groups


def prose(md):
    """Markdown with code blocks, code spans and HTML tags removed."""
    md = re.sub(r'```.*?```', '', md, flags=re.S)
    md = re.sub(r'`[^`]*`', '', md)
    return re.sub(r'<[^>]+>', '', md)


def error_line(output):
    value = ANSI.sub('', output.get('evalue', ''))
    value = re.sub(r' \([^()]*, line \d+\)$', '', value)  # SyntaxError adds "(file, line 1)"
    return f"{output['ename']}: {value}"


def main(path, jupyturtle):
    nb = nbf.read(path, nbf.NO_CONVERT)

    for i, c in enumerate(nb.cells):
        if c.cell_type == 'markdown':
            for m in HAZARD.finditer(prose(c.source)):
                problems.append(f'cell {i}: "{m.group(0)}" would be shown as a symbol on the website')
            if re.search(r'<img\b[^>]*\bdata-turtle\b[^>]*src=""', c.source):
                problems.append(f'cell {i}: empty data-turtle picture (run: review.sh images {path})')

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        shutil.copy(jupyturtle, tmp)
        print('>> running the notebook ...')
        NotebookClient(nb, timeout=300, kernel_name='python3', allow_errors=True,
                       resources={'metadata': {'path': str(tmp)}}).execute()

        for g in groups_of(nb.cells):
            title = g[0].source.lstrip().splitlines()[0].lstrip('# ')
            answers = [c for c in g if is_answer(c)]
            texts = [t.strip() for a in answers for t in TEXT_BLOCK.findall(a.source)]
            code_cells = [c for c in g if c.cell_type == 'code' and c.source.strip() != PLACEHOLDER]

            M = METRICS.setdefault(title, dict(stdout=0, errors=0, pyblocks=0, writecode=False, wrongcall=False))
            for c in code_cells:
                tagged = 'raises-exception' in c.metadata.get('tags', [])
                stdout = ''.join(o.get('text', '') for o in c.outputs
                                 if o.output_type == 'stream' and o.name == 'stdout').strip()
                errors = [error_line(o) for o in c.outputs if o.output_type == 'error']
                if errors and not tagged:
                    problems.append(f'{title}: code cell raised {errors[0]} (tag it "raises-exception" if intended)')
                if tagged and not errors:
                    problems.append(f'{title}: cell is tagged "raises-exception" but raised nothing')
                M['stdout'] += bool(answers and stdout); M['errors'] += len(errors) if answers else 0
                if answers and stdout and stdout not in texts:
                    problems.append(f'{title}: the code prints\n{stdout}\n   but no ```text block in the Answer says exactly that')
                if any(e.startswith(('SyntaxError', 'IndentationError')) for e in errors) \
                        and not c.source.lstrip().startswith('run_code('):
                    problems.append(f'{title}: a cell with a syntax error must put its code in run_code(\"\"\"...\"\"\"), '
                                    'or Colab underlines the error before the student predicts it')
                for e in errors:
                    if answers and not any(e in t for t in texts):
                        problems.append(f'{title}: the code raises "{e}" but the Answer does not show it')

            for k, block in enumerate(PY_BLOCK.findall(''.join(a.source for a in answers)), 1):
                M['pyblocks'] += 1
                f = tmp / f'answer_{k}.py'
                f.write_text(block)
                r = subprocess.run([sys.executable, f.name], cwd=tmp, capture_output=True, text=True, timeout=120)
                if r.returncode != 0:
                    last = (r.stderr.strip().splitlines() or ['?'])[-1]
                    problems.append(f'{title}: answer code block {k} does not run on its own as a .py file: {last}')

            question = ''.join(c.source for c in g if c.cell_type == 'markdown' and not is_answer(c))
            n_examples = len(EXAMPLE.findall(question))
            placeholders = [c for c in g if c.cell_type == 'code' and c.source.strip() == PLACEHOLDER]
            M['writecode'] = bool(placeholders)
            if placeholders:
                if n_examples < 2:
                    problems.append(f'{title}: write-code question shows {n_examples} example(s) with output; needs at least 2')
                if not SIGNATURE.search(question) and not any(
                        'no-signature' in c.metadata.get('tags', []) for c in placeholders):
                    problems.append(f'{title}: write-code question does not show the function header '
                                    '(```python block "def name(params):" with body "...")')
            wrong_calls = any('raises-exception' in c.metadata.get('tags', []) for c in code_cells)
            M['wrongcall'] = bool(wrong_calls and any(re.search(r'^\s*def ', c.source, re.M) for c in code_cells))
            if wrong_calls and any(re.search(r'^\s*def ', c.source, re.M) for c in code_cells) and n_examples < 2:
                problems.append(f'{title}: question about wrong calls shows {n_examples} correct call(s) '
                                'with output; needs at least 2')
            if not placeholders and not answers:
                problems.append(f'{title}: no Answer cell')

    import json; Path(str(path)+'.metrics.json').write_text(json.dumps(METRICS, indent=0))
    if problems:
        print(f'{len(problems)} problem(s):')
        for p in problems:
            print('  -', p)
        return 1
    print(f'OK: {path}')
    return 0


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    sys.exit(main(Path(sys.argv[1]), Path(sys.argv[2])))
