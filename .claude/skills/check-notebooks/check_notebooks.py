#!/usr/bin/env python3
"""Static checks for the Think Python notebooks. Stdlib only, no nbformat needed.

Usage: check_notebooks.py [notebook.ipynb ...]
Default: every chap*.ipynb in chapters/, blank/ and solutions/, plus TOC / Colab-link / workflow
consistency and a check that each solutions/chapNN.ipynb matches its chapter.
(chapters/jupyter_intro.ipynb is skipped by default: it is an older nbformat 4.4 file that
keeps its outputs on purpose and is only shipped in the zip, not in the book.)
Exit status 1 if any problem is found.
"""
import json
import re
import sys
from glob import glob
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
KNOWN_MAGICS = {"%%expect", "%%add_method_to", "%%expect_error"}
SOLUTION_MARK = "# Solution goes here"

problems = []


def problem(path, idx, msg):
    problems.append(f"{path}  cell {idx}: {msg}")


def check_notebook(path: Path):
    try:
        nb = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        problems.append(f"{path}: invalid JSON ({e})")
        return
    if nb.get("nbformat") != 4:
        problems.append(f"{path}: nbformat is {nb.get('nbformat')}, expected 4")
    has_ids = nb.get("nbformat_minor", 0) >= 5
    ids = set()
    for i, c in enumerate(nb.get("cells", [])):
        src = c.get("source", "")
        if isinstance(src, list):
            src = "".join(src)
        elif not isinstance(src, str):
            problem(path, i, "source is neither list nor string")
            continue
        cid = c.get("id")
        if not cid:
            if has_ids:
                problem(path, i, "missing cell id")
        elif cid in ids:
            problem(path, i, f"duplicate cell id {cid}")
        ids.add(cid)
        if c.get("cell_type") == "code":
            if c.get("outputs"):
                problem(path, i, "has stored outputs (notebooks are committed without outputs)")
            ec = c.get("execution_count")
            if ec is not None and not isinstance(ec, int):
                problem(path, i, f"execution_count is {ec!r}")
            if "outputs" not in c:
                problem(path, i, "code cell missing 'outputs' key")
            first = src.split("\n", 1)[0].strip()
            if first.startswith("%%"):
                magic = first.split()[0]
                if magic not in KNOWN_MAGICS:
                    problem(path, i, f"unknown cell magic {magic}")
                elif magic == "%%expect" and len(first.split()) != 2:
                    problem(path, i, f"%%expect needs exactly one exception name: {first!r}")
                elif magic == "%%add_method_to" and len(first.split()) != 2:
                    problem(path, i, f"%%add_method_to needs a class name: {first!r}")
            if src.startswith("# Solution") and src.strip() != SOLUTION_MARK:
                problem(path, i, f"solution cell should be exactly {SOLUTION_MARK!r}; "
                                 "prep_notebooks.py blanks any cell starting with '# Solution'")
        elif c.get("cell_type") == "markdown":
            if "outputs" in c or "execution_count" in c:
                problem(path, i, "markdown cell has code-cell keys")
        else:
            problem(path, i, f"unexpected cell_type {c.get('cell_type')!r}")


def check_toc_and_links():
    toc = (ROOT / "jb" / "_toc.yml").read_text()
    toc_files = set(re.findall(r"^\s*-\s*file:\s*(\S+)", toc, re.M))
    chapter_files = {p.stem for p in (ROOT / "chapters").glob("chap[01][0-9].ipynb")}
    for f in sorted(chapter_files - toc_files):
        problems.append(f"jb/_toc.yml: chapters/{f}.ipynb is not listed in the TOC")
    for f in sorted(toc_files):
        if f in ("index", "blank"):
            continue
        if not (ROOT / "chapters" / f"{f}.ipynb").exists() and not (ROOT / "jb" / f"{f}.md").exists():
            problems.append(f"jb/_toc.yml: entry '{f}' has no chapters/{f}.ipynb or jb/{f}.md")

    for page in ("index.md", "blank.md"):
        text = (ROOT / "jb" / page).read_text()
        for m in re.finditer(r"colab\.research\.google\.com/github/([^/]+/[^/]+)/blob/([^/]+)/([^)\s]+)", text):
            repo, branch, rel = m.groups()
            if repo != "y-rosenthal/yrThinkPython" or branch != "v3":
                problems.append(f"jb/{page}: Colab link points at {repo}@{branch}, not the fork's v3: {rel}")
            if not (ROOT / rel).exists():
                problems.append(f"jb/{page}: Colab link target does not exist: {rel}")

    wf = (ROOT / ".github" / "workflows" / "deploy-book.yml").read_text()
    m = re.search(r"cp\s+(\S+)\s+jb/", wf)
    if m:
        import fnmatch
        pattern = m.group(1)
        for f in sorted(toc_files - {"index", "blank"}):
            src = f"chapters/{f}.ipynb"
            if (ROOT / src).exists() and not fnmatch.fnmatch(src, pattern):
                problems.append(f"deploy-book.yml: '{src}' is in the TOC but not matched by the copy glob {pattern!r}")


def check_solutions():
    """solutions/chapNN.ipynb must be a copy of chapters/chapNN.ipynb whose '# Solution goes here'
    cells contain the solution code. prep_notebooks.py matches them by cell id, so a solution
    cell whose id is not a placeholder in the chapter would silently never appear on the site."""
    for soln_path in sorted((ROOT / "solutions").glob("chap*.ipynb")):
        chap_path = ROOT / "chapters" / soln_path.name
        if not chap_path.exists():
            problems.append(f"{soln_path}: no matching chapters/{soln_path.name}")
            continue
        try:
            chap = json.loads(chap_path.read_text(encoding="utf-8"))
            soln = json.loads(soln_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue  # reported by check_notebook
        def src(c):
            s = c.get("source", "")
            return "".join(s) if isinstance(s, list) else s
        placeholders = {c.get("id") for c in chap["cells"]
                        if c.get("cell_type") == "code" and src(c).startswith("# Solution")}
        chap_by_id = {c.get("id"): c for c in chap["cells"]}
        filled = set()
        for i, c in enumerate(soln["cells"]):
            cid = c.get("id")
            if c.get("cell_type") != "code" or cid in placeholders:
                if cid in placeholders and src(c).strip() and not src(c).startswith("# Solution"):
                    filled.add(cid)
                continue
            other = chap_by_id.get(cid)
            if other is None:
                problem(soln_path, i, "code cell id not found in the chapter (only '# Solution goes "
                                      "here' cells may be filled in; do not add cells here)")
            elif src(other) != src(c):
                problem(soln_path, i, "code cell differs from the chapter but is not a solution "
                                      "placeholder; the site ignores it, so edit chapters/ instead")
        missing = placeholders - filled
        if missing:
            print(f"note: {soln_path.relative_to(ROOT)}: {len(missing)} placeholder cell(s) left "
                  f"empty (rendered as blank cells on the site): {', '.join(sorted(missing))}")


def main(argv):
    paths = [Path(a) for a in argv] or sorted(
        [*map(Path, glob(str(ROOT / "chapters" / "chap*.ipynb"))),
         *map(Path, glob(str(ROOT / "blank" / "chap*.ipynb"))),
         *map(Path, glob(str(ROOT / "solutions" / "chap*.ipynb")))]
    )
    for p in paths:
        check_notebook(p)
    if not argv:
        check_toc_and_links()
        check_solutions()
    if problems:
        print(f"{len(problems)} problem(s):")
        for p in problems:
            print("  -", p)
        return 1
    print(f"OK: {len(paths)} notebook(s) checked" + ("" if argv else ", TOC and Colab links consistent"))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
