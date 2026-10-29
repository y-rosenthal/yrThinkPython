---
name: yr-review-questions
description: Add, revise or check practice questions (with collapsible answers, examples and turtle pictures) on a "Prof. Rosenthal's Review" page in yr/chapNN_review.ipynb, and verify every answer by running it. Use when asked to add/write/change/fix review questions, exercises, quiz or practice problems for a chapter's review page, or to check a review page's answers.
user-invocable: true
argument-hint: [chapter number] [how many / what topics]
---

# Add or revise review questions

The rules are in `yr/README.md`, "Review pages": the **style rules** (Questions, Answers), "Adding a question"
(what you type for each kind, and the workflow), "Markers", "What sync writes", "Format rules", "Change a
question" and "Troubleshooting". Read them first, and follow them. Do not repeat a rule here: if a rule is
missing or wrong, change `yr/README.md`.

If the chapter has no review page yet, use the `yr-review-page` skill instead. Work on a topic branch, not `v3`.

## Steps for the agent

1. `python3 yr/tools/review_cells.py list yr/chapNN_review.ipynb`; pick topics from the page's
   Concepts covered that have few or no questions.
2. Write each question in a spec file in your scratchpad, then follow the workflow of `yr/README.md`,
   "Adding a question" (number, add, sync, check, pictures, concepts, notebook check, build). Read every
   new output and value in sync's report: does the explanation still say the right thing? Never weaken the
   check.
3. To revise a question, follow `yr/README.md`, "Change a question". If the page was saved from Colab, run
   `yr/tools/review.sh normalize NB` first.
4. After changing any tool in `yr/tools/`, run `yr/tools/review.sh selftest`.
5. Report which questions were added or changed, and that `review.sh check` passed.
