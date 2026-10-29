---
name: sync-upstream
description: Pull in changes from the original Think Python repo (AllenDowney/ThinkPython, remote "upstream", branch v3) and resolve notebook merge conflicts safely, keeping every fork edit, the fork's own pages and the fork's Colab links. Use when asked to sync, merge, update from, or compare with upstream/Allen Downey's version.
user-invocable: true
argument-hint: [status | merge]
---

# Sync with upstream

Remotes: `origin` = y-rosenthal/yrThinkPython (this fork, branch `v3`); `upstream` =
AllenDowney/ThinkPython. Downey keeps the book up to date; the fork takes all of his changes.

## The policy (Prof. Rosenthal, 2026-10-11)

1. **Take all of Downey's content**: chapter text and code, blank notebooks, support files, zip files.
2. **Keep every fork change to his pages**: cells the fork added or changed in `chapters/` (tagged `course`, or
   corrections such as chapter 4's `%autoreload` fix), and the fork's lines in `README.md`, `.gitignore`, `jb/`.
3. **Keep the fork's own pages untouched**: `yr/` (the review pages), `solutions/`, `author-guide/`, `.claude/`,
   `.github/`, `AGENTS.md`, `CLAUDE.md`.
4. **Colab opens the fork**: every Colab link in `chapters/`, `blank/`, `jb/index.md` and `jb/blank.md` points to
   `y-rosenthal/yrThinkPython`, so students get the fork's notebooks. In `blank/`, "Run this notebook on Colab" opens
   the blank notebook itself.
5. **Nothing is published until the checks pass.** `check_sync.py` proves rules 1-4; it fails on any loss.

## 1. See what changed upstream

```bash
git fetch upstream
git log --format='%h %ad %s' --date=short HEAD..upstream/v3    # commits we do not have
git diff --stat HEAD...upstream/v3                              # files he touched
comm -12 <(git diff --name-only HEAD...upstream/v3 | sort) <(git diff --name-only upstream/v3...HEAD | sort)
```

The last command lists the files both sides changed (possible conflicts). Upstream commit messages are usually just
"Updating the notebooks", so read the diff, not the messages. `upstream-diff` shows the fork's own edits, cell by cell.
Summarise for the user: dates, which chapters he changed, which of them the fork also changed.

## 2. Merge on a topic branch (only when asked)

```bash
git switch -c sync-upstream-YYYY-MM v3
git merge --no-ff --no-commit upstream/v3
```

Resolve conflicts with these rules:

| File | Rule |
|---|---|
| A chapter the fork never edited | Take his: `git checkout --theirs chapters/chapNN.ipynb` |
| A chapter the fork edited | Keep ours, then apply his changes to the cells the fork did not touch (find them with `nb_cells.py`, notebook-conventions skill). `check_sync.py` lists any of his cell changes still missing |
| `blank/*.ipynb` | Take his (he maintains them) |
| `jb/index.md`, `jb/blank.md` | Keep ours (`--ours`), then apply every change of his that is not a link (compare with `diff <(git show upstream/v3:jb/index.md) jb/index.md`) |
| `README.md`, `jb/_config.yml`, `jb/_toc.yml`, `.github/` | Keep ours; apply his text corrections by hand. In `jb/_config.yml`, take his build settings (SEO: sitemap, Open Graph, page descriptions) with the fork's site URL; leave out his revenue and analytics (page-view counter, ads, sponsor, support footer) |
| Files of his site that the course site does not use (`jb/_templates/`, `jb/_static/*.css` of the counter, ads, sponsor, support footer) | Delete them, and list each in `NOT_TAKEN` in `check_sync.py` with the reason. Jupyter Book links every css file in `jb/_static` on every page, so an unused stylesheet of his would still load. He changes them rarely; when he does, the merge reports a modify/delete conflict: delete again |
| `.gitignore` | Keep both sides' rules |
| `*.zip`, `thinkpython.py`, `diagram.py`, `structshape.py`, `words.txt` | Take his, unless the fork changed them |

Notebook conflicts are JSON and rarely resolvable line by line. A git auto-merge of a notebook is usually right, and
`check_sync.py` verifies it cell by cell. If a chapter conflict is a correction the fork already reported upstream
(`contribute-upstream`), take his version: it is his wording, and it ends the divergence.

Then point his new Colab links at the fork and check everything:

```bash
python3 ${CLAUDE_SKILL_DIR}/fork_colab_links.py          # rewrite his Colab links to the fork's (safe to repeat)
python3 ${CLAUDE_SKILL_DIR}/check_sync.py                # rules 1-4; must print OK
git commit                                                # the merge commit: say what came in and what was kept
```

`check_sync.py` compares the fork point (BASE), the fork before the merge (BEFORE) and his version (UPSTREAM) with the
working tree. Run it while the merge is in progress, or after the merge commit (it then uses `HEAD^1` as BEFORE). It
reports "both changed" notes for cells both sides edited (the fork's text is kept): read his change and apply it by
hand if it is a correction you want.

## 3. After the merge

1. `python3 .claude/skills/check-notebooks/check_notebooks.py` must print `OK`. It also fails on a Colab link to
   Downey's repository (it calls `fork_colab_links.py --check`).
2. `python3 jb/update_overlay.py`: regenerate the display-tag overlay from his ThinkPythonSolutions notebooks, so new or
   changed cells get his tags; commit `jb/soln_overlay.json` if it changed. Every cell should be "matched".
3. `yr/tools/review.sh check yr/chap*_review.ipynb`: the review pages still pass (the merge must not change them).
4. Build with the `build-book` skill (it runs the chapters): no new warnings, no chapter that fails to run.
5. Push the topic branch. Publish with the `yrpublish` skill only when the user says so (a push to `v3` deploys).

## Where the Colab rule lives

`fork_colab_links.py` is the one place that knows the rule. `make-blank` applies it to each blank notebook it writes;
`check_notebooks.py` fails if a link points to Downey; `upstream-diff` and `contribute-upstream` ignore links that
differ only in the repository name, so a rewritten link is never reported as a correction to send him.
