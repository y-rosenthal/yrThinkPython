#!/usr/bin/env python3
"""Regenerate blank/chapNN.ipynb ("fill in the blanks" versions) from chapters/chapNN.ipynb.

Every code cell is emptied except setup cells (download(), %xmode, diagram imports),
which students need to run as-is. Markdown is copied unchanged.

Usage:
  make_blank.py 03 07          # rewrite blank/chap03.ipynb and blank/chap07.ipynb
  make_blank.py all            # all chapters
  make_blank.py --diff 03      # only report what would change, write nothing
Stdlib only.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

# Code cells whose source starts with one of these are kept verbatim in the blank version.
KEEP_PREFIXES = (
    "from os.path import basename, exists",   # the download() setup cell
    "# This cell tells Jupyter",              # %xmode Verbose
    "from diagram import",
    "import diagram",
)


def blank_cell(cell):
    src = cell.get("source", [])
    text = "".join(src) if isinstance(src, list) else src
    new = dict(cell)
    if cell.get("cell_type") == "code":
        new["outputs"] = []
        new["execution_count"] = None
        if not text.startswith(KEEP_PREFIXES):
            new["source"] = []
    return new


def make_blank(num, write=True):
    src = ROOT / "chapters" / f"chap{num}.ipynb"
    dst = ROOT / "blank" / f"chap{num}.ipynb"
    nb = json.loads(src.read_text(encoding="utf-8"))
    nb["cells"] = [blank_cell(c) for c in nb["cells"]]
    out = json.dumps(nb, indent=1, ensure_ascii=False) + "\n"
    changed = (not dst.exists()) or dst.read_text(encoding="utf-8") != out
    kept = sum(1 for c in nb["cells"] if c["cell_type"] == "code" and c["source"])
    total = sum(1 for c in nb["cells"] if c["cell_type"] == "code")
    status = "unchanged" if not changed else ("would change" if not write else "written")
    print(f"blank/chap{num}.ipynb: {status}  ({total} code cells, {kept} kept as setup)")
    if changed and write:
        dst.write_text(out, encoding="utf-8")
    return changed


def main(argv):
    write = True
    if "--diff" in argv:
        write = False
        argv = [a for a in argv if a != "--diff"]
    if not argv:
        print(__doc__)
        return 2
    if argv == ["all"]:
        nums = sorted(p.stem[4:] for p in (ROOT / "chapters").glob("chap[01][0-9].ipynb"))
    else:
        nums = [a.zfill(2) for a in argv]
    any_changed = False
    for n in nums:
        any_changed |= make_blank(n, write)
    return 0 if (write or not any_changed) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
