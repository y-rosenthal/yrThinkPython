"""Prototype: convert a review notebook from the <details> layout to the 'Answer heading section' layout.

  python convert.py OLD.ipynb NEW.ipynb [--wrap all|errors]

New layout, for every question:
  - question markdown: the heading, the text, and the question's code as ```python blocks (no runnable cell),
    except definition-only cells ("Run this cell to define f"), which stay code cells; '# Your code here' stays.
  - '#### Answer' markdown heading, saved COLLAPSED for Colab (metadata.colab.collapsed_sections + cell
    metadata.id) and JupyterLab (cell metadata jp-MarkdownHeadingCollapsed), followed by
      * the old Answer body (expected output in ```text blocks, explanation, turtle PNG), as markdown,
      * one code cell per question code block, that runs it (via run_code(...) when it raises),
        each preceded by its part label for multi-part questions.
"""
import ast
import re
import secrets
import sys

import nbformat as nbf

DETAILS = re.compile(r'\s*<details>\s*<summary>Answer</summary>\s*(.*?)\s*</details>\s*$', re.S)
RUN_CODE = re.compile(r'\s*run_code\("""\n(.*?)\n?"""\)\s*$', re.S)
PART = re.compile(r'\s*\*\*Part \w+\*\*\s*$')
PLACEHOLDER = '# Your code here'
CREDIT = '*Summary and questions by'

NEW_RUN_CODE = '''def run_code(code):
    """Run the Python code in the string code, exactly as if it were in a cell of its own.

    The answers run the question's code with run_code when its result is an error: the
    error is shown, but it does not stop "Run all", so the rest of the page still runs.
    """
    get_ipython().run_cell(code)'''

INTRO_OLD = re.compile(r'Some questions show their code inside `run_code.*?prediction\.', re.S)
INTRO_NEW = ('Each question\'s Answer is hidden under a collapsed **Answer** heading: click the arrow next to it '
             '(or the "cells hidden" button) to show it. The Answer ends with a code cell that runs the question\'s '
             'code, so you can see its real output. When that output is an error, the code is run with '
             '`run_code("""...""")` (defined in the next cell), which shows the error without stopping "Run all".')


def is_definition_only(code):
    """True for a cell that only defines things (def/class/import/assignments): it displays nothing."""
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return False
    return all(isinstance(s, (ast.FunctionDef, ast.ClassDef, ast.Import, ast.ImportFrom, ast.Assign))
               for s in tree.body)


def main(src, dst, wrap='errors'):
    nb = nbf.read(src, as_version=4)
    used = {c.get('id') for c in nb.cells}

    def fresh():
        while True:
            i = secrets.token_hex(4)
            if i not in used:
                used.add(i)
                return i

    def md(s, **meta):
        c = nbf.v4.new_markdown_cell(s.strip('\n'))
        c.id = meta.pop('id', None) or fresh()
        c.metadata.update(meta)
        return c

    def code(s, tags=()):
        c = nbf.v4.new_code_cell(s.strip('\n'))
        c.id = fresh()
        c.metadata['tags'] = list(tags)
        return c

    out, collapsed = [], []
    i, cells = 0, nb.cells
    while i < len(cells):
        c = cells[i]
        if c.cell_type == 'markdown' and c.source.lstrip().startswith('# ') and i == 0:
            c.source = c.source.replace('Each question has a suggested answer: click **Answer** to reveal it',
                                        'Each question has a suggested answer: click the arrow next to **Answer** to reveal it')
        if c.cell_type == 'markdown' and c.source.lstrip().startswith('## Questions'):
            c.source = INTRO_OLD.sub(INTRO_NEW, c.source)
        if c.cell_type == 'code' and 'setup' in c.metadata.get('tags', []):
            if 'def run_code(' in c.source:
                c.source = re.sub(r'def run_code\(code\):.*', NEW_RUN_CODE, c.source, flags=re.S)
            else:
                c.source = c.source.rstrip() + '\n\n' + NEW_RUN_CODE
        if c.cell_type == 'markdown' and c.source.lstrip().startswith(CREDIT):
            # A collapsed heading hides every cell up to the next heading of the same or a higher level,
            # so without a heading of its own the credit line would be hidden inside the last Answer.
            c.source = '## Credits\n\n' + c.source
        if not (c.cell_type == 'markdown' and c.source.lstrip().startswith('### ')):
            out.append(c)
            i += 1
            continue
        # one question: cells up to the next heading of level <= 3
        j = i + 1
        while j < len(cells) and not (cells[j].cell_type == 'markdown' and (
                re.match(r'\s*#{1,3} ', cells[j].source) or cells[j].source.lstrip().startswith(CREDIT))):
            j += 1
        group = cells[i:j]
        pending, runs, label = [], [], None
        answer = None

        def flush():
            if pending:
                first = next((p for p in pending if isinstance(p, nbf.NotebookNode)), None)
                txt = '\n\n'.join(p.source if isinstance(p, nbf.NotebookNode) else p for p in pending)
                out.append(md(txt, id=first.id if first is not None else None))
                pending.clear()

        for g in group:
            if g.cell_type == 'markdown' and DETAILS.match(g.source):
                answer = g
                continue
            if g.cell_type == 'markdown':
                s = g.source
                s = re.sub(r'then run (it|the cells?) to check', 'then open the Answer to check', s)
                s = s.replace('Each cell has one mistake.', 'Each part has one mistake.')
                s = s.replace('Predict the error for each, then', 'Predict the error for each, then')
                g.source = s
                label = s.strip() if PART.match(s) else (s.strip().splitlines()[-1] if PART.match(s.strip().splitlines()[-1]) else None)
                pending.append(g)
                continue
            src = g.source.strip()
            if src == PLACEHOLDER:
                flush()
                out.append(g)
                continue
            m = RUN_CODE.match(g.source)
            body = m.group(1) if m else src
            raises = bool(m) or 'raises-exception' in g.metadata.get('tags', [])
            if not m and not raises and is_definition_only(src):
                flush()  # "Run this cell to define f": stays a runnable cell (displays nothing)
                g.metadata['tags'] = [t for t in g.metadata.get('tags', [])]
                out.append(g)
                continue
            pending.append(f'```python\n{body}\n```')
            runs.append((label, body, raises))
            label = None
        flush()
        if answer is not None:
            head = md('#### Answer', id=answer.id, **{'jp-MarkdownHeadingCollapsed': True})
            head.metadata['id'] = head.id          # Colab-style cell id (Colab writes metadata.id == id)
            collapsed.append(head.id)
            out.append(head)
            out.append(md(DETAILS.match(answer.source).group(1)))
            # The run cell holds exactly the question's code (no added comment line: it would shift
            # line numbers in tracebacks and doctest reports).
            for lab, body, raises in runs:
                out.append(code(f'run_code("""\n{body}\n""")' if raises or wrap == 'all' else body))
        i = j

    nb.cells = out
    nb.metadata.setdefault('colab', {})['collapsed_sections'] = collapsed
    nbf.validate(nb)
    nbf.write(nb, dst)
    print(f'wrote {dst}: {len(out)} cells, {len(collapsed)} collapsed Answer sections')


if __name__ == '__main__':
    a = sys.argv[1:]
    wrap = 'errors'
    if '--wrap' in a:
        k = a.index('--wrap'); wrap = a[k + 1]; del a[k:k + 2]
    main(a[0], a[1], wrap)
