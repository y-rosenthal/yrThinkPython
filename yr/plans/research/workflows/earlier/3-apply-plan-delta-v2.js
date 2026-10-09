export const meta = {
  name: 'apply-plan-delta-v2',
  description: 'Apply the prototype-v2 plan delta to the plan file, then verify completeness and consistency, then fix',
  phases: [
    { title: 'Apply', detail: 'apply every replacement in the delta to the plan file' },
    { title: 'Verify', detail: 'two reviewers: delta fully applied; no stale or contradictory text left' },
    { title: 'Fix', detail: 'fix what the reviewers found' },
  ],
}
const S = '/tmp/claude-0/-home-user-yrThinkPython/6571a165-f8cc-5e43-8b74-c00357a4a6f6/scratchpad'
const PLAN = `${S}/v3main/yr/plans/runall-collapsible-answers.md`
const DELTA = `${S}/v2_delta.md`
const CTX = `Files: the plan file ${PLAN} (a git worktree of branch v3; do NOT commit or push, do not run git commands that change state);
the delta ${DELTA} (written after prototype v2: each "## Replace ..." / "## Add ..." heading says which part of the plan to replace and
gives the new text). Prototype v2 itself: ${S}/ultra/v2/ (out/chap05_review.ipynb, scripts/). The final pushed locations of the two
test notebooks are on branch yr-runall-research: yr/plans/research/prototype-v2/chap05_review.ipynb and errors_A_vs_B.ipynb (ALREADY
PUSHED, with Prof. Rosenthal's go-ahead implied by his testing; Colab links:
https://colab.research.google.com/github/y-rosenthal/yrThinkPython/blob/yr-runall-research/yr/plans/research/prototype-v2/chap05_review.ipynb and
.../prototype-v2/errors_A_vs_B.ipynb). Keep the plan's heading levels (sections are ### N., subsections ####). Keep the plan's style:
short sentences, bullets, VERIFIED/BELIEVED/UNKNOWN labels. Don't delete the "## Colab test results so far" history of the v1 test.`

phase('Apply')
const applied = await agent(`${CTX}
Apply EVERY replacement/addition in the delta to the plan file, in place (edit the file). For partial replacements ("items 4–6",
"Replace in 4.4: ...") replace exactly those parts. Where the delta's instructions are ambiguous, choose the reading that leaves the
plan consistent and note it. Update the top Status/Next-step lines so they say: prototype v2 is pushed and ready for Prof. Rosenthal's
Colab test (Part A2), with the two links. Return a list of every delta item and what you did for it.`,
  { label: 'apply', phase: 'Apply', schema: { type: 'object', properties: { items: { type: 'array', items: { type: 'object', properties: { delta_item: {type:'string'}, action: {type:'string'} }, required: ['delta_item','action'] } }, notes: {type:'array', items:{type:'string'}} }, required: ['items','notes'] } })

phase('Verify')
const ISS = { type: 'object', properties: { issues: { type: 'array', items: { type: 'object', properties: { where: {type:'string'}, problem: {type:'string'}, fix: {type:'string'} }, required: ['where','problem','fix'] } } }, required: ['issues'] }
const reviews = await parallel([
  () => agent(`${CTX}
Apply report: ${JSON.stringify(applied)}
Check that EVERY item in the delta was applied exactly once and correctly (compare text). List anything missing, duplicated or garbled
(e.g. broken headings, broken code fences, duplicated sections).`, { label: 'verify:completeness', phase: 'Verify', schema: ISS }),
  () => agent(`${CTX}
Read the WHOLE updated plan. Find text that is now stale or contradicts the v2 design (e.g. statements that Answers contain the
expected output as text blocks, that run cells show code, that outputs are not stored, that turtle answer pictures are PNGs drawn
by turtle_images for answers, old Part A instructions presented as current, the old run_code managed cell, check rules that no longer
apply, counts that changed). Also check the To do list and Decisions match the new state.`, { label: 'verify:consistency', phase: 'Verify', schema: ISS }),
])

phase('Fix')
const fixed = await agent(`${CTX}
Reviewer issues: ${JSON.stringify(reviews)}
Fix every issue in the plan file (edit in place). Then run a sanity check: all code fences balanced; headings levels as described;
no "## Replace" text leaked into the plan. Return what you changed and anything left.`,
  { label: 'fix', phase: 'Fix', schema: { type: 'object', properties: { changed: {type:'array', items:{type:'string'}}, left: {type:'array', items:{type:'string'}} }, required: ['changed','left'] } })
return { applied, reviews, fixed }