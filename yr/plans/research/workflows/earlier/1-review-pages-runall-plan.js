export const meta = {
  name: 'review-pages-runall-plan',
  description: 'Research, prototype, design and adversarially review a plan for Run-all-safe review pages with collapsible answers',
  phases: [
    { title: 'Research', detail: 'Colab facts, Jupyter facts, repo impact map, working prototype' },
    { title: 'Verify', detail: 'skeptics try to refute the key factual claims' },
    { title: 'Design', detail: 'three independent plans with different priorities' },
    { title: 'Judge', detail: 'panel scores plans; synthesize final plan' },
    { title: 'Critique', detail: 'completeness/feasibility critic, then revise' },
  ],
}

const SCRATCH = '/tmp/claude-0/-home-user-yrThinkPython/6571a165-f8cc-5e43-8b74-c00357a4a6f6/scratchpad'
const CONTEXT = `
CONTEXT (read carefully).
Repo: /home/user/yrThinkPython (a fork of Allen Downey's "Think Python" book, published with Jupyter Book v1 to
https://y-rosenthal.github.io/yrThinkPython/ and opened by students in Google Colab via links like
https://colab.research.google.com/github/y-rosenthal/yrThinkPython/blob/v3/yr/chap05_review.ipynb).
Course "review pages" live in yr/chap02_review.ipynb ... yr/chap07_review.ipynb (six notebooks: 02,03,04,05,06,07).
Format and style rules: yr/README.md (READ IT). Tools: yr/tools/review_cells.py, yr/tools/check_review.py (run via
yr/tools/review.sh check NB), yr/tools/turtle_images.py (review.sh images NB), jb/prep_notebooks.py (process_review: turns
markdown <details><summary>Answer</summary>...</details> cells into MyST dropdown admonitions for the website, drops
'# Your code here' cells), .claude/skills/check-notebooks/check_notebooks.py, .claude/skills/build-book/build_book.sh,
.github/workflows/deploy-book.yml. Skills: .claude/skills/yr-review-page/SKILL.md, .claude/skills/yr-review-questions/SKILL.md.

Current page layout: each question is a markdown heading '### Question N (level): kind', then (for "what is displayed /
drawn / happens" questions) a CODE CELL the student runs, then a markdown <details> Answer (collapsed) with the exact output
in a text block. Write-code questions have a '# Your code here' cell and the solution as markdown python blocks inside the
Answer. Errors-as-answers cells are tagged 'raises-exception'. Some cells (syntax errors, undefined names, wrong calls) were
just changed to run_code("""...""") — run_code is defined in the setup cell as exec(code, globals()) — because Colab's
editor underlines errors (e.g. red squiggles on syntax errors) before running, giving the answer away.

THE PROBLEM THE USER WANTS SOLVED (the user is the course's professor):
 1. Students must be able to use Colab's "Run all" and have it run to the end. Today Colab's Run all stops at the first
    cell that raises (Colab ignores the raises-exception tag, as far as we know).
 2. After Run all, NOTHING visible outside a collapsed Answer may give away an answer. Today, after Run all, every
    question's code cell shows its output (prints, errors, turtle drawings) right under the question = answer revealed.
 3. Students should see the answers (including the real, live output) by clicking the Answer expansion arrow.
 4. The user's idea: make the question plain text (the code shown in markdown) and put the runnable code cell INSIDE the
    answer section. Markdown <details> cannot contain a code cell; notebooks collapse a heading together with all cells
    under it (code cells + outputs), so the Answer would become a heading section saved as collapsed.
 5. Don't Repeat Yourself: avoid authors retyping the question's code in the answer cell. Options floated so far:
    A) code written once in the question markdown; review_cells.py generates the answer run cell; check_review fails if they
       differ (duplicate in file, single source for authors). B) question cell holds code in a string variable q8a="""...""",
       answer cell run_code(q8a) (true runtime DRY, but question code reads as one-color string). C) answer cell reads the
       notebook file (doesn't work in Colab). Other ideas welcome (e.g. a custom cell magic that stores the cell body without
       running it — only viable if Colab's editor does NOT lint/underline cell-magic cells; unknown).
 6. Also already established: run_code can catch the exception and call get_ipython().showtraceback(): the red traceback is
    displayed, the cell's execute_reply status is "ok", and nbclient with allow_errors=False continues (tested).
 7. The website (Jupyter Book) does NOT execute review pages; answers there show the expected output as text blocks and
    turtle pictures stored as PNG data URIs (made by review.sh images). The website must keep working and look good
    (answers collapsed, no stray 'Answer' headings polluting the page's right-hand table of contents, no new Sphinx warnings).
 8. The checks must stay strong: review.sh check verifies every printed output/error appears exactly in the Answer, answer
    python blocks run standalone as .py files, write-code questions show headers + 2 examples, etc. Never weaken checks.

ENVIRONMENT: Python venv with jupyter-book/nbclient/ipykernel: /root/.venvs/yrThinkPython (python 3.13). Python 3.12 venv:
${SCRATCH}/venv312. Pyright CLI: ${SCRATCH}/pr/node_modules/.bin/pyright. jupyturtle.py cached at
/root/.venvs/yrThinkPython/yr-cache/jupyturtle.py. Network: github.com/raw.githubusercontent.com OK; colab.research.google.com
is NOT reachable from this container (use web search / GitHub content instead). WebSearch/WebFetch tools may be available via
ToolSearch.
RULES: Do NOT modify anything under /home/user/yrThinkPython and do not run git commands that change its state (no commit,
checkout, switch, worktree add, stash). Put any experiments under ${SCRATCH}/ultra/<your-label>/ (copy files there first).
Be precise; distinguish VERIFIED (you tested it or saw primary evidence) from BELIEVED. Cite evidence.`

const FACTS = {
  type: 'object',
  properties: {
    facts: { type: 'array', items: { type: 'object', properties: {
      id: { type: 'string' }, claim: { type: 'string' },
      status: { type: 'string', enum: ['verified', 'strong-evidence', 'believed', 'unknown'] },
      evidence: { type: 'string' }, impact: { type: 'string' } },
      required: ['id', 'claim', 'status', 'evidence', 'impact'] } },
    open_questions: { type: 'array', items: { type: 'string' } },
    summary: { type: 'string' },
  },
  required: ['facts', 'open_questions', 'summary'],
}

phase('Research')
const research = await parallel([
  () => agent(`${CONTEXT}

YOUR TASK (label: colab-facts): establish, with evidence, how GOOGLE COLAB behaves on these points. Use web search,
Colab docs/FAQ, googlecolab/colabtools GitHub issues, and REAL Colab-saved .ipynb files on GitHub (raw.githubusercontent.com
is reachable; e.g. find notebooks whose JSON contains "collapsed_sections" — search with the web search tool or GitHub code
search and fetch raw files) to see the exact metadata format. Questions:
 Q1. Does Colab save/restore collapsed heading sections in the .ipynb? Exact format (notebook metadata colab.collapsed_sections?
     which ids — Colab's own cell metadata "id", nbformat 4.5 cell "id", or something else?). Does a notebook opened from GitHub
     that has this metadata open with those sections collapsed?
 Q2. When a section is collapsed, does Run all still execute the cells inside it? Are outputs inside collapsed sections hidden
     until expanded?
 Q3. Does Colab's Run all stop at the first cell whose execution errors? Does it honor the "raises-exception" cell tag? Does a
     cell that catches the exception and calls IPython showtraceback() (status ok) let Run all continue?
 Q4. Colab's editor diagnostics (squiggles): which engine (Pyright? something else)? Do they apply to code inside string
     literals (no?), to markdown (no?), to cells starting with a cell magic like %%bash or an unknown/custom %%magic? Is there a
     per-notebook or per-cell way to disable them (metadata, a comment like "# type: ignore" / "# pyright: ignore", etc.)?
     Note: users can toggle "Show code diagnostics"? find the actual setting name.
 Q5. How does Colab render markdown <details><summary> (works; user screenshot confirms) and does Colab support any other
     "hidden/collapsible code cell" feature: '#@title' forms with hidden code (cellView: form), "Hide code", etc. Could a
     form cell (#@title Answer {display-mode: "form"} with cellView form metadata) hide code but show output, or hide both?
 Q6. Anything else relevant: does Colab show heading-collapse arrows only for markdown headings (#, ##, ###, ####)? Does a
     collapsed section show a count like "3 cells hidden"? Can a section heading be very small/plain?
Return facts with status verified/strong-evidence/believed/unknown and the evidence (URLs, quoted JSON snippets).`,
    { label: 'research:colab', phase: 'Research', schema: FACTS }),

  () => agent(`${CONTEXT}

YOUR TASK (label: jupyter-facts): establish facts about the NON-Colab Jupyter ecosystem and the website toolchain:
 Q1. JupyterLab 4 / Notebook 7: cell metadata for a collapsed heading ("jp-MarkdownHeadingCollapsed": true?) — verify in
     JupyterLab source/docs. Does Run All run cells inside collapsed headings? Does Run All honor the "raises-exception" tag
     (find the JupyterLab PR/issue)? VS Code notebooks: any equivalent?
 Q2. IPython: verify that inside a cell, catching an exception and calling get_ipython().showtraceback() produces an 'error'
     output with the standard red traceback while execute_reply status is 'ok' (test it with nbclient in the venv). Also test
     SyntaxError raised by exec of a string: what does the traceback look like (which frames, does it show the offending line
     and caret)? Compare the visual output for a SyntaxError raised normally vs via exec+showtraceback. Is there a way to hide
     the run_code/exec frame (e.g. showtraceback(exception_only=True) or tb_offset) so it looks like a normal error?
     Save sample outputs (as text) in your scratch dir and report.
 Q3. Jupyter Book v1 / myst-nb (versions in the venv): options to render a markdown heading + following code cell(s) as ONE
     collapsible dropdown on the website; whether a heading in a notebook appears in the page's right-hand "secondary"
     table of contents and how to keep it out (e.g. converting the heading to non-heading markup in prep_notebooks.py, or
     tags like 'remove-cell', 'hide-input', 'hide-cell', 'hide-output'); how cell tags hide-input/hide-cell/remove-input
     render (toggle buttons). Read jb/_config.yml and jb/prep_notebooks.py to see what the site already does.
 Q4. Custom IPython cell magics: can a cell magic (registered in the setup cell with register_cell_magic) receive a body with
     a SyntaxError (yes?) and store it without running? How would such a cell render on the website (prep could strip the
     %%line)? Test it with nbclient.
Return facts with statuses and evidence.`,
    { label: 'research:jupyter', phase: 'Research', schema: FACTS }),

  () => agent(`${CONTEXT}

YOUR TASK (label: repo-map): map the repo impact. Read yr/README.md, all six yr/chap0*_review.ipynb (use a small python
script to list cells: type, tags, first lines), jb/prep_notebooks.py, yr/tools/*.py, check_notebooks.py, build_book.sh,
deploy-book.yml, and the two yr-review skills.
Produce: (1) a table of EVERY question on all six pages: page, number, kind (what is displayed / drawn / happens(error) /
write code / write-code-with-docstring / doctest / refactor / wrong calls with parts / multi-part), which cells it has
(question code cells, definition cells like "Run this cell to define X", raises-exception cells, run_code cells,
'# Your code here' cells, turtle picture placeholders), and whether running its question cell(s) produces visible output
that gives away the answer (prints, errors, drawings, return values displayed as last expression). (2) For each tool,
exactly which functions/assumptions would have to change if answers became heading sections ('#### Answer' markdown
heading + markdown explanation + code cell(s)) and question code moved into markdown — e.g. check_review.groups_of splits on
'### ' headings, is_answer looks for <details>, turtle_images draws pictures for data-turtle placeholders by running "the
question's code cells above", prep_notebooks details_to_dropdown, review_cells add/answer kinds, check_notebooks lint rules.
(3) Subtle cases: questions whose cells DEFINE functions used later (must still run in Run all, in order); questions with
several parts; write-code questions whose examples call the student's function; turtle questions (stored PNG picture vs live
drawing); questions whose "answer" is a docstring/help output; cells that print downloads in setup; the chapter 4 page.
Return facts (claims about the repo, status verified) and a summary that includes the full question table in markdown.`,
    { label: 'research:repo', phase: 'Research', schema: FACTS }),

  () => agent(`${CONTEXT}

YOUR TASK (label: prototype): build and test a WORKING PROTOTYPE of the proposed layout on a COPY, to find practical problems.
 1. Copy the repo (excluding jb/_build and .git) to ${SCRATCH}/ultra/proto/repo (e.g. rsync -a --exclude jb/_build --exclude .git).
 2. Convert yr/chap05_review.ipynb in the copy (by script) to the new layout for at least: Q1 (what is displayed), Q8 (find the
    error, run_code parts), Q14 (infinite recursion, definition cell + error), Q17 (what is drawn, turtle), and one write-code
    question (Q4). New layout: question = heading + markdown with the code in a \`\`\`python block (no runnable question cell,
    except definition cells like "Run this cell to define X" that produce no output); Answer = a markdown heading cell
    (e.g. '#### Answer', or decide something better) followed by the explanation markdown (expected output in text blocks,
    stored turtle PNG) and a code cell that runs the question code (for errors: via run_code that catches and calls
    showtraceback). Mark the Answer headings collapsed for BOTH Colab and JupyterLab using the best-known metadata (Colab:
    notebook metadata colab.collapsed_sections with Colab-style cell metadata ids — check by looking at real Colab-saved
    notebooks on GitHub via raw.githubusercontent.com or web search; JupyterLab: cell metadata "jp-MarkdownHeadingCollapsed": true).
 3. Simulate Colab Run all: execute the converted notebook with nbclient allow_errors=False (must reach the end) and show which
    outputs appear and where.
 4. Website: adapt a COPY of jb/prep_notebooks.py so the Answer heading section becomes one collapsed MyST dropdown (code
    shown as a python block inside, since the site doesn't execute) and the Answer heading does not appear in the secondary TOC;
    then build the book in the copy with the venv (cd copy && source /root/.venvs/yrThinkPython/bin/activate; the build steps
    are in .claude/skills/build-book/build_book.sh — you may run it with --no-exec from the COPY's root; it uses git rev-parse
    for ROOT, so if that fails because the copy has no .git, run the steps by hand: copy notebooks into jb/, python
    prep_notebooks.py, jb build .). Inspect jb/_build/html/yr/chap05_review.html: answers collapsed? stray headings? warnings?
    Take a headless screenshot with /opt/pw-browsers/chromium-1194/chrome-linux/chrome --headless --no-sandbox --screenshot.
 5. Try the DRY options concretely on Q8: (A) generator that copies question markdown code into the answer cell; (B) string
    variable; (C') custom cell magic %%question that stores the body (check rendering & whether Pyright flags it — Pyright
    doesn't understand magics, so just report). Report pros/cons observed.
Return facts (status verified for things you ran), problems found, and file paths of the prototype/screenshot.`,
    { label: 'research:prototype', phase: 'Research', schema: FACTS }),
])
const [colab, jupy, repo, proto] = research
const researchText = JSON.stringify({ colab, jupyter: jupy, repo, prototype: proto }, null, 1)
log(`research done: ${research.filter(Boolean).length}/4 agents returned`)

phase('Verify')
const VERDICTS = {
  type: 'object',
  properties: {
    verdicts: { type: 'array', items: { type: 'object', properties: {
      fact_id: { type: 'string' }, claim: { type: 'string' },
      verdict: { type: 'string', enum: ['confirmed', 'plausible', 'doubtful', 'refuted'] },
      reasoning: { type: 'string' } }, required: ['fact_id', 'claim', 'verdict', 'reasoning'] } },
    overall_risks: { type: 'array', items: { type: 'string' } },
  },
  required: ['verdicts', 'overall_risks'],
}
const lenses = [
  'Colab behavior (collapsed_sections format and whether it is honored on open, Run all semantics, diagnostics/linting scope, form cells). Try to REFUTE each Colab claim with independent evidence (web search, real Colab-saved notebooks on GitHub). Default to doubtful when evidence is indirect.',
  'Jupyter/IPython/Jupyter Book claims (showtraceback status, exec SyntaxError tracebacks, JupyterLab metadata and Run All, myst-nb rendering, secondary TOC). Re-run small tests yourself in ${SCRATCH}/ultra/verify-jupyter/ to confirm or refute.',
  'Repo-impact and prototype claims: re-check them against the actual files and the prototype outputs in ' + SCRATCH + '/ultra/proto/. Look for anything that would break the checks, the website build, turtle pictures, or the authoring workflow that the research missed.',
]
const verify = await parallel(lenses.map((lens, i) => () => agent(`${CONTEXT}

You are a SKEPTICAL VERIFIER. Lens: ${lens}
Here are the research findings (JSON):
${researchText}

For every fact relevant to your lens, give a verdict (confirmed only if you independently verified it or saw primary
evidence). List overall risks the plan must handle.`, { label: `verify:${i + 1}`, phase: 'Verify', schema: VERDICTS })))
const verifyText = JSON.stringify(verify, null, 1)

phase('Design')
const PLAN = {
  type: 'object',
  properties: {
    title: { type: 'string' },
    plan_markdown: { type: 'string' },
    assumptions_needing_colab_test: { type: 'array', items: { type: 'string' } },
    dry_choice: { type: 'string' },
  },
  required: ['title', 'plan_markdown', 'assumptions_needing_colab_test', 'dry_choice'],
}
const angles = [
  'STUDENT-EXPERIENCE FIRST: what a student sees in Colab (before and after Run all), in JupyterLab, and on the website; readability of question code; minimal confusion; how answers reveal live output.',
  'MAINTAINABILITY / DRY FIRST: authoring workflow for the professor and future Claude sessions (review_cells.py spec format, a single source of truth for each question code, generators, checks that enforce invariants), minimal special cases, clear README rules.',
  'RISK / VERIFIABILITY FIRST: what can be verified here vs only in Colab; fallbacks if Colab ignores collapsed metadata or lints magics; a staged rollout (one page first, user tests in Colab with a precise checklist), keeping the website and checks green at every step, rollback.',
]
const plans = await parallel(angles.map((angle, i) => () => agent(`${CONTEXT}

RESEARCH FINDINGS:
${researchText}

SKEPTIC VERDICTS (trust these over the raw findings where they disagree):
${verifyText}

Write a complete, concrete implementation PLAN. Priority angle: ${angle}
The plan must cover: final page layout for each question kind (what is displayed/drawn/happens, errors, multi-part, wrong
calls, definition cells, write code, doctest, turtle); exactly how answers collapse in Colab/JupyterLab/website; the DRY
mechanism; run_code (catch + showtraceback; how the traceback looks); changes to each tool (review_cells.py, check_review.py,
turtle_images.py, prep_notebooks.py, check_notebooks.py), README and both skills; how to convert the six existing pages (script,
keep cell ids where possible); verification steps here; the precise Colab test checklist for the professor; rollout order;
open decisions for the professor (with a recommendation each). Be specific (file/function names, metadata JSON). Don't
pretend unverified Colab behavior is certain.`, { label: `plan:${i + 1}`, phase: 'Design', schema: PLAN })))

phase('Judge')
const SCORES = {
  type: 'object',
  properties: {
    scores: { type: 'array', items: { type: 'object', properties: {
      plan_index: { type: 'number' }, correctness: { type: 'number' }, student_experience: { type: 'number' },
      maintainability: { type: 'number' }, risk_handling: { type: 'number' }, total: { type: 'number' },
      strengths: { type: 'string' }, weaknesses: { type: 'string' } },
      required: ['plan_index', 'correctness', 'student_experience', 'maintainability', 'risk_handling', 'total', 'strengths', 'weaknesses'] } },
    best_ideas_to_graft: { type: 'array', items: { type: 'string' } },
  },
  required: ['scores', 'best_ideas_to_graft'],
}
const plansText = plans.map((p, i) => p ? `=== PLAN ${i} (${p.title}) ===\n${p.plan_markdown}\nColab assumptions: ${JSON.stringify(p.assumptions_needing_colab_test)}\nDRY: ${p.dry_choice}` : `=== PLAN ${i}: missing ===`).join('\n\n')
const judges = await parallel(['correctness against the verified facts and the repo', 'the professor\'s stated goals (Run all to the end; nothing revealed outside collapsed answers; answers with live output by clicking; DRY)', 'simplicity and long-term maintainability'].map((focus, i) => () => agent(`${CONTEXT}

VERIFIED/REFUTED FACTS:
${verifyText}

PLANS:
${plansText}

Judge each plan (scores 1-10) with emphasis on ${focus}. List the best ideas to graft into the winner.`, { label: `judge:${i + 1}`, phase: 'Judge', schema: SCORES })))

const synth = await agent(`${CONTEXT}

RESEARCH: ${researchText}
VERDICTS: ${verifyText}
PLANS: ${plansText}
JUDGES: ${JSON.stringify(judges, null, 1)}

Synthesize ONE final plan: start from the highest-scoring plan and graft the best ideas. Resolve conflicts explicitly. It
will be shown to the professor (non-specialist in Jupyter internals) and then executed by Claude. Structure: 1) What students
will see (Colab before/after Run all, website) 2) Page layout per question kind with a tiny example 3) DRY mechanism
4) Tool/README/skill changes 5) Conversion of the six pages 6) Verification here 7) Colab test checklist for the professor
(numbered, concrete) 8) Rollout (one page first) 9) Decisions needed from the professor, each with a recommendation
10) Known uncertainties and fallbacks. Be concrete and honest about what is unverified.`, { label: 'synthesize', phase: 'Judge', schema: PLAN })

phase('Critique')
const CRIT = {
  type: 'object',
  properties: {
    blocking_issues: { type: 'array', items: { type: 'string' } },
    gaps: { type: 'array', items: { type: 'string' } },
    wrong_or_unverified_claims: { type: 'array', items: { type: 'string' } },
    suggested_edits: { type: 'array', items: { type: 'string' } },
  },
  required: ['blocking_issues', 'gaps', 'wrong_or_unverified_claims', 'suggested_edits'],
}
const critiques = await parallel([
  'COMPLETENESS: every question kind on all six pages handled? every tool and doc updated? website, checks, turtle pictures, Python 3.12/3.13, JupyterLab, Colab all covered? anything the professor asked for missing?',
  'FEASIBILITY/CORRECTNESS: would each step actually work given the verified facts and the prototype? any claim stated as certain that is not verified? any step that would weaken the checks or break the build?',
].map((lens, i) => () => agent(`${CONTEXT}

VERDICTS: ${verifyText}
PROTOTYPE/RESEARCH: ${researchText}

FINAL PLAN TO CRITIQUE:
${synth ? synth.plan_markdown : 'MISSING'}

Critique it through this lens: ${lens}`, { label: `critic:${i + 1}`, phase: 'Critique', schema: CRIT })))

const final = await agent(`${CONTEXT}

FINAL PLAN DRAFT:
${synth ? synth.plan_markdown : 'MISSING'}

CRITIQUES:
${JSON.stringify(critiques, null, 1)}

VERDICTS: ${verifyText}

Revise the plan to fix every blocking issue and gap, and correct every wrong/unverified claim (mark unverified ones as such).
Keep the same 10-section structure. Keep it readable for the professor: concise, concrete, no filler.`, { label: 'revise', phase: 'Critique', schema: PLAN })

return { final, synth_title: synth && synth.title, judges, verify, research: { colab, jupy, repo, proto }, critiques }