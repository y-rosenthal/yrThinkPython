# Notes for Claude

## Pending work: tell the user at the start of every session

The review pages' new format (Colab's "Run all" works; answers hidden until clicked) is finished on branch
`yr-review-runall`: the tools and all six converted pages, verified. It is **not published**: merging it into `v3` and
pushing deploys the site, so Prof. Rosenthal does that (or gives permission). The plan, its to-do list and what is
left (publish, check the live site, Colab spot checks, one open decision) are in
`yr/plans/runall-collapsible-answers.md` (the Status line at the top). At the start of a session, tell the user in one
or two lines where this stands and ask whether to continue.

When that work is finished, delete this section.

## Where things are

- `yr/README.md`: the course's review pages (`yr/chapNN_review.ipynb`), their style rules and tools.
- `yr/tools/`: the review-page tools. `review.sh sync` writes outputs, pictures and values by running
  the code on the pinned Colab-like kernel; `review.sh check` verifies a page; `review.sh selftest`
  tests the tools; `review_format.py` defines the page format.
- `.claude/skills/`: skills for building, checking, publishing and syncing the book
  (for example `yrpublish`, `yr-review-page`, `yr-review-questions`).
