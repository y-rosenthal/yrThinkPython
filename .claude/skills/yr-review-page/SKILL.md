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

**A new page format is planned, not yet built** (`yr/plans/runall-collapsible-answers.md`). Until
it is, build pages in today's format. Whenever the design or the tools change, update this skill
(and `yr-review-questions`) in the same change. Question numbers stay fixed once a page is in use
during a semester (insert as 3b; see `yr-review-questions`).

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
placeholders), `## Questions` with a setup cell tagged `setup`, and the credit line.
Edit cells with the NotebookEdit tool or a small `json` script (never sed on the JSON).

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
yr/tools/review.sh images yr/chapNN_review.ipynb      # if there are turtle pictures
yr/tools/review.sh check  yr/chapNN_review.ipynb      # must print OK
python3 .claude/skills/check-notebooks/check_notebooks.py
.claude/skills/build-book/build_book.sh               # must report no new warnings
```

Then look at `jb/_build/html/yr/chapNN_review.html` (or serve `jb/_build/html` with
`python3 -m http.server` and open it): sidebar position, numbering of the neighbouring chapters,
the two concept lists open, answers collapsed, pictures shown.

Report to the user what was added, what was verified, and anything not verified (e.g. how the
page looks in Colab, which needs the notebook on GitHub).
