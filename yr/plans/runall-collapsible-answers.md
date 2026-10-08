# Plan: review pages that work with Colab's "Run all", with answers hidden until clicked

**Status (2026-10-08): planning in progress, nothing implemented yet.**
The review pages that are live today (2b–7b) are complete and working; this plan changes how
their questions and answers are laid out. Research notes collected so far:
[runall-research-notes.md](runall-research-notes.md). When the plan is finished, it replaces the
"Draft plan" section below.

## To do

- [ ] Finish the plan (research, prototype, review) and write it into this file
- [ ] Prof. Rosenthal decides the open questions ("Decisions needed" below)
- [ ] Convert the chapter 5 page first and publish it
- [ ] Prof. Rosenthal tests chapter 5 in Colab with the checklist below
- [ ] Convert the other five pages; update the tools, `yr/README.md` and the skills
- [ ] Skills: update `yr-review-questions` and `yr-review-page` (and add a skill if useful) so every
      question with an error, or with output that must stay hidden, is written the same way (goal 7)
- [ ] Human guide: how to add each kind of question, pointing to the skills and tools (goal 8)
- [ ] Check that each problem Prof. Rosenthal reported is fixed on the live pages (goal 6)
- [ ] Publish, verify the live site, then remove the "Pending work" note from `CLAUDE.md`
      and mark this plan done

## What Prof. Rosenthal wants

1. Students can use Colab's **Runtime → Run all**, and it runs to the end of the page.
   Today it stops at the first question whose answer is an error, because Colab ignores the
   `raises-exception` cell tag.
2. After Run all, **nothing outside a collapsed Answer gives an answer away**. Today every
   question's code cell shows its output (printed text, the error, the turtle drawing) right under
   the question.
3. Students see each answer, including the real output, by clicking the Answer's expansion arrow.
4. His idea: show each question's code as plain text, and put the runnable code cell inside the
   Answer.
5. Don't Repeat Yourself: whoever writes a question shouldn't have to type its code twice.
6. **The research must end in fixes**, not just a report: the problems he found must be fixed on
   the live pages. Those problems are: Colab's editor underlining the error before students predict it,
   Run all stopping at the first error, and answers visible after Run all outside a collapsed Answer.
7. **Same treatment every time:** once the approach is settled, create or update the Claude skills
   (`yr-review-questions`, `yr-review-page`, and any new one that helps) so that every future question
   whose code has an error, or whose output must stay hidden, is written the same way. The tools
   (`review_cells.py`, `review.sh check`) should make the right way the easy way and fail on the
   wrong way.
8. **Documentation for people:** a guide for a human editing the review pages that explains how to
   add each kind of question, especially ones whose code has an error, and points to the skills and
   tools to use (for example, a section near the top of `yr/README.md`, or a separate guide linked from it).

## What is live now (for context)

- Six review pages: `yr/chap02_review.ipynb` ... `yr/chap07_review.ipynb` (2b, 3b, 4b, 5b, 6b, 7b).
- Code whose error Colab's editor can see before running (syntax errors, undefined names, wrong
  arguments) is in a string run by `run_code("""...""")`, defined in each page's setup cell, so the
  editor doesn't underline the answer. `review.sh check` enforces this for syntax errors.
  See "Errors an editor can see" in `yr/README.md`.
- Answers are markdown `<details>` blocks. These can't contain a code cell, which is why the new
  layout is needed.

## Key findings so far (details and evidence in the research notes)

- **Collapsed sections in Colab:** a markdown heading collapses everything under it, code cells and
  outputs included. Colab saves this in the notebook as `metadata.colab.collapsed_sections` (a list of
  heading cell ids) and honors it when the notebook is opened from GitHub. Google's ML Crash Course
  uses this to hide solution sections that contain code. *Strong evidence; not yet tested by us.*
- **Run all runs cells inside collapsed sections,** and their outputs stay hidden until expanded.
  *Strong evidence.*
- **JupyterLab / Notebook 7** use cell metadata `"jp-MarkdownHeadingCollapsed": true` on the heading.
- **Errors without stopping Run all:** `run_code` can catch the error and display it. Two variants:
  `get_ipython().showtraceback()` (shows a normal error output; verified that Jupyter keeps going,
  *unknown whether Colab does*), or printing the colored traceback as ordinary output
  (verified to work everywhere, since nothing marks the cell as failed).
- **Colab's editor checks** (red underlines) come from Pyright. Strings and markdown are never
  checked. A `# type: ignore` line at the top of a cell *might* turn checking off for that cell;
  untested in Colab.

## Draft plan (to be replaced by the reviewed final plan)

1. **New layout for every "predict" question** (what is displayed / drawn / happens):
   - The question shows its code in a markdown code block. No runnable cell in the question, except
     cells that only define things later cells need ("Run this cell to define `add_and_show`").
   - The Answer becomes a small heading ("Answer") saved as collapsed for Colab and JupyterLab. Under
     it: the explanation (expected output, stored turtle picture for the website) and a code cell that
     runs the question's code, so Run all fills in the real output inside the hidden Answer.
   - Errors go through `run_code`, which displays the error instead of stopping Run all.
2. **DRY:** the code is written once, in the question. A command in `review_cells.py` generates the
   Answer's run cell from it, and `review.sh check` fails if the two ever differ.
   (Rejected so far: storing the code in a string variable, which is harder for students to read;
   reading the notebook file at run time, which doesn't work in Colab. A custom `%%magic` cell is
   undecided until we know whether Colab's editor checks such cells.)
3. **Website:** `jb/prep_notebooks.py` turns each Answer heading section back into one collapsed box,
   with no "Answer" headings in the page's table of contents, and no new Sphinx warnings.
4. **Tools and docs:** update `check_review.py`, `turtle_images.py`, `review_cells.py`,
   `prep_notebooks.py`, `check_notebooks.py`, `yr/README.md` and the two `yr-review-*` skills.
5. **Rollout:** convert chapter 5 first. Prof. Rosenthal tests it in Colab with a short checklist (below).
   Then convert the other five pages and publish.

## Draft Colab test checklist (for the chapter 5 trial)

1. Open the page from its "Run this page on Colab" link. Are all Answers collapsed?
2. Runtime → Run all. Does it reach the end of the page?
3. After Run all, is any output visible outside a collapsed Answer?
4. Open an Answer: is the real output there (printed text, the error, the turtle drawing)?
5. Do any question cells or Answers show red underlines before you run anything?
6. Does running a cell, or an error, automatically open a collapsed Answer?

## Decisions needed from Prof. Rosenthal

- Should "write code" questions also get a runnable solution cell inside their Answer
  (today their solutions are only text)?
- Which DRY option (see step 2)?

## How to resume (for a future Claude session)

The research was done by a multi-agent workflow in a cloud session on 2026-10-08. While it ran, a
background script pushed each finished agent's result to the branch **`yr-runall-research`**, in
`yr/plans/research/`: one markdown file per agent (research, verify, plan, judge, synthesize, critic,
revise) plus the prototype's files in `prototype/` (converted chapter 5 notebook, modified
`prep_notebooks.py`, conversion scripts). Start there: `git fetch origin yr-runall-research`. If the
final plan (`revise.md`) is missing there and not in this file, redo only the missing parts: map every question on the six pages and every tool that
would change, build a prototype of the chapter 5 conversion in a scratch folder (convert the page,
run it top to bottom with nbclient `allow_errors=False`, build the website from it), then write the
final plan here and ask Prof. Rosenthal for the decisions above before changing the live pages.
