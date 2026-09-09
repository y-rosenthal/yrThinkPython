---
name: notebook-conventions
description: Conventions for editing the Think Python chapter notebooks (chapters/chapNN.ipynb, blank/). Load before adding, changing, or removing any cell, exercise, or text in a .ipynb file in this repo.
user-invocable: true
argument-hint: [chapters/chapNN.ipynb]
---

# Editing the Think Python notebooks

**Source of truth:** `chapters/chapNN.ipynb`. `jb/chap*.ipynb` are gitignored copies made
at build time; never edit them. `blank/` holds the fill-in-the-blanks versions (see the
`make-blank` skill). `chapters/jupyter_intro.ipynb` is not in the book, only in the zip.

## Find the cell first

```bash
python3 ${CLAUDE_SKILL_DIR}/nb_cells.py chapters/chap03.ipynb                # index, type, first line of every cell
python3 ${CLAUDE_SKILL_DIR}/nb_cells.py chapters/chap03.ipynb --grep "Exercise|expect"
python3 ${CLAUDE_SKILL_DIR}/nb_cells.py chapters/chap03.ipynb --full 65      # print one cell in full
```

Then edit with the NotebookEdit tool (cell index or cell id) or a small stdlib `json` script.
Do not hand-edit the raw JSON with sed. Do not run the notebook in place: outputs must
stay out of the committed file.

## Cell format (nbformat 4.5)

- `source` is a list of lines, each ending in `\n` except the last. Match the existing style.
- Every cell has an 8-hex-char `id` (e.g. `"1331faa1"`); new cells need a fresh unique one.
- Code cells: `"metadata": {"tags": []}`, `"outputs": []`, `"execution_count": null` (or an int).
  **No outputs are committed.** The site is built with `execute_notebooks: 'off'`, so what
  readers see online is exactly the source text.
- Markdown cells: `"metadata": {}`.

## Content conventions

- Chapter title is a `#` heading in the first markdown cell; sections are `##`; each chapter
  ends with `## Glossary`, then `## Exercises` containing `### Ask a virtual assistant`
  and several `### Exercise` subsections.
- **Exercises**: a `### Exercise` markdown cell, then one or more code cells whose entire
  source is `# Solution goes here`. `jb/prep_notebooks.py` blanks any code cell that
  *starts with* `# Solution`, so never put real code under that comment.
- **Expected errors**: cells that deliberately raise use the cell magic on line 1,
  a blank line, then the code:
  ```
  %%expect ValueError

  int('hello')
  ```
  Exactly one exception name. The magic is defined in `thinkpython.py`; the build strips
  the first line so the site shows plain code.
- **Adding methods to a class across cells** uses `%%add_method_to ClassName` (chap 15-17).
- **Setup cells**: each chapter starts with the `download()` cell that fetches
  `thinkpython.py`, `diagram.py`, sometimes `jupyturtle.py`/`words.txt` from
  `https://github.com/AllenDowney/ThinkPython/raw/v3/…`. Those URLs point at the
  *upstream* repo, so changes to the fork's helper modules do not reach Colab users unless
  the URLs are changed to `y-rosenthal/yrThinkPython`. The `%xmode Verbose` cell sits at
  the start of the Exercises section.
- Section labels for cross references come from cell tags starting with `section`/`chapter`
  (prep_notebooks.py turns them into MyST `(label)=` targets). The current notebooks have
  **no** such tags, yet about 26 markdown cells still contain links like
  `[Chapter 10](section_memos)`, which render as broken cross references (known build warnings).
  To fix one, add the tag (e.g. `section_memos`) to the `tags` list of the heading cell it
  should point to; do not remove the reference text.

## After editing

1. `python3 ${CLAUDE_PROJECT_DIR}/.claude/skills/check-notebooks/check_notebooks.py` (fast, stdlib only).
2. If code changed, execute it: `${CLAUDE_PROJECT_DIR}/.claude/skills/check-notebooks/run_notebooks.sh chapters/chapNN.ipynb`.
3. If the chapter has a `blank/` counterpart and the edit affects it, regenerate it (`make-blank` skill).
4. Preview with the `build-book` skill when text or structure changed.
5. The Colab links in `jb/index.md` and `jb/blank.md` point at `v3`; the site rebuilds on push to `v3` (see `deploy-book`).
6. If the edit corrects an error in the original book (not a course-specific change), report it
   upstream with the `contribute-upstream` skill so the fix lands in his copy too.

## Branches

Work on a branch, not on `v3`: `git switch -c <topic>` before editing. `v3` is what the site
is built from, and every push to it deploys. Merge to `v3` (or open a PR on the fork) when
the change is checked and built.
