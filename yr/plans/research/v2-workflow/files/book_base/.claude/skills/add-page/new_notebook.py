#!/usr/bin/env python3
"""Create a new chapter-style notebook that matches the repo's conventions.

Usage: new_notebook.py chapters/chap20.ipynb "Chapter Title"
Copies the download()/setup cells from chapters/chap01.ipynb, then adds a title cell,
a placeholder section, and an exercise section with a '# Solution goes here' cell.
Stdlib only; never overwrites an existing file.
"""
import json
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def cid():
    return uuid.uuid4().hex[:8]


def md(text):
    lines = text.split("\n")
    return {"cell_type": "markdown", "id": cid(), "metadata": {},
            "source": [l + "\n" for l in lines[:-1]] + [lines[-1]]}


def code(text):
    lines = text.split("\n")
    return {"cell_type": "code", "id": cid(), "metadata": {"tags": []},
            "execution_count": None, "outputs": [],
            "source": [l + "\n" for l in lines[:-1]] + [lines[-1]]}


def main(argv):
    if len(argv) != 2:
        print(__doc__); return 2
    dst = ROOT / argv[0]
    title = argv[1]
    if dst.exists():
        print(f"refusing to overwrite {dst}"); return 1
    template = json.loads((ROOT / "chapters" / "chap01.ipynb").read_text(encoding="utf-8"))
    setup = []
    for c in template["cells"]:
        src = "".join(c["source"])
        if c["cell_type"] == "code" and (src.startswith("from os.path import basename, exists")
                                         or src.startswith("# This cell tells Jupyter")):
            c = dict(c); c["id"] = cid(); c["execution_count"] = None; c["outputs"] = []
            setup.append(c)
    # chap01 has an intro markdown cell before the download cell; keep the same shape.
    cells = [
        md(f"# {title}\n\nOne or two sentences saying what this chapter covers."),
        *setup[:1],
        md("## First section\n\nText goes here."),
        code("print('Hello')"),
        md("## Exercises"),
        *setup[1:],
        md("### Exercise\n\nDescribe the exercise here."),
        code("# Solution goes here"),
    ]
    nb = {"cells": cells, "metadata": template["metadata"], "nbformat": 4, "nbformat_minor": 5}
    dst.write_text(json.dumps(nb, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"created {dst.relative_to(ROOT)} with {len(cells)} cells")
    print("next: add it to jb/_toc.yml, add a Colab link in jb/index.md, and check the cp glob in .github/workflows/deploy-book.yml")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
