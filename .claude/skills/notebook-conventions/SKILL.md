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
  *starts with* `# Solution`, so never put real code under that comment. Suggested solutions
  go in `solutions/chapNN.ipynb` instead (see below).
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
- **Display tags and section labels are not in these notebooks.** Downey builds his site from
  his ThinkPythonSolutions notebooks, which carry outputs and tags (`remove-input`, `remove-cell`,
  `section_*` labels) that are stripped from `chapters/`. This fork keeps his tags, matched by
  cell id, in `jb/soln_overlay.json` (regenerate with `python jb/update_overlay.py` after syncing
  upstream); `prep_notebooks.py` applies them at build time, and `execute_notebooks.py`
  produces the outputs. So do not add such tags to `chapters/`. A new cell you add for the
  course has no overlay entry: it is shown with its output, which is usually what you want; to
  hide its code or the whole cell on the site, give it a `remove-input` / `remove-cell` tag (and
  the `course` tag).

## Course material vs corrections: the `course` tag

Every cell you **add** for the course (new exercises, notes, examples) and every upstream cell
you **change for course reasons** (not to fix an error) gets the tag `course` in its metadata:
`"metadata": {"tags": ["course"]}`. Leave corrections to the original text untagged. This is
what lets `upstream-diff` separate your material from fixes worth sending upstream, and what
`contribute-upstream` uses to leave course cells out of issue drafts. The tag has no effect on
the built site. For a new exercise, tag the `### Exercise` markdown cell and its
`# Solution goes here` cell(s).

## Course additions go in `yr/`

New course material (chapter summaries, extra questions) goes in `yr/`, not in `chapters/`:
one review notebook per chapter, `yr/chapNN_review.ipynb`, shown on the site as
"NNb. Prof. Rosenthal's Review" right after the chapter. Read `yr/README.md` before creating or
editing one: it has the page layout (concepts checklist, then easy → hard questions), the
`<details>` answer format, the `# Your code here` and `raises-exception` conventions, and the
TOC / index.md steps. The `yr-review-page` and `yr-review-questions` skills cover creating
pages and adding questions, with tools in `yr/tools/` that write outputs and pictures (`review.sh sync`)
and verify answers (`review.sh check`). Review pages follow their own format (`yr/README.md`): they
store outputs on their hidden run cells, so the "no stored outputs" rule above does not apply to them.

## Suggested solutions: `solutions/chapNN.ipynb`

Solutions never go in `chapters/` (Colab opens the raw notebook, so students would see them).
They live in `solutions/chapNN.ipynb`, a copy of the chapter notebook in which the
`# Solution goes here` cells contain the solution code, **with the same cell ids**. At build
time `jb/prep_notebooks.py` matches those cells by id and shows each one on the website inside
a collapsed "Suggested solution" dropdown (readers click to reveal it); consecutive solution
cells become one dropdown, and a note is inserted after the `## Exercises` heading. Chapters
without a solutions notebook keep the old behaviour (blank cells). Chapters 4 and 5 have
one (added 2026-09-09); add more chapter by chapter as the user asks.

Rules: only fill in placeholder cells, do not add or edit other cells there (the checker flags
it, and the site ignores it). Leave a placeholder as `# Solution goes here` to keep it blank.
When a chapter changes, its solutions notebook does not need to change unless placeholder cells
were added or removed; the checker lists placeholders that have no solution. To create one for
another chapter: copy `chapters/chapNN.ipynb` to `solutions/`, fill in the placeholders with a
`json` script (keep ids), then run it with `run_notebooks.sh solutions/chapNN.ipynb` (it must
execute with no errors at all, including the exercise test cells) and build the book.

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
