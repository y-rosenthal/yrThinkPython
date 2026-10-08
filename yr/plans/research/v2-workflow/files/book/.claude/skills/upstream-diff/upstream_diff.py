#!/usr/bin/env python3
"""Cell-level report of how this fork's notebooks differ from upstream (AllenDowney/ThinkPython v3).

Usage:
  upstream_diff.py                      # summary table, all chapter notebooks in chapters/ and blank/
  upstream_diff.py chapters/chap05.ipynb [...]   # full cell-by-cell diff for these notebooks
  upstream_diff.py --all                # full diff for every notebook that differs
  upstream_diff.py --ref origin/v3      # compare against another ref (default upstream/v3)

Cells are matched by cell id, so a cell that moved is not reported as removed+added.
Cells tagged "course" are course-specific additions/edits (see notebook-conventions);
they are counted separately from untagged changes, which are candidates to report upstream.
Stdlib + git only. Run `git fetch upstream` first for a current comparison.
"""
import difflib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
COURSE_TAG = "course"


def cells_of(text):
    nb = json.loads(text)
    out = []
    for i, c in enumerate(nb["cells"]):
        src = "".join(c["source"]) if isinstance(c["source"], list) else c["source"]
        out.append({"i": i, "id": c.get("id") or f"__noid{i}", "type": c["cell_type"],
                    "src": src, "tags": c.get("metadata", {}).get("tags", [])})
    return out


def upstream_text(ref, rel):
    try:
        return subprocess.check_output(["git", "-C", str(ROOT), "show", f"{ref}:{rel}"],
                                       text=True, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        return None


def compare(rel, ref):
    ours_text = (ROOT / rel).read_text(encoding="utf-8")
    theirs_text = upstream_text(ref, rel)
    ours = cells_of(ours_text)
    if theirs_text is None:
        return {"rel": rel, "new_file": True, "added": ours, "changed": [], "removed": []}
    theirs = cells_of(theirs_text)
    by_id = {c["id"]: c for c in theirs}
    our_ids = {c["id"] for c in ours}
    added = [c for c in ours if c["id"] not in by_id]
    changed = [(by_id[c["id"]], c) for c in ours if c["id"] in by_id and by_id[c["id"]]["src"] != c["src"]]
    removed = [c for c in theirs if c["id"] not in our_ids]
    return {"rel": rel, "new_file": False, "added": added, "changed": changed, "removed": removed}


def heading_for(cells, i):
    for j in range(i, -1, -1):
        c = cells[j]
        if c["type"] == "markdown" and c["src"].lstrip().startswith("#"):
            return c["src"].lstrip().split("\n", 1)[0].strip()
    return "(no heading)"


def is_course(c):
    return COURSE_TAG in c["tags"]


def print_full(r):
    rel = r["rel"]
    if r["new_file"]:
        print(f"=== {rel}: not in upstream ({len(r['added'])} cells)\n")
        return
    ours = cells_of((ROOT / rel).read_text(encoding="utf-8"))
    print(f"=== {rel}: {len(r['changed'])} changed, {len(r['added'])} added, {len(r['removed'])} removed\n")
    for old, new in r["changed"]:
        tag = " [course]" if is_course(new) else ""
        print(f"--- changed cell {new['i']} ({new['type']}){tag}  under: {heading_for(ours, new['i'])}")
        for line in difflib.unified_diff(old["src"].splitlines(), new["src"].splitlines(),
                                         "upstream", "fork", lineterm="", n=1):
            if line.startswith(("---", "+++")):
                continue
            print("   " + line)
        print()
    for c in r["added"]:
        tag = " [course]" if is_course(c) else " [UNTAGGED: add the 'course' tag if this is course material]"
        print(f"+++ added cell {c['i']} ({c['type']}){tag}  under: {heading_for(ours, c['i'])}")
        for line in c["src"].splitlines()[:8]:
            print("   + " + line)
        if c["src"].count("\n") > 8:
            print("   + ...")
        print()
    for c in r["removed"]:
        print(f"xxx removed upstream cell ({c['type']}) that was at upstream index {c['i']}")
        for line in c["src"].splitlines()[:4]:
            print("   - " + line)
        print()


def main(argv):
    ref = "upstream/v3"
    if "--ref" in argv:
        k = argv.index("--ref"); ref = argv[k + 1]; argv = argv[:k] + argv[k + 2:]
    full_all = "--all" in argv
    argv = [a for a in argv if a != "--all"]
    if argv:
        paths = [str(Path(a)) for a in argv]
    else:
        paths = sorted(str(p.relative_to(ROOT)) for d in ("chapters", "blank")
                       for p in (ROOT / d).glob("*.ipynb"))
    results = [compare(p, ref) for p in paths]
    differing = [r for r in results if r["new_file"] or r["added"] or r["changed"] or r["removed"]]

    if argv or full_all:
        for r in (differing if full_all else results):
            print_full(r)
        if not differing:
            print(f"no differences from {ref}")
        return 0

    print(f"fork vs {ref}, matched by cell id  (tagged '{COURSE_TAG}' = course material; untagged = candidate upstream corrections)\n")
    print(f"{'notebook':26} {'changed':>8} {'added':>6} {'removed':>8}   course-tagged   untagged")
    tot = [0, 0, 0]
    for r in differing:
        if r["new_file"]:
            print(f"{r['rel']:26} {'(new file)':>8}")
            continue
        edits = [n for _, n in r["changed"]] + r["added"]
        course = sum(1 for c in edits if is_course(c)); untagged = len(edits) - course
        print(f"{r['rel']:26} {len(r['changed']):8} {len(r['added']):6} {len(r['removed']):8}   {course:13}   {untagged}")
        tot[0] += len(r["changed"]); tot[1] += len(r["added"]); tot[2] += len(r["removed"])
    if not differing:
        print("  (no notebook differs)")
    else:
        print(f"{'total':26} {tot[0]:8} {tot[1]:6} {tot[2]:8}")
    print("\nfull diff: upstream_diff.py chapters/chapNN.ipynb   |   rich view: nbdiff-web (see SKILL.md)")
    other = subprocess.run(["git", "-C", str(ROOT), "diff", "--stat", f"{ref}...HEAD", "--", ".", ":!*.ipynb", ":!.claude"],
                           capture_output=True, text=True).stdout.strip()
    if other:
        print("\nnon-notebook files that differ from upstream:\n" + other)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
