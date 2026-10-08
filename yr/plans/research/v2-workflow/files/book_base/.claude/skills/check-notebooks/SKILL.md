---
name: check-notebooks
description: Lint the chapter notebooks (valid JSON, no stored outputs, cell ids, %%expect/# Solution conventions, TOC and Colab-link consistency) and optionally execute them to catch runtime errors. Use after any notebook edit, before committing, or when asked to test/validate/run the notebooks.
user-invocable: true
argument-hint: [notebook paths | all | --run]
---

# Check the notebooks

Arguments: `$ARGUMENTS` (empty means static check of everything).

## 1. Static check (seconds, no dependencies)

```bash
python3 ${CLAUDE_SKILL_DIR}/check_notebooks.py            # all chap*.ipynb in chapters/, blank/ and solutions/, plus TOC/links/workflow glob
python3 ${CLAUDE_SKILL_DIR}/check_notebooks.py chapters/chap05.ipynb
```

It reports, per cell: invalid JSON, missing/duplicate cell ids, stored outputs, malformed
`%%expect` / `%%add_method_to` lines, `# Solution` cells that contain code (the build blanks them),
and, when run with no arguments: chapters missing from `jb/_toc.yml`, TOC entries with no file,
Colab links in `jb/index.md` / `jb/blank.md` that point at the wrong repo/branch or a missing file,
TOC notebooks not matched by the `cp` glob in `.github/workflows/deploy-book.yml`, and
`solutions/chapNN.ipynb` cells that would not reach the site (code cells whose id is not a
`# Solution goes here` placeholder in the chapter). Placeholders with no solution are listed as
a note, not a problem.
Fix everything it lists; a clean run prints `OK`.

## 2. Execute notebooks (when code changed, or `--run` / "run the notebooks" was asked)

```bash
${CLAUDE_SKILL_DIR}/run_notebooks.sh chapters/chap05.ipynb chapters/chap06.ipynb
${CLAUDE_SKILL_DIR}/run_notebooks.sh all      # ~all 20 chapters, several minutes, needs network for download() cells
```

- First run creates a venv at `~/.venvs/yrThinkPython` (system Python 3.12) and installs
  nbconvert/ipykernel/jupyter-book/matplotlib/pyyaml. That is outside the repo on purpose
  (the repo is in Dropbox).
- Notebooks execute as copies in `/tmp/yrThinkPython-run`; the repo files are untouched and
  gain no outputs. Logs and executed copies (with outputs) are there for inspection.
- How results are judged:
  - Errors in cells **before** the `## Exercises` heading fail the notebook: those are real bugs.
  - Errors **after** it are listed as "expected" and do not fail: exercise test cells call
    functions whose `# Solution goes here` cells are intentionally empty. Every chapter with
    exercises has a few of these. Still glance at them: an error that is not a NameError for
    an exercise function may be real.
  - A `%%expect SomeError` cell that raises exactly `SomeError` passes. A different exception
    is reported with "(%%expect SomeError declared)".
  - `input()` is stubbed to return a non-numeric string, so the chapter 5 input cells run.
- Chapter 4 (turtle graphics) and chapters 12-13 (Project Gutenberg downloads) need network.
- `run_notebooks.sh solutions/chap04.ipynb` must report no errors at all: the test cells after
  the exercises exercise the solutions. (Do not pass a chapter and its solutions notebook in the
  same run; both copies are named `chapNN.ipynb` in the scratch dir and the second overwrites the first.)
- All 20 chapters take a few minutes; run only the chapters you touched during iteration.

Report failures with the notebook, cell index (use `nb_cells.py` from the notebook-conventions
skill to map the traceback to a cell), and the exception text.
