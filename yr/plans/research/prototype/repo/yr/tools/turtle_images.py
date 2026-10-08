"""Draw the turtle pictures in a review notebook by running the code, and embed them as PNGs.

Usage (through the wrapper, which sets up the venv):
    yr/tools/review.sh images yr/chap04_review.ipynb

In a markdown cell, a picture is written as an <img> tag with a `data-turtle` attribute:

    ```python
    make_turtle()
    triangle(80)
    ```
    <img data-turtle src="">

Each such tag is (re)filled with a PNG of what its code draws, as a data: URI, so the picture
is stored inside the notebook and shows up in Colab, Jupyter and on the website alike.

Which code is drawn: the nearest ```python block above the tag in the same cell; if there is
none, the last code cell above it (that is how an Answer shows the result of the question's
code cell). That code should start with make_turtle().

Before drawing, the tool runs, in a fresh namespace for every question (a question starts at a
'### ' heading): the notebook's setup cells (code cells tagged "setup"), then every ```python
block in the question's Answer cells, and then, in order, the question's own code cells as it
reaches them. So examples may call the function the student is asked to write (defined by the
suggested answer) or a function defined in a code cell above them.
"""
import base64
import contextlib
import io
import re
import sys
from pathlib import Path

import cairosvg
import nbformat as nbf

IMG = re.compile(r'<img\b[^>]*\bdata-turtle\b[^>]*>')
PY_BLOCK = re.compile(r'```python\n(.*?)```', re.S)
SCALE = 2  # render at 2x for sharp pictures on high-resolution screens


ANSWER_HEADING = re.compile(r'\s*#### Answer\s*$')


def is_answer(cell):
    return cell.cell_type == 'markdown' and re.match(r'\s*<details>\s*<summary>Answer</summary>', cell.source)


def split_answer(group):
    """(question cells, answer markdown cells) of a question in the new layout: the Answer is the
    '#### Answer' heading and the cells under it. Old layout: the <details> Answer cells."""
    for k, c in enumerate(group):
        if c.cell_type == 'markdown' and ANSWER_HEADING.match(c.source):
            return group[:k], [d for d in group[k + 1:] if d.cell_type == 'markdown']
    return [c for c in group if not is_answer(c)], [c for c in group if is_answer(c)]


def questions(cells):
    """Split cells into (setup_cells, [question_cells, ...]); a question starts at a '### ' heading."""
    setup = [c for c in cells if c.cell_type == 'code' and 'setup' in c.metadata.get('tags', [])]
    groups, current = [], None
    for c in cells:
        if c.cell_type == 'markdown' and c.source.lstrip().startswith('### '):
            current = []
            groups.append(current)
        elif c.cell_type == 'markdown' and c.source.lstrip().startswith(('# ', '## ')):
            current = None
        if current is not None:
            current.append(c)
    return setup, groups


def run(code, ns, label):
    """Execute code in ns, hiding its printed output; report (but survive) exceptions."""
    out = io.StringIO()
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            exec(compile(code, label, 'exec'), ns)
    except Exception as e:  # e.g. a question whose code draws a line and then fails
        return f'{type(e).__name__}: {e}'
    return None


def png_tag(svg):
    svg = svg.replace('<svg ', '<svg xmlns="http://www.w3.org/2000/svg" ', 1)
    width = int(re.search(r'width="(\d+)"', svg).group(1))
    png = cairosvg.svg2png(bytestring=svg.encode(), scale=SCALE)
    data = base64.b64encode(png).decode()
    return f'<img data-turtle alt="Turtle drawing" width="{width}" src="data:image/png;base64,{data}">'


def main(path):
    import os
    import tempfile
    path = path.resolve()
    os.chdir(tempfile.mkdtemp())  # the setup cell may download files: keep them out of the repo
    import jupyturtle  # found through PYTHONPATH (review.sh), so the download is not needed
    jupyturtle.TURTLE_DELAY = 0  # outside Jupyter nothing is displayed, so no need to wait

    nb = nbf.read(path, nbf.NO_CONVERT)
    setup, groups = questions(nb.cells)
    setup_code = '\n\n'.join(c.source for c in setup)
    count = 0
    for g in groups:
        title = g[0].source.lstrip().splitlines()[0]
        if not any(IMG.search(c.source) for c in g if c.cell_type == 'markdown'):
            continue
        ns = {}
        run(setup_code, ns, 'setup')
        question_cells, answer_md = split_answer(g)
        # new layout: the question's code is a ```python block in the question, not a code cell
        question_blocks = [b for c in question_cells if c.cell_type == 'markdown' for b in PY_BLOCK.findall(c.source)]
        for c in answer_md:
            if True:
                for block in PY_BLOCK.findall(c.source):
                    err = run(block, ns, 'answer')
                    if err:
                        print(f'!! {title}: answer code failed: {err}')
        last_code = None
        for c in g:
            if c.cell_type == 'code':
                if c.source.strip() != '# Your code here':
                    last_code = c.source
                    run(c.source, ns, 'question code')  # e.g. defines a function the examples use
                continue
            if c.cell_type != 'markdown' or not IMG.search(c.source):
                continue
            pieces, pos = [], 0
            for m in IMG.finditer(c.source):
                blocks = PY_BLOCK.findall(c.source[:m.start()])
                code = blocks[-1] if blocks else (last_code or (question_blocks[-1] if question_blocks else None))
                if code is None:
                    print(f'!! {title}: no code above a data-turtle image; left unchanged')
                    pieces.append(c.source[pos:m.end()])
                    pos = m.end()
                    continue
                if 'make_turtle(' not in code:
                    print(f'!! {title}: image code does not call make_turtle(); it continues the previous drawing')
                err = run(code, ns, 'image')
                if err:
                    print(f'   {title}: the drawn code raised {err} (picture shows the drawing up to that point)')
                svg = jupyturtle.get_turtle().get_SVG()
                pieces.append(c.source[pos:m.start()] + png_tag(svg))
                pos = m.end()
                count += 1
            pieces.append(c.source[pos:])
            c.source = ''.join(pieces)
    nbf.write(nb, path)
    print(f'{count} turtle picture(s) drawn in {path}')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(Path(sys.argv[1]))
