---
name: upstream-diff
description: Show how this fork's notebooks differ from Allen Downey's upstream ThinkPython, cell by cell, separating course-specific material (tagged "course") from corrections that could be sent upstream. Use when asked what has changed vs upstream/the original, to review the fork's edits, or before syncing or contributing upstream.
user-invocable: true
argument-hint: [chapters/chapNN.ipynb ... | --all] [--ref REF]
---

# Diff the fork against upstream

```bash
git fetch upstream                                             # make upstream/v3 current
python3 ${CLAUDE_SKILL_DIR}/upstream_diff.py $ARGUMENTS
```

- No arguments: one summary line per notebook that differs (changed / added / removed cells,
  how many of the edits carry the `course` tag), plus `git diff --stat` for non-notebook files.
- With notebook paths, or `--all`: the full cell-by-cell diff. Changed cells show a unified diff
  of their text under the section heading they sit in; added cells show their first lines.
- `--ref origin/v3` compares the working tree against a different ref (e.g. to see what is
  uncommitted relative to the deployed site).

Cells are matched by **cell id**, not position, so inserting an exercise does not make every
later cell look changed, and upstream reordering does not look like an edit.

## Reading the result

- **changed, untagged**: probably a correction. Consider sending it upstream (`contribute-upstream`).
- **changed or added, tagged `course`**: the user's own material. Never sent upstream, kept on merge.
- **added, untagged**: the script flags it. Ask whether it is course material and add the tag.
- **removed**: an upstream cell the fork deleted. Rare; confirm it was intended.

## Rich side-by-side view

`nbdime` is installed in the book venv (`~/.venvs/yrThinkPython`):

```bash
source ~/.venvs/yrThinkPython/bin/activate
git show upstream/v3:chapters/chap05.ipynb > /tmp/up_chap05.ipynb
nbdiff /tmp/up_chap05.ipynb chapters/chap05.ipynb          # terminal, notebook-aware
nbdiff-web /tmp/up_chap05.ipynb chapters/chap05.ipynb      # browser, side by side
```

To make plain `git diff` notebook-aware for this repo: `nbdime config-git --enable` (writes to
`.git/config` and `.gitattributes`; run once, and commit `.gitattributes` if it should apply for
everyone).
