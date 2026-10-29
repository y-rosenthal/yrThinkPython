---
name: yr-additions-page
description: Create or change a "NNb. Prof. Rosenthal's Additions" page (yr/chapNN_additions.ipynb) - material that a Think Python chapter uses but does not explain, with examples and practice questions on the page - and put it before the chapter's review page (which becomes NNc). Use when asked to add missing material, extra explanations, "additions", or a topic the book does not cover, for a chapter, without changing Downey's chapter.
user-invocable: true
argument-hint: [chapter number] [topics]
---

# Create or change an additions page

The rules are in `yr/README.md`: "The pages of a chapter", "Additions pages" (layout, style rules) and
"Adding an additions page" (the steps). Read these sections first, and follow them. Do not repeat a rule here:
if a rule is missing or wrong, change `yr/README.md`.

Do not change Downey's chapter (`chapters/chapNN.ipynb`). Work on a topic branch, not `v3`. Leave committing
and pushing to the user unless asked. A second additions page for a chapter needs Prof. Rosenthal's agreement
first (`yr/README.md`, "Additions pages").

## Steps for the agent

1. Read every cell of `chapters/chapNN.ipynb`
   (`python3 .claude/skills/notebook-conventions/nb_cells.py chapters/chapNN.ipynb`, then `--full`), and
   the reference examples named in `yr/README.md`.
2. Make or edit the notebook with a small `json` script or the NotebookEdit tool (never `sed` on the JSON),
   with the layout and the style rules of `yr/README.md`.
3. Add the page to the site and verify it: `yr/README.md`, "Adding an additions page", steps 3 and 4.
4. Report to the user what was added, what was verified, and what was not verified (for example, how the page
   looks in Colab, which needs the notebook on GitHub).
