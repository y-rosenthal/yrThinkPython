#!/usr/bin/env python3
"""List the cells of a notebook with their index, type, tags and first line, so you can
find the right cell index for NotebookEdit or a targeted JSON edit.

Usage: nb_cells.py chapters/chap03.ipynb [--grep PATTERN] [--full INDEX]
"""
import json
import re
import sys


def main(argv):
    if not argv:
        print(__doc__); return 2
    path = argv[0]
    nb = json.load(open(path, encoding="utf-8"))
    cells = nb["cells"]
    if "--full" in argv:
        i = int(argv[argv.index("--full") + 1])
        c = cells[i]
        print(f"--- cell {i} ({c['cell_type']}, id={c.get('id')}, tags={c['metadata'].get('tags')})")
        print("".join(c["source"]))
        return 0
    pat = re.compile(argv[argv.index("--grep") + 1], re.I) if "--grep" in argv else None
    for i, c in enumerate(cells):
        src = "".join(c["source"])
        if pat and not pat.search(src):
            continue
        first = src.split("\n", 1)[0][:90]
        kind = {"markdown": "md  ", "code": "code"}.get(c["cell_type"], c["cell_type"])
        tags = c["metadata"].get("tags") or ""
        print(f"{i:4d} {kind} {tags!s:10.10} {first}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
