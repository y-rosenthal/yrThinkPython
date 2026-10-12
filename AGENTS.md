# Rules for AI coding agents (yrThinkPython)

These rules are for every collaborator and every coding agent (Claude Code, Codex, Cursor, Copilot and others).
`CLAUDE.md` imports this file. Put new project rules here, not in `CLAUDE.md` or in one agent's private memory.

## The repository

- A fork of Allen Downey's *Think Python*, 3rd edition, for Prof. Rosenthal's course. Remotes: `origin` =
  y-rosenthal/yrThinkPython (branch `v3`), `upstream` = AllenDowney/ThinkPython.
- Every push to `v3` builds and publishes the website (`.github/workflows/deploy-book.yml`), which students use.
- `README.md` gives the layout. `author-guide/CONTENT-AUTHOR-GUIDE.qmd` is the guide for content authors.

## Where things are

- `yr/README.md`: the course's review pages (`yr/chapNN_review.ipynb`), their style rules and tools.
- `yr/tools/`: the review-page tools. `review.sh sync` writes outputs, pictures and values by running
  the code on the pinned Colab-like kernel; `review.sh check` verifies a page; `review.sh selftest`
  tests the tools; `review_format.py` defines the page format.
- `author-guide/CONTENT-AUTHOR-GUIDE.qmd`: the guide for content authors (Quarto book).
- `.claude/skills/NAME/SKILL.md`: step-by-step procedures, with their scripts next to them. Claude Code loads them
  as skills; with another agent, read the `SKILL.md` for the task and follow it. The main ones:
  - `yr-review-page`, `yr-review-questions`: write review pages and questions;
  - `sync-upstream`: take Allen Downey's changes; `upstream-diff`, `contribute-upstream`: compare with his book and
    report corrections to him;
  - `build-book`, `check-notebooks`, `notebook-conventions`, `make-blank`, `add-page`: build, check and edit the book;
  - `yrpublish`: publish the website.

## How to work

- Work on a topic branch (`git switch -c NAME v3`), never directly on `v3`. Merge into `v3` and push only when
  Prof. Rosenthal says so: the push publishes the website.
- Send corrections to Allen Downey's book as GitHub issues on AllenDowney/ThinkPython, not pull requests. He closes
  notebook pull requests, because his notebooks are made from another repository. Use the `contribute-upstream`
  skill, and get Prof. Rosenthal's approval before you open an issue.
- Before you push, run `python3 .claude/skills/check-notebooks/check_notebooks.py` (it must print `OK`) and the
  checks that the skill for the task names.

## Allen Downey's content and the fork's own content

- Take all of Downey's changes: he keeps the book up to date. Never lose anything of the fork when you merge them:
  - its edits to his pages (cells tagged `course`, corrections such as chapter 4 without `%autoreload`, its lines in
    `README.md`, `.gitignore` and `jb/`);
  - its own pages (`yr/`, `solutions/`, `author-guide/`, and any page added later);
  - its Colab links: every Colab link in `chapters/`, `blank/`, `jb/index.md` and `jb/blank.md` opens
    y-rosenthal/yrThinkPython.

  Follow the `sync-upstream` skill: `check_sync.py` must print `OK` before you publish a sync.
- Put new course material in `yr/` (the initials "yr" mark it). Do not remove or change Downey's exercises. Keep
  the book's chapter numbers.
- Do not add `%load_ext autoreload` or `%autoreload` to any notebook. Colab runs Python 3.12 or later with IPython
  7.34, whose autoreload imports the removed module `imp`, so the cell fails for students.

## Review pages (`yr/`)

- The style and format rules are in `yr/README.md`. Read it before you change a review page.
- Question numbers do not change during a semester, because homework is assigned by number. A question inserted
  between Questions 3 and 4 is Question 3b. Never reuse a deleted question's number, and never renumber
  automatically. Prof. Rosenthal renumbers only between semesters (`review_cells.py renumber`).
- Never type an output, a value or a picture by hand. `yr/tools/review.sh sync` writes them by running the code,
  and `yr/tools/review.sh check` must print `OK`.

## Documentation

- Write documentation, skills, comments and commit messages in ASD-STE100 Simplified Technical English: short
  sentences, active voice, the imperative for procedures, simple words with one meaning, the same term each time.
- When a design or a tool changes, update `yr/README.md`, the review skills (`.claude/skills/yr-review-page`,
  `yr-review-questions`) and `author-guide/CONTENT-AUTHOR-GUIDE.qmd` in the same change.

## Scripts

The shared rule "Scripts have --help" (below) applies. In this repository:

- `check_notebooks.py`, and so the deploy, fails on a script in `.claude/skills/`, `yr/` or `jb/` without a
  docstring or header comment and `--help`. A module that is only imported, a file that is only sourced, and
  Downey's own scripts go in its `NO_HELP` list. Do not change Downey's scripts.
- `review.sh COMMAND --help` also shows the options of that command.

<!-- begin shared rules: copied by agents-init from yrAiProjectTemplates/rules/AGENTS.md; edit there -->

## Scripts have --help

Every script you write or change (for a skill, a tool, or a one-off script that stays in the project) has `-h`
and `--help`. The help states the general purpose of the script, its usage line, and every option with its
default. With `-h` or `--help`, the script prints the help, exits with status 0, and does no work: it changes no
files and installs nothing.

- Python: the docstring at the top holds the help. At the start of `main`, before any work:
  `if '-h' in argv or '--help' in argv: print(__doc__); return 0` (or use `argparse` with a description).
- Bash: the header comment holds the help. Right after `set -euo pipefail`, before any setup:
  `case "${1:-}" in -h|--help) sed -n '2,/^[^#]/{/^#/s/^# \{0,1\}//p}' "$0"; exit 0 ;; esac`
- Other languages: the same behavior, in the usual way for that language.
- When you add, remove or change an option, update the help in the same change.
- Do not add `--help` to files that are only imported or sourced, or to third-party files that the project
  keeps unchanged (for example files from an upstream repository).

## Rules for every AI tool are in AGENTS.md

- Put a project's rules in its `AGENTS.md`, so that every collaborator's coding agent reads them. Most agents read
  `AGENTS.md` (Codex, Cursor, GitHub Copilot, Claude Code). Keep `CLAUDE.md` as one import line, `@AGENTS.md`, plus
  rules that apply only to Claude Code. Do not use a symlink for `CLAUDE.md` (Windows clones and Dropbox can break it).
- If a project's `AGENTS.md` does not have the block `<!-- begin shared rules -->`, tell the user and offer to run
  `agents-init.sh` in the project. `agents-init.sh --help` explains it.

<!-- end shared rules -->
