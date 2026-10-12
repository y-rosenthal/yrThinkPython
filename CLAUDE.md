# Notes for Claude

## Where things are

- `yr/README.md`: the course's review pages (`yr/chapNN_review.ipynb`), their style rules and tools.
- `yr/tools/`: the review-page tools. `review.sh sync` writes outputs, pictures and values by running
  the code on the pinned Colab-like kernel; `review.sh check` verifies a page; `review.sh selftest`
  tests the tools; `review_format.py` defines the page format.
- `author-guide/CONTENT-AUTHOR-GUIDE.qmd`: the guide for content authors (Quarto book). Update it in the same
  change as `yr/README.md` and the review skills.
- `.claude/skills/`: skills for building, checking, publishing and syncing the book
  (for example `yrpublish`, `yr-review-page`, `yr-review-questions`).

## Scripts

Every script of the fork (in `.claude/skills/`, `yr/`, `jb/` or elsewhere) has `-h` and `--help`, which print
the purpose of the script and every option, then exit with status 0 and change nothing:

- Python: the docstring at the top says what the script does, its usage line and each option; at the start of
  `main` (before any work): `if '-h' in argv or '--help' in argv: print(__doc__); return 0`.
- Bash: the header comment says the same; right after `set -euo pipefail`, before any setup:
  `case "${1:-}" in -h|--help) sed -n '2,/^[^#]/{/^#/s/^# \{0,1\}//p}' "$0"; exit 0 ;; esac`.
- When you add or change an option, update the help in the same change.

`check_notebooks.py` (and so the deploy) fails on a script in `.claude/skills/`, `yr/` or `jb/` without a
docstring or `--help`. A module that is only imported, or a file that is only sourced, goes in its `NO_HELP` list.
Downey's own scripts are not changed (sync policy).
