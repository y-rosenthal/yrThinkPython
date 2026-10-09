---
name: build-book
description: Build the Jupyter Book HTML locally (same steps as the GitHub Actions deploy) and preview a chapter. Use when asked to build, preview, render, or check how the book/site looks, or to reproduce a deploy failure locally.
user-invocable: true
argument-hint: [--clean] [--open] [--update-baseline] [--no-exec]
---

# Build the book locally

```bash
${CLAUDE_SKILL_DIR}/build_book.sh $ARGUMENTS
```

What it does, mirroring `.github/workflows/deploy-book.yml` exactly:

1. Creates/activates the venv `~/.venvs/yrThinkPython` (system `/usr/bin/python3`, 3.12, with
   `jupyter-book<2`). The linuxbrew default `python3` is 3.14 and is not used. Override with
   `THINKPYTHON_VENV` / `THINKPYTHON_PYTHON` if needed.
2. `cp chapters/chap[01][0-9].ipynb jb/` and `cp yr/*.ipynb jb/yr/` (these copies are gitignored).
3. `python jb/execute_notebooks.py`: runs every chapter copy so the pages show code outputs
   (the committed notebooks have none, and Jupyter Book's own execution is off). Exercise
   placeholders are filled, in a scratch copy only, with our `solutions/` or Downey's solutions
   from `jb/soln_overlay.json`, so the exercise test cells draw their example pictures. Unexpected
   errors are dropped and reported as warnings; a chapter that cannot run is left without outputs.
   About 45 seconds; needs network (Gutenberg texts, jupyturtle). The yr/ review pages are
   not executed: converted pages show the outputs that `yr/tools/review.sh sync` stored in their
   hidden run cells, inside the closed Answer dropdowns.
4. `python jb/prep_notebooks.py`: adds Downey's display tags from `jb/soln_overlay.json`
   (`remove-input`, `remove-cell`, `section_*` labels: same shown/hidden cells as his site),
   strips `%%expect` lines, adds section labels, turns `# Solution…` cells into collapsed
   "Suggested solution" dropdowns when `solutions/chapNN.ipynb` has a matching cell id (see the
   notebook-conventions skill), otherwise blanks them, and prepares the yr/ review pages
   (`yr/README.md`, "How the build handles yr/"; on a converted page it stops the build if an
   Answer dropdown is missing or notebook machinery such as `@title` or a marker is left).
5. `jb build .` inside `jb/`. Output: `jb/_build/html/index.html`, one `chapNN.html` per chapter.

Flags: `--clean` runs `jb clean` first (use after changing `_toc.yml` or `_config.yml`, since
Sphinx caches aggressively); `--open` opens the index in the browser; `--update-baseline`
rewrites `known_warnings.txt` (see below); `--no-exec` skips step 3 for a quick text-only
preview (pages then have no outputs and the warning list differs).

## Checking the result

- The script compares Sphinx warnings against `known_warnings.txt` in this skill's folder and
  prints only **new** ones. The few known warnings are harmless "Lexing literal_block" notices
  (syntax highlighting of tracebacks and deliberate syntax errors) and the like. Fix new warnings; a TOC entry with no file, a broken `{ref}` label, or
  a markdown cell with unbalanced backticks are the usual causes.
- If you deliberately fix or add known warnings, rerun with `--update-baseline` and commit
  `known_warnings.txt` with the change.
- To confirm a specific edit rendered: `grep -c "some phrase" jb/_build/html/chap03.html`.
- To view a page in Chrome use the claude-in-chrome tools on
  `file:///home/yitz/Dropbox/_yrQuarto-master/yrThinkPython/jb/_build/html/chap03.html`.
- A full build takes about a minute (half of it executing the chapters).

Never commit `jb/_build/` or `jb/chap*.ipynb` (both gitignored). Publishing is done by the
workflow, not locally: see the `deploy-book` skill.
