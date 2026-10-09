# Workflow scripts

Multi-agent workflow scripts (for Claude Code's Workflow tool) used to plan the "Run all" redesign of the review pages.
See `yr/plans/runall-collapsible-answers.md` on branch `v3` for the plan they feed.

## `dry-generated-answers-audit.js` (portable; completed 2026-10-09, results in `../dry-audit/`)

Audits every question on the six review pages for text typed twice (goal 9) and answers typed by hand instead of produced
by running code (goal 10), runs every hand-typed example output and quoted value to find wrong ones, and designs a layout
that meets goals 9-11, with three designs, three judges and a critic. It was started in the cloud session on 2026-10-09
and stopped when Prof. Rosenthal moved to his laptop.

To run it on another computer:

1. In a checkout of this repo on branch `v3`, make a checkout of this research branch next to it:
   ```bash
   git fetch origin yr-runall-research
   git worktree add ../yrThinkPython-research origin/yr-runall-research
   ```
2. Make sure the book's venv exists: `source .claude/skills/build-book/ensure_venv.sh`.
3. Start Claude Code in the repo root and ask it to run the workflow script
   `../yrThinkPython-research/yr/plans/research/workflows/dry-generated-answers-audit.js`
   (Workflow tool, `scriptPath`). Optional args: `{"research": "...", "work": "..."}` if the folders differ from
   `../yrThinkPython-research` and `../yrThinkPython-work`.
4. When it finishes, save its result (the `final` answer, `audits`, `designs`) into `yr/plans/research/` on this branch,
   and bring the answer and decisions to Prof. Rosenthal.

The agents only read the repo and write in `../yrThinkPython-work/`.

## `earlier/`

The three workflows that already ran in the cloud session, kept for reference. Their paths point to that session's
temporary folders, so they don't run elsewhere as they are; their results are already saved in `yr/plans/research/`.

1. `1-review-pages-runall-plan.js`: research, prototype, three plans, judges, critics, final plan (`revise.md`).
2. `2-review-pages-prototype-v2.js`: prototype v2 after the first Colab test (results in `v2-workflow/`, `prototype-v2/`).
3. `3-apply-plan-delta-v2.js`: applied the v2 changes to the plan file.
