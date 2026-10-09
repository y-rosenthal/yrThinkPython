---
name: yr-review-questions
description: Add, revise or check practice questions (with collapsible answers, examples and turtle pictures) on a "Prof. Rosenthal's Review" page in yr/chapNN_review.ipynb, and verify every answer by running it. Use when asked to add/write/change/fix review questions, exercises, quiz or practice problems for a chapter's review page, or to check a review page's answers.
user-invocable: true
argument-hint: [chapter number] [how many / what topics]
---

# Add or revise review questions

Read `yr/README.md` first: the guide "Adding a question", the **style rules**, the markers, the
format rules and the tools. If the chapter has no review page yet, use the `yr-review-page` skill
instead. Work on a topic branch, not `v3`.

Whenever the design or the tools change, update this skill, `yr-review-page` and `yr/README.md` in the
same change.

## The rules

- **Focus on code.** Mostly "what is displayed / drawn / happens?" and "write code".
- **Standalone.** Each question must make sense to someone who never saw Think Python: no
  references to the book or its examples; give every helper function the question uses; the main
  point is the Python, and context goes last in a "**By the way:**" paragraph.
- **Levels.** Heading `### Question N (easy|medium|hard): <kind>`; keep the page ordered easy → hard.
- **Question numbers never change during a semester** (homework is assigned by number). A question
  inserted between Questions 3 and 4 is **Question 3b** (then 3c, ...): get the number with
  `python3 yr/tools/review_cells.py next NB --before 4`. Never renumber the others;
  `review_cells.py renumber` is only for the start of a new semester, when Prof. Rosenthal asks.
- **Write-code questions** give the function header (unless the point is writing it: tag the
  `# Your code here` cell `no-signature`) and at least 2 examples with their output.
- **Wrong-call questions** first show at least 2 correct ways to call the function, with output.
- **Answers** give more than one approach when there is one.
- **No `(c)`/`(r)`/`(tm)`/`+-` in text**: write **Part a**, **Part b**, **Part c**.
- Only use Python taught up to this chapter, or explain the extra bit in the question.

## Type each fact once

You type: the question's code (a `~~~python` run block), the prompt, the example calls, the
solutions, the fixes, helpers (once, in a definition cell), and the explanation with each value
written as an expression and a marker. `review.sh sync` writes everything else by running the code
on the pinned Colab-like kernel: run cells and their outputs, error names, example outputs and
pictures, the "Start from this header" block, import lines, "Then try:", "uses X from Question N",
"Run this cell to define X", values, and the template cells.

**Never type or edit by hand:** run cells, stored outputs, ```` ```text ```` blocks or pictures in a
question, anything between `<!-- begin generated: ... -->` and `<!-- end generated: ... -->`, the
first N lines of a block under `<!-- generated imports: N -->`, a value after a marker (type `?`), the
help note, the helper cell, the credits, the notebook metadata `yr_review`. `review.sh check` fails
on any of these.

Per kind (the README has a spec example for each):

- **What is displayed / drawn / happens**: `%%% run` with the code; the Answer explains, and quotes
  values as `` `EXPR` is <!--=-->`?` `` or `` <!--= EXPR -->`?` ``. A value marker never starts a line
  or a list item (Colab shows the line as raw HTML).
- **Errors** (syntax errors, NameError, wrong calls, a failing import, RecursionError): the same,
  with `%%% run a` / `%%% run b` for parts and `%%% part a` / `%%% part b` for each part's
  explanation; name each error with `` <!--=error-->`?` ``. Nothing else is needed: the code is text, so
  Colab's editor can't underline it, and sync wraps the run cell so the traceback prints as text.
- **Write a function**: the prompt, `**Examples**`, ```` ```python ```` blocks with the calls only,
  `%%% placeholder`, and the solution(s) in the Answer with **no** example calls, example inputs,
  provided helpers or imports. Every Answer block must give every example's output; mark a
  halfway version `<!-- not a solution -->`.
- **Write code without a function**: examples assign the inputs; `%%% placeholder no-signature`;
  the solution is only the computation.
- **Helpers**: one definition cell (`%%% code`) where the helper is first provided; later questions
  just use it.
- **Fixes and "what if"**: a short ```` ```python ```` block in the Answer: the changed lines, or the
  new `def` (the question's calls run after it). Keep an input line if a later question assigns
  that name (check prints those names as notes). For the whole code with one change, use
  `<!-- derive: from=QN replace="OLD" with="NEW" -->` over an empty block.
- **Turtle drawings**: start example and run-block code with `make_turtle()`; keep the drawing
  inside the canvas (300 × 150, the turtle starts in the middle).

### Steps

1. `python3 yr/tools/review_cells.py list yr/chapNN_review.ipynb`; pick topics from the page's
   Concepts covered that have few or no questions.
2. Write the questions in a spec file in your scratchpad (format: run `python3 yr/tools/review_cells.py`
   without arguments; examples in `yr/README.md`, "Adding a question").
3. `python3 yr/tools/review_cells.py add yr/chapNN_review.ipynb SPEC [--before N]`. The tool refuses a
   number that already exists and prints the free one.
4. `yr/tools/review.sh sync yr/chapNN_review.ipynb`. Read every new output and value in its report:
   does the explanation still say the right thing? If sync says an output that was already on the
   page changes, reread that Answer; only if it is still right, run sync again with `--accept`. Sync
   refuses (exit 2) if a solution disagrees with another, a value marker fails, or an output is too
   long; fix the question.
5. `yr/tools/review.sh check yr/chapNN_review.ipynb` must print OK. Fix the question or the answer
   until it passes; never weaken the check. Its rule numbers are in `yr/README.md`, "Format rules";
   rule 12 (C4) means an Answer block does not run, or does not show what the page says, when a
   student copies it into a new cell after Run all.
6. Look at new pictures (extract a PNG from the stored output or the `data:` URI, or build the site).
7. If "Concepts covered" lacks a fact a new question relies on, add it there (same style).
8. `python3 .claude/skills/check-notebooks/check_notebooks.py` and
   `.claude/skills/build-book/build_book.sh` (no new warnings); look at the page.

To revise a question, edit the cells you typed (NotebookEdit tool or a `json` script, keeping cell
ids), then steps 4-8. If the page was saved from Colab, run `yr/tools/review.sh normalize NB` first.
After changing any tool, run `yr/tools/review.sh selftest`.

Report which questions were added or changed and that `review.sh check` passed.
