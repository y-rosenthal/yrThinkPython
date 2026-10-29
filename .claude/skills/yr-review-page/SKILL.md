---
name: yr-review-page
description: Create a "NNb. Prof. Rosenthal's Review" page (NNc when the chapter has an additions page) for a Think Python chapter (yr/chapNN_review.ipynb, a concepts checklist plus practice questions with collapsible answers) and add it to the site, or write/revise the "Concepts covered" summary of an existing review page. Use when asked for a review page, chapter summary, fact list, concepts checklist or study guide for a chapter.
user-invocable: true
argument-hint: [chapter number] [concepts-only]
---

# Create a review page (or its concept summary)

The rules are in `yr/README.md`, "Review pages": the layout, the **style rules** (they are Prof. Rosenthal's
instructions; follow them exactly), "Adding a question", "Markers", and the steps in "Adding a review page for
another chapter". Read them first, and read the reference example that `yr/README.md` names. Do not repeat a
rule here: if a rule is missing or wrong, change `yr/README.md`.

Work on a topic branch, not `v3` (`git switch -c yr-review-chNN`); leave committing and pushing to the user
unless asked.

## Steps for the agent

1. Follow `yr/README.md`, "Adding a review page for another chapter". Read the chapter with
   `python3 .claude/skills/notebook-conventions/nb_cells.py chapters/chapNN.ipynb` (then `--full` for the
   cells you need). Edit cells with the NotebookEdit tool or a small `json` script (never `sed` on the JSON);
   never edit the template cells by hand (`yr/README.md`, "Layout of a page").
2. For the questions, follow the `yr-review-questions` skill.
3. For a "concepts-only" request (revise the summary of an existing page): write or revise the two Concepts
   lists only, then run the verification of the last step.
4. Report to the user what was added, what was verified, and anything not verified (for example, how the
   page looks in Colab, which needs the notebook on GitHub).
