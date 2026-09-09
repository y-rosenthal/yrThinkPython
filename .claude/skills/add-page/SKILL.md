---
name: add-page
description: Add a new chapter, notebook, or markdown page to the Think Python book so it builds, appears in the table of contents, and gets a Colab link. Use when asked to add a chapter/appendix/page/section to the book or to include an existing notebook in the site.
user-invocable: true
argument-hint: [chapters/chapNN.ipynb "Title"]
---

# Add a page to the book

The book is assembled from `jb/_toc.yml`; a file that is not listed there is not built.
Chapter notebooks live in `chapters/`; standalone markdown pages live in `jb/`.

## New chapter notebook

1. Create it:
   ```bash
   python3 ${CLAUDE_SKILL_DIR}/new_notebook.py chapters/chap20.ipynb "Chapter Title"
   ```
   This copies the `download()` and `%xmode` setup cells from chapter 1 and adds a title,
   a section, and an Exercises section with a `# Solution goes here` cell. Fill in the content
   following the `notebook-conventions` skill.
2. Add it to `jb/_toc.yml` under the numbered `Chapters` part (order = book order).
3. Add a Colab link entry to `jb/index.md`, same format as the others:
   `https://colab.research.google.com/github/y-rosenthal/yrThinkPython/blob/v3/chapters/chap20.ipynb`.
   If a blank version exists, add it to `jb/blank.md` too.
4. **Check the copy glob.** Both `.github/workflows/deploy-book.yml` and
   `build_book.sh` copy `chapters/chap[01][0-9].ipynb` into `jb/`. A name like `chap20.ipynb`
   or `appendix.ipynb` is not matched, so widen the glob in both places. The static check
   (`check_notebooks.py`) reads the workflow's glob and flags any TOC notebook it misses.
5. Run the `check-notebooks` static check, then `build-book`. Confirm the page appears in the
   sidebar and its heading numbering looks right.

## Markdown page (no code)

Create `jb/<name>.md`, list it in `jb/_toc.yml` (unnumbered `Front Matter` / `End Matter` parts
are for non-chapters), build. MyST extensions enabled in `_config.yml` include `colon_fence`,
`dollarmath`, `deflist`, `tasklist`, so `:::{note}` admonitions and `$x^2$` math work.

## Removing or reordering

Edit `_toc.yml` only; leave the notebook in `chapters/` unless the user wants it deleted. Update
`jb/index.md` links to match, and rebuild with `--clean` because Sphinx caches the old TOC.
