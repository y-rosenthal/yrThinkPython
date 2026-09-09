#!/usr/bin/env python3
"""Draft an upstream issue for a correction made in a chapter notebook.

Usage:
  issue_body.py chapters/chap18.ipynb              # every cell that differs from upstream/v3
  issue_body.py chapters/chap18.ipynb --cell 57    # one cell (index from nb_cells.py)

For each changed cell it prints: the section heading, a link to that section on the
upstream site (https://allendowney.github.io/ThinkPython/chapNN.html#anchor), the upstream
text, and the fork's text. Paste the result into the issue body. Stdlib + git only.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SITE = "https://allendowney.github.io/ThinkPython"


def load(path_text):
    nb = json.loads(path_text)
    return [(c["cell_type"], "".join(c["source"]), c.get("id"), c.get("metadata", {}).get("tags", []))
            for c in nb["cells"]]


def anchor(heading):
    # Sphinx/MyST slug: lowercase, non-alphanumerics -> hyphen, collapse, strip
    s = re.sub(r"[^0-9a-z]+", "-", heading.lower()).strip("-")
    return s


def section_for(cells, i):
    for j in range(i, -1, -1):
        kind, src, _, _ = cells[j]
        if kind == "markdown" and src.lstrip().startswith("#"):
            line = src.lstrip().split("\n", 1)[0]
            return line.lstrip("#").strip()
    return None


def main(argv):
    if not argv:
        print(__doc__); return 2
    path = Path(argv[0])
    only = int(argv[argv.index("--cell") + 1]) if "--cell" in argv else None
    rel = path.relative_to(ROOT) if path.is_absolute() else path
    chap = path.stem
    ours = load(path.read_text(encoding="utf-8"))
    try:
        theirs_text = subprocess.check_output(
            ["git", "-C", str(ROOT), "show", f"upstream/v3:{rel.as_posix()}"], text=True)
    except subprocess.CalledProcessError:
        print("could not read upstream/v3 version; run `git fetch upstream` first"); return 1
    theirs = load(theirs_text)
    by_id = {cid: (k, s) for k, s, cid, _ in theirs if cid}

    changed = []
    skipped = 0
    for i, (kind, src, cid, tags) in enumerate(ours):
        if only is not None and i != only:
            continue
        if "course" in tags:
            skipped += 1
            continue
        up = by_id.get(cid)
        if up is None:
            changed.append((i, kind, None, src))
        elif up[1] != src:
            changed.append((i, kind, up[1], src))
    if not changed:
        print(f"{rel}: no cells differ from upstream/v3" + (f" (cell {only})" if only is not None else "")
              + (f"; {skipped} course-tagged cell(s) ignored" if skipped else ""))
        return 0
    if skipped:
        print(f"(ignored {skipped} cell(s) tagged 'course')\n", file=sys.stderr)

    their_index = {cid: j for j, (_, _, cid, _) in enumerate(theirs) if cid}
    print(f"Notebook: `{rel}` (fork), compared with `upstream/v3`\n")
    for i, kind, up, src in changed:
        cid = ours[i][2]
        heading = section_for(theirs, their_index[cid]) if cid in their_index else section_for(ours, i)
        link = f"{SITE}/{chap}.html#{anchor(heading)}" if heading else f"{SITE}/{chap}.html"
        print(f"### Cell {i} ({kind}) in section “{heading}”\n")
        print(f"Location: {link}\n")
        if up is None:
            print("This cell does not exist upstream (new in the fork).\n")
        else:
            print("Current text:\n")
            print("```" + ("python" if kind == "code" else ""))
            print(up.rstrip())
            print("```\n")
        print("Suggested text:\n")
        print("```" + ("python" if kind == "code" else ""))
        print(src.rstrip())
        print("```\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
