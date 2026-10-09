# Notes for Claude

## Where things are

- `yr/README.md`: the course's review pages (`yr/chapNN_review.ipynb`), their style rules and tools.
- `yr/tools/`: the review-page tools. `review.sh sync` writes outputs, pictures and values by running
  the code on the pinned Colab-like kernel; `review.sh check` verifies a page; `review.sh selftest`
  tests the tools; `review_format.py` defines the page format.
- `author-guide/CONTENT-AUTHOR-GUIDE.qmd`: the guide for content authors (Quarto book). Update it in the same
  change as `yr/README.md` and the review skills.
- `.claude/skills/`: skills for building, checking, publishing and syncing the book
  (for example `yrpublish`, `yr-review-page`, `yr-review-questions`).
