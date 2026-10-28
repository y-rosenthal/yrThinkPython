# Think Python, 3rd edition (course fork)

This is a fork of [AllenDowney/ThinkPython](https://github.com/AllenDowney/ThinkPython),
adapted for use in a Python course. The online version of this fork is at
<https://y-rosenthal.github.io/yrThinkPython/>.

The original book is *Think Python: How to Think Like a Computer Scientist*, 3rd edition,
by Allen B. Downey. The original online version is at
<https://allendowney.github.io/ThinkPython/>, and the home page for the book is at
[Green Tea Press](http://thinkpython.com).
You can order print and electronic versions of *Think Python 3e* from
[Bookshop.org](https://bookshop.org/a/98697/9781098155438) and
[Amazon](https://www.amazon.com/_/dp/1098155432?smid=ATVPDKIKX0DER&_encoding=UTF8&tag=greenteapre01-20&linkCode=ur2&linkId=e2a529f94920295d27ec8a06e757dc7c&camp=1789&creative=9325).

Like the original, this work is licensed under a
[Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License](https://creativecommons.org/licenses/by-nc-sa/4.0/).

## Layout

- `chapters/` – the chapter notebooks (`chap00.ipynb` … `chap19.ipynb`). Edit these.
- `blank/` – "fill in the blanks" versions of each chapter with most code removed.
- `solutions/` – suggested solutions to the exercises (chapters 4 and 5 so far). Each file is
  a copy of the chapter notebook with the `# Solution goes here` cells filled in. The website
  shows these behind a collapsed "Suggested solution" dropdown under each exercise; the
  notebooks that Colab opens are unchanged.
- `yr/` – Prof. Rosenthal's course additions, kept apart from the book: a review page per
  chapter (`yr/chap04_review.ipynb`, shown on the site as "4b. Prof. Rosenthal's Review" right
  after chapter 4) with a concepts checklist and practice questions with collapsible answers, and
  for some chapters an additions page before it, with material that the chapter does not explain
  (`yr/chap07_additions.ipynb`, "7b. Prof. Rosenthal's Additions"; the review is then "7c.").
  See [yr/README.md](yr/README.md) for the layout, conventions and how to add one.
- `author-guide/` – the guide for content authors, a Quarto book (`CONTENT-AUTHOR-GUIDE.qmd`): how to
  work in this repository, and step by step how to write review-page questions. Build it with
  `cd author-guide && quarto render`.
- `AGENTS.md` – the rules for AI coding agents (Claude Code, Codex, Cursor, Copilot and others); `CLAUDE.md` imports
  it. `.claude/skills/` – step-by-step procedures (Claude Code skills) for building, checking, syncing and publishing.
- `jb/` – Jupyter Book configuration (`_config.yml`, `_toc.yml`), the landing pages
  (`index.md`, `blank.md`), `execute_notebooks.py` (runs the chapters at build time so the
  pages show outputs), `prep_notebooks.py` (applies display tags, strips `%%expect` magics,
  adds section labels and merges in the solutions) and `soln_overlay.json` / `update_overlay.py`
  (display tags and solutions taken from Downey's ThinkPythonSolutions notebooks).
- `thinkpython.py`, `diagram.py`, `structshape.py`, `words.txt`, `photos.zip` – helper
  modules and data files used by the notebooks.

## Publishing the website

The site is built by the GitHub Actions workflow in `.github/workflows/deploy-book.yml`.
On every push to the `v3` branch it copies the notebooks from `chapters/` (and `yr/`) into
`jb/`, runs the chapters so the pages show their outputs (`jb/execute_notebooks.py`), applies
the display tags of Downey's own site (`jb/soln_overlay.json`, via `jb/prep_notebooks.py`),
builds the HTML with Jupyter Book, and publishes the result to the `gh-pages` branch,
which GitHub Pages serves. The workflow can also be started by hand from the
repository's **Actions** tab.

To build locally:

```bash
.claude/skills/build-book/build_book.sh      # same steps as the workflow; output in jb/_build/html
```

The committed notebooks have no outputs and no display tags: Downey builds his site from his
separate ThinkPythonSolutions notebooks, which have both. `jb/update_overlay.py` copies his tags
(and his solutions, used only to run the exercise test cells) into `jb/soln_overlay.json`;
rerun it after merging upstream changes.

## Keeping up with the original

The `upstream` remote points at the original repository. The fork takes all of Downey's changes, and keeps its
own edits to his pages, its own pages (`yr/`, `solutions/`, `author-guide/`) and its own Colab links. Use the
`sync-upstream` skill of Claude Code, which follows this procedure on a topic branch:

```bash
git fetch upstream
git switch -c sync-upstream-YYYY-MM v3
git merge --no-ff --no-commit upstream/v3       # resolve conflicts: see .claude/skills/sync-upstream/SKILL.md
python3 .claude/skills/sync-upstream/fork_colab_links.py    # his Colab links -> the fork's
python3 .claude/skills/sync-upstream/check_sync.py          # proves that nothing was lost; must print OK
```

<!-- begin yrProject setup: written by yrProject.sh; "yrProject.sh update" replaces this block -->
*Set up by `yrProject.sh` (yrProject v0.5.2; parts: rules, yrIssues, subjexts). It installed the rules
for AI agents, the skills and the settings, and it updates them. Before you change them, read
`.yrProject/README.md`.*
<!-- end yrProject setup -->
