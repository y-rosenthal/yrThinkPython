---
name: build-book
description: Build the Jupyter Book HTML locally (same steps as the GitHub Actions deploy) and preview a chapter. Use when asked to build, preview, render, or check how the book/site looks, or to reproduce a deploy failure locally.
user-invocable: true
argument-hint: [--clean] [--open] [--update-baseline]
---

# Build the book locally

```bash
${CLAUDE_SKILL_DIR}/build_book.sh $ARGUMENTS
```

What it does, mirroring `.github/workflows/deploy-book.yml` exactly:

1. Creates/activates the venv `~/.venvs/yrThinkPython` (system `/usr/bin/python3`, 3.12, with
   `jupyter-book<2`). The linuxbrew default `python3` is 3.14 and is not used. Override with
   `THINKPYTHON_VENV` / `THINKPYTHON_PYTHON` if needed.
2. `cp chapters/chap[01][0-9].ipynb jb/` (these copies are gitignored).
3. `python jb/prep_notebooks.py`: strips `%%expect` lines, adds section labels, and turns
   `# Solution…` cells into collapsed "Suggested solution" dropdowns when `solutions/chapNN.ipynb`
   has a matching cell id (see the notebook-conventions skill), otherwise blanks them.
4. `jb build .` inside `jb/`. Output: `jb/_build/html/index.html`, one `chapNN.html` per chapter.

Flags: `--clean` runs `jb clean` first (use after changing `_toc.yml` or `_config.yml`, since
Sphinx caches aggressively); `--open` opens the index in the browser; `--update-baseline`
rewrites `known_warnings.txt` (see below).

## Checking the result

- The script compares Sphinx warnings against `known_warnings.txt` in this skill's folder and
  prints only **new** ones. The 29 known warnings are inherited from upstream: 26 missing
  `section_*`/`chapter_*` cross-reference targets (the notebooks reference labels, but no cell
  carries the matching tag any more) and 3 harmless "Lexing literal_block" notices. They are on
  the live site too. Fix new warnings; a TOC entry with no file, a broken `{ref}` label, or
  a markdown cell with unbalanced backticks are the usual causes.
- If you deliberately fix or add known warnings, rerun with `--update-baseline` and commit
  `known_warnings.txt` with the change.
- To confirm a specific edit rendered: `grep -c "some phrase" jb/_build/html/chap03.html`.
- To view a page in Chrome use the claude-in-chrome tools on
  `file:///home/yitz/Dropbox/_yrQuarto-master/yrThinkPython/jb/_build/html/chap03.html`.
- A full build takes about a minute; incremental rebuilds are faster.

Never commit `jb/_build/` or `jb/chap*.ipynb` (both gitignored). Publishing is done by the
workflow, not locally: see the `deploy-book` skill.
