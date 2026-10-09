---
name: yr-review-page
description: Create a "NNb. Prof. Rosenthal's Review" page for a Think Python chapter (yr/chapNN_review.ipynb, a concepts checklist plus practice questions with collapsible answers) and add it to the site, or write/revise the "Concepts covered" summary of an existing review page. Use when asked for a review page, chapter summary, fact list, concepts checklist or study guide for a chapter.
user-invocable: true
argument-hint: [chapter number] [concepts-only]
---

# Create a review page (or its concept summary)

Read `yr/README.md` first. It has the page layout, the **style rules** (they are Prof. Rosenthal's
instructions, follow them exactly) and the cell conventions. `yr/chap04_review.ipynb` is the
reference example: read it before writing a new page.

Work on a topic branch, not `v3` (`git switch -c yr-review-chNN`); leave committing/pushing to
the user unless asked.

**Build new pages in the new format** (`#### Answer` headings; `yr/README.md`, "Layout of a page"):
`review_cells.py new` creates one, and `review.sh sync` writes the template cells (help note,
helper cell, credits), the run cells and every output. The six existing pages are converted one at
a time (`yr/plans/runall-collapsible-answers.md`); edit a page that is not converted yet in the old
format. Whenever the design or the tools change, update this skill, `yr-review-questions` and
`yr/README.md` in the same change. Question numbers stay fixed once a page is in use during a
semester (insert as 3b; see `yr-review-questions`).

## 1. Study the chapter

Read every cell of `chapters/chapNN.ipynb`
(`python3 .claude/skills/notebook-conventions/nb_cells.py chapters/chapNN.ipynb`, then `--full`
for the cells you need). List every fact taught: syntax, behavior, functions and modules used,
definitions (the chapter's Glossary is a checklist for these), practices. Note what earlier
chapters cover, so questions only use material up to this chapter (or teach anything extra in
the question itself).

## 2. Create the skeleton

```bash
python3 yr/tools/review_cells.py new NN "Chapter title"     # -> yr/chapNN_review.ipynb
```

It has the title cell, `## Concepts covered` with the two `<details open>` lists (TODO
placeholders), `## Questions` with a setup cell tagged `setup`, and the credits.
Edit cells with the NotebookEdit tool or a small `json` script (never sed on the JSON).
The first `review.sh sync` adds the help note and the helper cell "Helper for the Answers" (it defines
`run_code`, which error answers use); never edit those or the title and credits cells by hand.

## 3. Write "Concepts covered"

Follow the style rules in `yr/README.md`. In short:

- **Python Syntax and Semantics**: every fact about Python syntax and behavior in the chapter,
  grouped under short bold labels. Keep it short and show the syntax in the most straightforward
  way: the general form with UPPERCASE placeholders (`for i in range(SOME_INTEGER):` /
  `    SOME_CODE`), one sentence saying what it does, then "For example" and a small example.
  No arrows or shorthand notation. Instruction-manual tone: facts, not explanations.
- Facts only: an example is not a fact ("a loop of `forward(50)` / `left(90)` four times draws a
  square" is out). State the underlying rule instead ("`range(SOME_INTEGER)` is shorthand for
  `0, 1, 2, ...` up to SOME_INTEGER minus 1").
- **Definitions, etc.**: `**Definitions**` with bullets `DEFINITION: **term** is ...`, then
  `**Other ideas**` for practices and concepts that are not syntax.
- Nothing that is not about Python or programming.
- Complete: someone who ticks off every bullet has reviewed the whole chapter. Add facts that the
  questions rely on.
- Values in the lists are written as expressions with a marker, and sync fills them in:
  `` `-7 // 2` is <!--=-->`?` `` (never at the start of a line or list item). Concepts values are
  computed after the setup cell only.

For "concepts-only" requests (revise the summary of an existing page) stop after this step and
go to step 6.

## 4. Write the questions

Use the `yr-review-questions` skill for the details (kinds, examples, answers, pictures,
verification). Aim for about 15-20 questions, roughly a third each easy, medium and hard, mostly
"what is displayed / drawn / happens" and "write code". Adapt the setup cell to the chapter
(downloads such as `jupyturtle.py` or `words.txt`, imports) and introduce any module the
questions use at the top of the Questions section.

## 5. Add the page to the site

- `jb/_toc.yml`: split the numbered "Chapters" list after `chapNN` and list the page in its own
  unnumbered part between the halves:
  ```yaml
      - file: chapNN
  - chapters:
      - file: yr/chapNN_review
  - numbered: True
    chapters:
      - file: chap(NN+1)
  ```
  (The comment above `yr/chap04_review` in the TOC explains why; keep it only once.)
- `jb/index.md`: under the chapter's Colab line add
  `* [Click here to run NNb. Prof. Rosenthal's Review on Colab](https://colab.research.google.com/github/y-rosenthal/yrThinkPython/blob/v3/yr/chapNN_review.ipynb)`
- `yr/README.md`: update "so far: chapter ..." in the folder listing.

## 6. Verify

```bash
yr/tools/review.sh sync  yr/chapNN_review.ipynb       # writes outputs, pictures, values; read its report
yr/tools/review.sh check yr/chapNN_review.ipynb       # must print OK
python3 .claude/skills/check-notebooks/check_notebooks.py
.claude/skills/build-book/build_book.sh               # must report no new warnings
```

Then `python3 yr/tools/verify_site.py jb/_build/html/yr/chapNN_review.html yr/chapNN_review.ipynb`
(one closed Answer per question, no hidden code or markers on the page), and look at
`jb/_build/html/yr/chapNN_review.html` (or serve `jb/_build/html` with `python3 -m http.server`):
sidebar position, numbering of the neighbouring chapters, the two concept lists open, answers
collapsed, outputs and pictures shown. (Old-format page: `review.sh images` instead of `sync`.)

Report to the user what was added, what was verified, and anything not verified (e.g. how the
page looks in Colab, which needs the notebook on GitHub).
