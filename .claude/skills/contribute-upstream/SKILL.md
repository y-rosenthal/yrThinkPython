---
name: contribute-upstream
description: Send a correction or suggestion to Allen Downey's original Think Python repo the way he actually accepts them (a GitHub issue with the section link and proposed text, not a pull request). Use when asked to report, submit, contribute, or send a fix/typo/error upstream, or to open a PR/issue on AllenDowney/ThinkPython.
user-invocable: true
argument-hint: [chapters/chapNN.ipynb] [--cell N]
---

# Contribute a fix upstream

## How upstream works (verified Sept 2026)

- `AllenDowney/ThinkPython` is a **generated** repo: the chapter notebooks are copied from
  `AllenDowney/ThinkPythonSolutions` (`soln/chapNN.ipynb`) by `chapters/build.sh`, solutions
  stripped, then committed as "Updating the notebooks".
- Every pull request against the notebooks has been **closed without merging** (11 of 11 since
  2024, plus the one PR on the solutions repo). The maintainer replies "Will fix. Thank you!"
  or "fixed in the upstream document and propagated", then makes the change himself.
- Issues get the same response and are the intended channel. So: **open an issue, not a PR.**
  A PR is fine only as an attachment to an issue when the change is large.

## Steps

1. Make sure the fix exists in this fork first (`notebook-conventions` skill), and that the
   fork is current: `git fetch upstream`.
2. Draft the issue body. The script compares the fork's notebook with `upstream/v3` cell by
   cell (matching on cell id), finds the section each changed cell is in, and prints a link to
   that section on the upstream site plus current/suggested text:
   ```bash
   python3 ${CLAUDE_SKILL_DIR}/issue_body.py $ARGUMENTS
   ```
   Keep one issue per distinct problem. Trim the output to the cells that are corrections
   (leave out course-specific edits that upstream should not adopt).
3. Write a one-line title in the style he responds to: `chap18: "is" should be "it" in
   Packing keyword arguments`, or `chap15: time_to_int is called as a function but defined
   as a method`. Say what is wrong and why in a sentence; the script output supplies the rest.
4. Show the title and body to the user, then create the issue **only when they confirm**:
   ```bash
   gh issue create -R AllenDowney/ThinkPython --title "..." --body-file body.md
   ```
   (The `-R` is required: this repo's `upstream` remote makes `gh` default to his repo for
   some commands and the fork for others.)
5. Record the issue URL in the commit message of the fork's fix, e.g.
   `chap18: fix "is/it" typo (reported upstream: AllenDowney/ThinkPython#81)`.

## After he fixes it

The fix arrives through `sync-upstream` as a change to `chapters/chapNN.ipynb`. Upstream's
wording may differ from the fork's; take upstream's version so the fork stops diverging.

## If the user insists on a pull request

The only repo where a PR could be applied directly is `AllenDowney/ThinkPythonSolutions`
(edit `soln/chapNN.ipynb`, the version with solutions). Expect it to be closed and re-applied
by hand, as happened to the previous one. Flow: `gh repo fork AllenDowney/ThinkPythonSolutions
--clone`, branch from `v3`, make the minimal change in `soln/`, push, then
`gh pr create -R AllenDowney/ThinkPythonSolutions --base v3`. Never PR from this fork's `v3`:
it carries the deploy workflow, landing pages and `.claude/`, which upstream must not receive.
