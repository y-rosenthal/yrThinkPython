# Rules for AI coding agents (yrThinkPython)

<!-- begin yrProject setup: written by yrProject.sh; "yrProject.sh update" replaces this block -->
## Set up by yrProject.sh

`yrProject.sh` (yrProject v0.7.1; parts: rules, yrIssues, subjexts) set up this project. yrProject
(https://github.com/y-rosenthal/yrProject) is the templates and the tool that give a project one base for
AI-assisted work: rules for AI agents, skills, hooks, GitHub issues for work to do later, project docs. The tool
installed files here, and `yrProject.sh update` keeps them up to date. Every file that it installed starts with
a comment that names yrProject and its version, and says whether the file belongs to the tool or to the project.

- Start every reply with the version line `(yrProject v0.7.1 [latest])`, or `[latest vA.B.C]` if a newer
  version exists, or `[latest UNKNOWN]`. In Claude Code a hook gives you the exact line at each prompt; in another
  agent, run `bash .claude/skills/yrProject/scripts/yrProject-notice.sh version` once at the start of a session.
  In the first reply of a session, add one line with the facts of the setup (the type, the installed parts and the
  parts not installed: `bash .claude/skills/yrProject/scripts/yrProject-notice.sh facts`), unless a SessionStart
  message already showed them to the user; then answer.
- Before you change a file that the tool installed, read `.yrProject/README.md`. It lists the files, and tells who
  changes each one.
- Do not edit this block, the shared-rules block, the `yrProject` block in `.gitignore`, or the files in
  `.yrProject/`. `yrProject.sh update` writes them again.
- The user does not need to know the tool. To check, update, migrate or remove this setup, or to list or make
  yrProjects, follow the `yrProject` skill (`.claude/skills/yrProject/SKILL.md`).
- "Project" alone does not mean the yrProject setup. Unless the user says yrProject or it is obvious, ask.
<!-- end yrProject setup -->

These rules are for every collaborator and every coding agent (Claude Code, Codex, Cursor, Copilot and others).
`CLAUDE.md` imports this file. Put new project rules here, not in `CLAUDE.md` or in one agent's private memory.

## The repository

- A fork of Allen Downey's *Think Python*, 3rd edition, for Prof. Rosenthal's course. Remotes: `origin` =
  y-rosenthal/yrThinkPython (branch `v3`), `upstream` = AllenDowney/ThinkPython.
- Every push to `v3` builds and publishes the website (`.github/workflows/deploy-book.yml`), which students use.
- `README.md` gives the layout. `author-guide/` is the guide for content authors: a Quarto book that includes
  `README.md`, `yr/README.md` and the skills, plus the setup and the workflow for people (`author-guide/index.qmd`).

## Where things are

- `yr/README.md`: **the one place for the rules of the course's pages** (`yr/`): the pages of a chapter and their
  order, the additions pages, the review pages, the markdown pages, their layout, style rules, format rules, tools
  and procedures. Read it before you change anything in `yr/`.
- `yr/tools/`: the review-page tools. `review.sh sync` writes outputs, pictures and values by running
  the code on the pinned Colab-like kernel; `review.sh check` verifies a page; `review.sh selftest`
  tests the tools; `review_format.py` defines the page format.
- `.claude/skills/NAME/SKILL.md`: step-by-step procedures, with their scripts next to them. Claude Code loads them
  as skills; with another agent, read the `SKILL.md` for the task and follow it. A skill holds steps and points to
  the rules; it does not repeat them. The main ones:
  - `yr-additions-page`: write an additions page (material that Downey's chapter does not explain);
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

## Pending work

- Work to do later is the GitHub issues of this fork (y-rosenthal/yrThinkPython), not of AllenDowney/ThinkPython.
  Add, list, work on and close them with the `yrIssues` skill (the shared rule "Work to do later is GitHub issues"
  below).
- `PROJECT_BOARD.md` was retired on 2026-10-12: its Task N is issue #N. Its build notes are in
  `planning/upstream_build_notes.md`. Do not start another to-do file or task board.
- Corrections for Allen Downey's book are a different thing: they go to AllenDowney/ThinkPython with the
  `contribute-upstream` skill.

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

## The course's pages (`yr/`)

- Do not change Downey's chapters to add material. Put it in the course's pages in `yr/`: any number of pages after a
  chapter, lettered b, c, d, ... in the order of the TOC (`yr/chapNN_additions.ipynb`, `yr/chapNN_review.ipynb`,
  `yr/chapNN_more_review.ipynb`), or a markdown page (`yr/NAME.md`).
- `yr/README.md` holds every rule for these pages: read the sections for your task before you change a page, and
  follow them. Two of its rules are easy to break and costly: question numbers stay fixed during a semester
  ("Question numbers between semesters"), and nothing that `review.sh sync` writes is typed by hand ("Adding a
  question"). `review.sh check` and `check_notebooks.py` must print `OK`.

## Documentation

- Write documentation, skills, comments and commit messages in ASD-STE100 Simplified Technical English: short
  sentences, active voice, the imperative for procedures, simple words with one meaning, the same term each time.
- **One place for each rule.** A rule for the course's pages lives in `yr/README.md`; a rule for the chapter
  notebooks in the `notebook-conventions` skill; what a check does in the docstring of its script. Every other
  file (a skill, `AGENTS.md`, `README.md`) points to the section instead of repeating the rule. When a design or
  a tool changes, change the rule in its one place, and a skill only if its steps change. The author guide
  (`author-guide/`) includes these files, so it needs no change.

## Scripts

The shared rule "Scripts have --help" (below) applies. In this repository:

- `check_notebooks.py`, and so the deploy, fails on a script in `.claude/skills/`, `yr/` or `jb/` without a
  docstring or header comment and `--help`. A module that is only imported, a file that is only sourced, and
  Downey's own scripts go in its `NO_HELP` list. Do not change Downey's scripts.
- `review.sh COMMAND --help` also shows the options of that command.

<!-- begin shared rules: copied by yrProject from yrProject/rules/AGENTS.md; edit there -->

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
- If a project's `AGENTS.md` does not have the block `<!-- begin shared rules -->`, tell the user and offer to set
  it up as a yrProject with `yrProject.sh update`. `yrProject.sh status` shows the project's state,
  `yrProject.sh check` whether it is set up correctly, `yrProject.sh remove` takes the setup out again, and
  `yrProject.sh --help` explains them. An agent has no
  terminal to answer `update`'s question in: run `yrProject.sh update --dry-run`, show the user the plan, and run
  `yrProject.sh update -y` only after the user approves it. In a yrProject, the `yrProject` skill does all this.

## "Project" does not mean yrProject

- A yrProject is a project that `yrProject.sh` set up: its shared rules, skills and hooks, and its record in
  `.yrProject/`. Do not assume that the word "project" means a yrProject, or its yrProject setup. Unless the user
  says yrProject (or the yrProject setup, the tool, its shared rules or its skills), or it is otherwise obvious,
  ask what they mean before you act. For example, "update the project" or "make a new project" may mean the code,
  the book, or something else.

## Work to do later is GitHub issues

- Record work to do later as GitHub issues in the project's own repository, not in a to-do file, a task board or a
  TODO document. Call them "issues", as GitHub does. If the project has the `yrIssues` skill
  (`.claude/skills/yrIssues/`), use it: a SessionStart hook shows the user how many issues are open, and the issues
  that it creates get the label `yrIssue`. (Projects set up before yrProject v0.5.0 have the `pending-work` skill
  instead; `yrProject.sh update` replaces it.)
- If a project keeps such a list in a file, tell the user and offer to move it into issues.
- Things that expire or renew on a date (API keys, access tokens, domains, certificates, subscriptions, periodic
  checks) go in `_yrRenewals/renewals.yml` if the project has the `yrRenewals` skill
  (`.claude/skills/yrRenewals/`): a daily GitHub workflow opens a reminder issue before each date, and closing
  it is the acknowledgement. Never write a key, a token or a password there, or in an issue.
- `_yrIssues/issues.md` (the saved copy of the open issues) and `_yrIssues/queue.md` (issues written while GitHub
  could not be reached) are written by the yrIssues skill, and git ignores them (yrProject v0.6.0 and later). Do
  not edit, commit or restore them. In a project from before v0.6.0, a staged deletion of `issues.md` is the
  migration (`git rm --cached`: the file stays on disk), not an accident: leave it, and commit it with a plain
  `git commit`, not one limited to paths. A path-limited commit rebuilds those paths from the working tree, where
  the ignored file still exists, and silently drops the untracking.

<!-- end shared rules -->
