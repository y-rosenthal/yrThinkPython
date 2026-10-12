#!/usr/bin/env python3
"""Static checks for the Think Python notebooks. Stdlib only, no nbformat needed.

Usage: check_notebooks.py [notebook.ipynb ...]
Default: every chap*.ipynb in chapters/, blank/ and solutions/ and every yr/*.ipynb, plus TOC / Colab-link / workflow
consistency, a check that each solutions/chapNN.ipynb matches its chapter, a check of the yr/ page titles and their
order in the TOC (chapter, then NNb. Additions, then NNb or NNc. Review), and a check that every script of the fork
(.claude/skills/, yr/, jb/) has a docstring or header comment and a -h/--help option that prints it.
(chapters/jupyter_intro.ipynb is skipped by default: it is an older nbformat 4.4 file that
keeps its outputs on purpose and is only shipped in the zip, not in the book.)
Exit status 1 if any problem is found.
"""
import ast
import json
import re
import sys
from glob import glob
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "yr" / "tools"))
import review_format  # noqa: E402  (stdlib only)
sys.path.insert(0, str(ROOT / ".claude" / "skills" / "sync-upstream"))
import fork_colab_links  # noqa: E402  (stdlib only)
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
    # converted review pages (yr/, #### Answer headings) store the outputs of their run cells, written by
    # `review.sh sync`; nothing else may store output, and the sync stamp must match (no hand edits)
    review = path.parent.name == "yr" and review_format.page_format(nb) == "v3"
    run_cells = set()
    if review:
        run_cells = {i for q in review_format.parse_page(nb) for i in q["run_cells"]}
        for p in review_format.stamp_problems(nb):
            problems.append(f"{path}: {p}")
        for i, c in enumerate(nb.get("cells", [])):
            if c.get("cell_type") == "markdown":
                for p in review_format.marker_problems(review_format.source(c)):
                    problem(path, i, p)
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
            if c.get("outputs") and i not in run_cells:
                problem(path, i, "has stored outputs (notebooks are committed without outputs"
                                 + ("; on review pages only run cells, written by review.sh sync)" if review else ")"))
            ec = c.get("execution_count")
            if review and ec is not None:
                problem(path, i, "execution_count is stored (review pages: run review.sh sync)")
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
        if f.startswith("yr/"):
            if not (ROOT / f"{f}.ipynb").exists():
                problems.append(f"jb/_toc.yml: entry '{f}' has no {f}.ipynb")
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

    changed, colab_problems = fork_colab_links.run(check=True)
    for rel in changed:
        problems.append(f"{rel}: has Colab links to AllenDowney/ThinkPython; run "
                        ".claude/skills/sync-upstream/fork_colab_links.py")
    problems.extend(colab_problems)

    for p in sorted((ROOT / "yr").glob("*.ipynb")):
        if f"yr/{p.stem}" not in toc_files:
            problems.append(f"jb/_toc.yml: yr/{p.name} is not listed in the TOC")

    wf = (ROOT / ".github" / "workflows" / "deploy-book.yml").read_text()
    if "cp yr/*.ipynb jb/yr/" not in wf:
        problems.append("deploy-book.yml: does not copy yr/*.ipynb into jb/yr/")
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


YR_PAGE = re.compile(r"chap(\d\d)_(additions|review)")


def check_yr_pages():
    """The yr/ pages of a chapter: "NNb. Prof. Rosenthal's Additions" (yr/chapNN_additions.ipynb), if there is one,
    and then "NNb. Prof. Rosenthal's Review" (yr/chapNN_review.ipynb), which is "NNc." when the chapter has an
    additions page. The TOC lists them in that order, right after the chapter (yr/README.md)."""
    toc = re.findall(r"^\s*-\s*file:\s*(\S+)", (ROOT / "jb" / "_toc.yml").read_text(), re.M)
    for p in sorted((ROOT / "yr").glob("*.ipynb")):
        m = YR_PAGE.fullmatch(p.stem)
        if not m:
            problems.append(f"yr/{p.name}: a yr/ page is chapNN_additions.ipynb or chapNN_review.ipynb")
            continue
        nn, kind = m.groups()
        try:
            first = review_format.source(json.loads(p.read_text(encoding="utf-8"))["cells"][0])
        except (json.JSONDecodeError, IndexError, KeyError):
            continue  # reported by check_notebook
        if kind == "additions":
            want = f"# {int(nn)}b. Prof. Rosenthal's Additions"
            order = [f"chap{nn}", f"yr/chap{nn}_additions"]
            if (ROOT / "yr" / f"chap{nn}_review.ipynb").exists():
                order.append(f"yr/chap{nn}_review")
        else:
            want = f"# {int(nn)}{review_format.review_letter(p)}. Prof. Rosenthal's Review"
            order = None
        if not first.startswith(want + "\n"):
            problems.append(f"yr/{p.name}: the title must be {want!r}"
                            + (" (run yr/tools/review.sh sync)" if kind == "review" else ""))
        if order and all(f in toc for f in order):
            at = toc.index(order[0])
            if toc[at:at + len(order)] != order:
                problems.append(f"jb/_toc.yml: list {', '.join(order)} in this order, one after the other")


# Scripts that are not run from the command line, and Downey's own scripts (kept as his: sync-upstream)
NO_HELP = {
    "yr/tools/review_format.py": "a module, imported by the review tools",
    ".claude/skills/build-book/ensure_venv.sh": "sourced by other scripts",
    "jb/prep_notebooks.py": "Downey's file",
    "jb/build.sh": "Downey's file",
}


def check_script_help():
    """Every script of the fork says what it does and takes -h/--help (AGENTS.md, "Scripts")."""
    scripts = [p for pat in (".claude/skills/**/*.py", ".claude/skills/**/*.sh", "yr/**/*.py", "yr/**/*.sh",
                             "jb/*.py", "jb/*.sh") for p in ROOT.glob(pat)]
    for p in sorted(set(scripts)):
        rel = p.relative_to(ROOT).as_posix()
        if rel in NO_HELP:
            continue
        text = p.read_text(encoding="utf-8")
        if p.suffix == ".py":
            if not ast.get_docstring(ast.parse(text)):
                problems.append(f"{rel}: no docstring (say what the script does and list its options)")
            if "'--help'" not in text and '"--help"' not in text and "argparse" not in text:
                problems.append(f"{rel}: no -h/--help option (print the docstring; see AGENTS.md)")
        elif "--help)" not in text:
            problems.append(f"{rel}: no -h/--help option (print the header comment; see AGENTS.md)")


def main(argv):
    if "-h" in argv or "--help" in argv:
        print(__doc__)
        return 0
    paths = [Path(a) for a in argv] or sorted(
        [*map(Path, glob(str(ROOT / "chapters" / "chap*.ipynb"))),
         *map(Path, glob(str(ROOT / "blank" / "chap*.ipynb"))),
         *map(Path, glob(str(ROOT / "solutions" / "chap*.ipynb"))),
         *map(Path, glob(str(ROOT / "yr" / "*.ipynb")))]
    )
    for p in paths:
        check_notebook(p)
    if not argv:
        check_toc_and_links()
        check_solutions()
        check_yr_pages()
        check_script_help()
    if problems:
        print(f"{len(problems)} problem(s):")
        for p in problems:
            print("  -", p)
        return 1
    print(f"OK: {len(paths)} notebook(s) checked" + ("" if argv else ", TOC, Colab links and script help consistent"))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
