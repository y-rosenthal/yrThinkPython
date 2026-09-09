---
name: make-blank
description: Regenerate the "fill in the blanks" notebooks in blank/ from chapters/ by emptying all code cells except setup cells. Use when a chapter was edited and its blank version must match, or when asked to create/update/refresh blank notebooks.
user-invocable: true
argument-hint: [chapter numbers | all] [--diff]
---

# Regenerate blank notebooks

`blank/chapNN.ipynb` is the student version of `chapters/chapNN.ipynb`: same markdown, every
code cell emptied so students type the code themselves. Setup cells students must run as-is
(the `download()` cell, `%xmode Verbose`, `from diagram import …`) are kept.

```bash
python3 ${CLAUDE_SKILL_DIR}/make_blank.py --diff $ARGUMENTS    # report which files would change, write nothing
python3 ${CLAUDE_SKILL_DIR}/make_blank.py $ARGUMENTS           # write blank/chapNN.ipynb  (e.g. "03 07" or "all")
```

Notes:

- The current `blank/` files came from upstream and were made by hand, so they drift from
  `chapters/` in small ways (a moved paragraph, "Ask an assistant" vs "Ask a virtual assistant",
  and upstream kept setup cells only in chapters 1-3). Regenerating from `chapters/` makes the
  blank version follow the fork's edits exactly; that is the intended behaviour. Mention the
  drift to the user the first time a chapter is regenerated.
- The kept-cell rules are the `KEEP_PREFIXES` tuple at the top of `make_blank.py`; extend it if
  a new kind of setup cell is introduced.
- Markdown, cell ids and notebook metadata are copied unchanged, so `git diff` of a
  regenerated file shows only code-cell changes.
- Afterwards run the `check-notebooks` static check, and remember `jb/blank.md` links to these
  files on Colab (the book itself does not include them).
