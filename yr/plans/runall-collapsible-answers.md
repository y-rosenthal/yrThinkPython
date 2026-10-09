# Plan: review pages that work with Colab's "Run all", with answers hidden until clicked

**Status (2026-10-09): the DRY audit (goals 9-11) is done and Prof. Rosenthal has decided E1–E20 (section "DRY audit and decisions E1–E20" below). The design is now "v2 plus a sync step that fills markdown": the author types each fact once and `review.sh sync` generates every output, header, import, error name and quoted value. The design summary and sections 1–5 were rewritten for it (v3) the same day, with variant B errors, run-cell titles that name the question and Python 3.13; section 9 says which old decisions are settled. Sections 6–8 and 10 are still v2's and get revised in Step 3. Nothing of the new format is implemented yet; the one live change is that question numbers stay fixed (`3b` inserts).**

**Next step:**
1. Done 2026-10-09 (see "Colab test results so far"): Claude ran Part A2 and DRY tests 1-4 in Prof. Rosenthal's Chrome. Prof.
   Rosenthal then chose variant B, run-cell titles that name the question, and the help note as is.
2. Done 2026-10-09: sections 1–5 rewritten (v3); section 9 restated.
3. Done 2026-10-09: the C4 prototype passes on all 11 fix blocks (results in section 4.4).
4. Done 2026-10-09: all of D1–D18 decided (section 9).
5. Next: Step 2 (update `make_smoke.py` to v3 and run the smoke test), then Step 3 (build the tools).

The two prototype v2 notebooks for Part A2:
- Chapter 5 review page: https://colab.research.google.com/github/y-rosenthal/yrThinkPython/blob/yr-runall-research/yr/plans/research/prototype-v2/chap05_review.ipynb
- Errors, variant A vs B: https://colab.research.google.com/github/y-rosenthal/yrThinkPython/blob/yr-runall-research/yr/plans/research/prototype-v2/errors_A_vs_B.ipynb

The review pages that are live today (2b–7b) are complete and working; this plan changes how
their questions and answers are laid out. Early research notes:
[runall-research-notes.md](runall-research-notes.md). Everything else the research produced (each
agent's report, the three candidate plans, the judges, the critics, the prototype and the helper
scripts) is on branch `yr-runall-research` in `yr/plans/research/`.

## To do

Step numbers refer to section 8 of the plan below.

- [x] Finish the plan (research, prototype, review) and write it into this file (Step 0)
- [x] Step 1a: Prof. Rosenthal ran Part A on prototype v1 (results below): Run all OK; Answers too repetitive
- [x] Step 1b: prototype v2 built (each output shown once, code hidden, outputs stored); three reviews; all blocking and major issues fixed
- [x] Step 1c: push prototype v2 (2 files) to `yr-runall-research` (2026-10-08)
- [x] Step 1d, the test part: Part A2 run in Colab by Claude in Prof. Rosenthal's Chrome (2026-10-09; results below)
- [x] Step 1d, A2 decisions: variant B, run-cell titles name the question, help note as is (2026-10-09)
- [x] Prof. Rosenthal decided the rest of D1–D18 (2026-10-09: all as recommended)
- [x] DRY audit for goals 9-11 (17-agent workflow, run on the laptop 2026-10-09; results on `yr-runall-research` in
      `yr/plans/research/dry-audit/`, commit ad089b6)
- [x] Prof. Rosenthal decided E1–E20 (2026-10-09; `dry-audit/decisions.md`, commit 9d4f4ee; summarized below)
- [x] DRY Colab tests 1-4 (2026-10-09; results below): E12 works with one rule, E13 confirmed (1000), E18 needs Python 3.13
- [ ] DRY Colab tests 5-7 and the site-build diff, once a converted page exists
- [ ] Move `colablike.lock` to Colab's Python 3.13.16 (IPython 7.34.0, ipykernel 6.17.1 unchanged) and re-sync (E18)
- [x] Rewrite the design summary and sections 1–5 for E1–E20 (v3), and restate section 9's D1–D18 (2026-10-09)
- [x] Live now: question numbers stay fixed during a semester (`review_cells.py` accepts `3b`; README and skills say so; 2026-10-09)
- [ ] Revise sections 6–8 and 10 (verification, checklists, rollout, uncertainties) for v3, with Step 3
- [x] Prototype check C4 on the 11 fix blocks (2026-10-09): all 11 pass trimmed, and 3 negative tests fail as they must
      (`yr/plans/research/c4-prototype/` on `yr-runall-research`). E5 is confirmed
- [ ] Fix the problems the audit found (list in the DRY audit section): ch05 "about 3000" frames (E13), the v2 converter's
      leftover sentences, the check gaps
- [x] Save the prototype v2 files the checkpoint skipped (lock file, shell scripts, `v2fix_exp/` experiments) to
      `yr-runall-research` under `yr/plans/research/v2-workflow/` (2026-10-08, commit 632e55e)
- [ ] Step 2: update `make_smoke.py` to v2 (Part B lists the changes and drops the tests v1 and A2 settle); with his
      OK, push `colab-smoke-test`; he runs checklist Part B; adjust the plan if the results call for it
- [ ] Step 3: build the new tools (`review_format.py`, `sync_review.py`, new `check_review.py`, `turtle_images.py`,
      `ensure_colab_venv.sh` and `colablike.lock`, `prep_notebooks.py` guard, self-test), keeping old pages working
- [ ] Skills: update `yr-review-questions` and `yr-review-page` so every question with an error, or with output
      that must stay hidden, is written the same way (goal 7; Step 3)
- [ ] Human guide: "Adding a question: a guide for people" near the top of `yr/README.md`, pointing to the
      skills and tools (goal 8; Step 3)
- [ ] Step 4: convert chapter 5 only; Prof. Rosenthal runs checklist Part C from the branch link
- [ ] Step 5: publish chapter 5 and verify the live page
- [ ] Step 6: convert ch02, ch03, ch06, ch07, then ch04, each with a Colab spot-check
- [ ] Step 7: check on the live pages that each problem Prof. Rosenthal reported is gone (goal 6), remove the
      legacy code, add the CI lint step, delete the "Pending work" note from `CLAUDE.md`, mark this plan done

## Colab test results so far

**2026-10-09, prototype v2 (Part A2) and DRY tests 1-4**, run by Claude in Prof. Rosenthal's Chrome (Claude in Chrome
extension). Full table and screenshots: `yr/plans/research/dry-audit/colab-tests/` on `yr-runall-research`
(`results-2026-10-09.md`, `screens/`). VERIFIED:
- **Colab's stack is Python 3.13.16**, IPython 7.34.0, ipykernel 6.17.1, not Python 3.12 as this plan assumed. `colablike.lock`
  must move to 3.13 (E18). Consequence: ch04 Q15c's "Did you mean 'sides'?" **does** appear in Colab, so section 9's D17
  (accept the 3.12 output) is reversed; today's page text already matches Colab.
- **E12 markers work mid-sentence** (also in bold, bullets, two per line and inside a collapsed Answer), **but a marker at the
  very start of a line breaks that whole line** (rendered as raw HTML, backticks visible). Rule: a value marker never starts a
  line or list item; check enforces it. Block comments on their own line are invisible everywhere (T2).
- **Recursion limit is 1000** (depth 977), as locally: ch05's "about 3000" and the book's "almost 3000" are wrong for Colab (E13).
- help() layout, float reprs and the ch04 Q15a SyntaxError text are the same as locally.
- **A2 passes:** Answers closed on opening (Q1 "2 cells hidden", Q8 "7 cells hidden"); question code coloured; Q1's output once,
  under the title "Output" and a "Show code" link, no code; Q8 in order with `/tmp/ipykernel_0/….py", line 2` headers and no
  `<!-- error` text; Q17's tree at 300×220; Run all reaches the end with Answers closed and nothing outside them but
  "Downloaded jupyturtle.py"; Q8 and Q14 re-run (Q14 still `<cell line: 0>`, "last 1 frames repeated"); Q9's code cell runs.
- **Two A2 findings:**
  - **A red run icon appears on a CLOSED Answer row after Run all** when the Answer holds an error cell (seen on Q14). It tells
    students the answer is an error before they open it. Variant B (traceback as text) would avoid it, since nothing raises.
  - **"Output" entries do appear in the contents sidebar**, under an Answer once it is opened and under every Answer with a run
    cell after Run all. The plan's response: an empty title, or one that names the question.
- Run all took under 10 s, but the runtime was already connected (a Terminal panel opened by accident), so a cold start was not
  timed.
- **Prof. Rosenthal chose variant B (2026-10-09)**: error answers show the traceback as plain text, so nothing is flagged and no red icon appears on closed Answers. This settles section 9's D15 (B: a hidden helper cell again; checks read the error from text; failing-import test in Part B).
- **Run-cell titles (decided 2026-10-09):** name the question, e.g. "Output of Question 8a" (generated by sync; updated by `review.sh renumber`, E16). Supersedes section 9's D16.
- **Help note (decided 2026-10-09):** keep the prototype v2 wording as is (A2-7).
- **Earlier open items, now decided:** variant A or B (B) (screenshots `a2-6-variant-A-after-runall.jpg`, `a2-6-variant-B-after-runall.jpg`),
  the run-cell titles, and the help note's wording (A2-7).

**2026-10-08, prototype v1** (chapter 5 from `yr-runall-research`; Run all, then Answers opened). VERIFIED from his screenshots:
- **Run all does not stop at a caught error (variant A works in Colab).** The page's 21 code cells ran in order: Q2's cell [3], Q8's three error cells [9] [10] [11], and Q1 re-run as [22]. This settles test B4 for variant A.
- **Q8's line numbers were right.** Each traceback read `File "/tmp/ipykernel_2148/445721521.py", line 2`, and line 2 is where each part's mistake is. The newline after `r"""` does not shift line numbers: IPython drops leading blank lines (VERIFIED on 7.34 and 9.17). 445721521 is ipykernel's hash of part a's code, and v2 stores the same file name.
  - The first version of this entry called these headers "off by one". That was a misreading.
- **Problem: repetition** (Q1, Q2). Each Answer showed the expected output as text, then the question's code again, then the same output live.
- **Problem: Q8 "not exactly right".**
  - The run cells were bunched at the end of the Answer.
  - The `run_code("""…""")` wrapper and a string-coloured body were visible.
  - Each error was shown twice.
  - Each error had a red (!) icon and a "Next steps: Explain error" button.

**Response: prototype v2** (see "The design in one paragraph"):
- **Fixed:** the repetition (each output shown once), the visible wrapper (code hidden) and the bunching (parts interleaved).
- **Not fixable in the page with variant A:** Colab's icon and button after Run all. Part A2 shows him variant B on the same day (D15).
- **Pushed 2026-10-08,** not yet tested in Colab: Part A2 (section 7).

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

9. **Typed once, everywhere (2026-10-09).** "I really want a DRY approach - Don't Repeat Yourself. You should really avoid
   typing the same text for the question twice." This covers more than question code: helper functions, example calls, headers and
   anything else an author would otherwise type twice.
10. **Answers generated by running the code, not hardcoded (2026-10-09).** "I don't want the answer hardcoded, rather generated by
    running the code." This covers outputs, errors and drawings, and also example outputs in "write code" questions and values
    quoted in explanations. Where something can't be generated (prose), the plan must say so and say how it is kept correct.
    An audit of every question against goals 9-11 was started in the cloud session (workflow wf_d7f38dd1-6fa), stopped, and
    run to the end on Prof. Rosenthal's laptop on 2026-10-09 (workflow wf_8b89496c-710). Its script is on branch
    `yr-runall-research` at `yr/plans/research/workflows/dry-generated-answers-audit.js`; its results are summarized in the
    section "DRY audit and decisions E1–E20" below.
11. **Answer code a student can copy and run (2026-10-09; replaces the "runs as a standalone .py file" rule).** "I don't need each
    Answer code block to be an actual .py file. I just mean that if a student copies the Answer from the rendered page, that the
    student should be able to run the code. However, helper functions that are provided don't need to be in the answer if they are
    already in the question. I'm just trying to avoid the issue where weaker students miss things like imports." So an Answer's code
    includes its own imports, and leaves out helpers the question provides. Those helpers must really be defined in the notebook, so
    helpers shown today only as text in a question become a runnable "Run this cell to define ..." cell, typed once.
12. **Question numbers stay fixed during a semester (2026-10-09).** Homework is assigned by number. "I might have told student to do
    question 5. Then I might want to add a new question to the website between questions 3 and 4. I don't want that to modify
    question 5's number to be 6. I would rather number the new question as 3b." But: "Every semester I teach the course, I would
    like to start clean with questions 1,2,3,4,5,6, etc." So no tool renumbers questions on its own; a deliberate command run
    between semesters does (E16).

## DRY audit and decisions E1–E20 (2026-10-09)

Full results on branch `yr-runall-research` in `yr/plans/research/dry-audit/`: `final.md` (the answer), `decisions.md`
(Prof. Rosenthal's decisions, quoting Prof. Rosenthal where a recommendation was changed), `result.json` (every agent's result) and
`work/` (the agents' scripts and prototypes: `design-1/`, `design-2/`, `design-3/`, `verify-examples/`, `prose-claims/`, ...).
In those files the decisions are numbered D1–D20; here they are **E1–E20**, so they don't clash with section 9's D1–D18.

**Findings (counts across the six pages).** v2 meets goals 9 and 10 only for "what is displayed / what happens / find the error"
questions (82 outputs generated). Still typed twice or by hand in v2: 30 write-code headers (each typed 2-4 times), 145 example-call
lines repeated in 57 Answer blocks, about 52 example outputs, provided helpers (ch04 `jump` typed 7 times), fixes that retype the
question (ch07 Q14: 19 lines to change one word), 275 values quoted in prose, and 24 new hidden error records that v2 adds.
All 86 hand-typed example outputs are correct today; of 264 checkable prose values, 263 are correct.

**The design (E1).** v2 plus one `review.sh sync` step that fills markdown (the audit's design-3), with design-1's generators;
design-2 (`%%question` cell magics) only as a fallback. The author types each fact once: question code, each helper, the
solutions, each example call, each fix, and the expression behind each quoted value. `sync` writes every output, header, import
line, error name and quoted value; `check` fails if running `sync` again would change anything.

| | Decision | |
|---|---|---|
| E1 | Base design: v2 + sync fills markdown, with design-1's generators; design-2 only as fallback | as recommended |
| E2 | Example outputs (write-code, "Two correct ways", help()) generated by sync; the author types only the calls | as recommended |
| E3 | check runs **every** python block in an Answer against every example (a block that redefines only some functions is checked against those functions' examples); all must agree. A block that is not a full solution is marked `<!-- not a solution -->` (today only ch06 Q17's halfway version) and its own output is still generated | **changed**: was "first block is the reference" |
| E4 | "Start from this header" block generated from the solutions' def lines, today's look kept; `<!-- header: f g -->` overrides | as recommended |
| E5 | Answer code trimmed (no example calls, example inputs or provided helpers); imports generated; check C4 runs each block after Run all with the setup imports removed and fails on a silent doctest failure | as recommended, after the C4 prototype |
| E6 | Provided helpers: a runnable definition cell where first provided; generated "uses X from Question N" pointers later | as recommended |
| E7 | ch04 `describe` kept in both Q5 and Q15; check confirms the copies match | as recommended |
| E8 | v2's hidden `<!-- error: X -->` records dropped; the visible error name is generated (`<!--=error-->`) | as recommended |
| E9 | One-word fixes in long functions (ch07 Q14, ch05 Q14, ch05 Q10 approach 2) use a derive marker; other fixes show only the changed lines | as recommended |
| E10 | A fix that uses a name a later question reassigns keeps its own input line (ch02 Q4 `price = 4`); lint lists names assigned by more than one question | as recommended |
| E11 | **All** "what if" claims become small variant blocks with generated output or pictures, drawings included (e.g. "`left(144)` draws a flipped star") | **changed**: drawings were to stay prose |
| E12 | Values in prose: `` `EXPR` is <!--=-->`?` `` and `<!--= EXPR -->` markers, added claim by claim with a render-diff gate; cell metadata instead if Colab shows inline comments | as recommended, pending a Colab test |
| E13 | ch05 "about 3000" frames: "about N (depends on the environment)", N generated from `sys.getrecursionlimit()`; if Colab also gives 1000, report the book's "almost 3000" upstream as an issue | as recommended, pending a Colab test |
| E14 | Concepts entries that overlap a question stay (Concepts stands alone), with generated values; delete ch04's repeated jupyturtle paragraph in the Questions intro and the facts listed twice in ch02 Concepts | as recommended |
| E15 | Page frame (title, intro, credits, download(), setup and "Run this cell to define" sentences) generated from one template | as recommended |
| E16 | Question numbers are typed and **stable**; sync never renumbers. An inserted question is "3b"; check refuses a "3b" that clashes with a "Part b" in Question 3, and checks uniqueness and "from Question N" pointers. A deliberate command between semesters (`review.sh renumber`) renumbers 1, 2, 3, ... and fixes pointers (goal 12) | **changed**: was "renumber on every sync" |
| E17 | Generated text sits inside the author's cells, between delimiters sync writes; check reports a hand edit before sync would overwrite it | as recommended |
| E18 | sync and check generate only on the pinned `colablike.lock` stack | as recommended, pending a Colab test |
| E19 | A trimmed Answer gets a generated "Then try: `f(...)`" line from the examples | as recommended |
| E20 | Extend `jb/prep_notebooks.py` and `verify_site.py` for the markers, delimiters and helper cells; each converted page passes a diff gate (local site build, rendered page before vs after) | as recommended |

**Problems the audit found** (details in `final.md` section 3):
- ch05 Concepts says "about 3000" frames; locally the limit is 1000 (E13). The number comes from the book (`chapters/chap05.ipynb`).
- v2 converter: the stale "defines `run_code`" intro sentence on ch02, ch03, ch04, ch07; lead-in sentences left dangling where a text
  block was removed (ch03 Q10a, Q14; ch04 Q2, Q7, Q14, Q15; ch07 Q14); ch02 Q10's run cells rely on the setup cell's `import math`.
- Check gaps: check_v2 S13 checks a block with no text block after it by exit code only, and a failing doctest exits 0; no check
  compares write-code example outputs with a solution.
- False alarms in `verify_removed.py` (ch03 Q9, ch07 Q1) and check_v2 S18 (ch07 Q8).
- Unused imports in some ch04 Answer blocks (generated imports fix this).

**DRY Colab tests** (in addition to Part A2):
1. Inline comments: `` `-7 // 2` is <!--=-->`-4` `` mid-sentence renders with no stray text and an intact code span (decides E12).
2. Block comments (`<!-- not a solution -->`, `<!-- header: f -->`, `<!-- derive: ... -->`, region delimiters) are invisible.
3. `sys.getrecursionlimit()` and where a deep recursion stops (E13).
4. Colab's Python/IPython versions vs the stored outputs: error wording (ch04 Q15c), help() layout (ch04 Q12), float reprs (E18).
5. Run all on a converted page with the new definition cells reaches the end, and the NameError answers (ch02 Q9, ch04 Q7, ch07 Q8)
   don't change.
6. Copy-and-run: trimmed Answer blocks pasted after Run all run correctly (ch02 Q4 must show `8`, not `19.9919.99`).
7. Out-of-order click: a run cell clicked before the setup cell (ch02 Q10).
8. Local, not Colab: build the site from a converted page and diff it (E20).

## What is live now (for context)

- Six review pages: `yr/chap02_review.ipynb` ... `yr/chap07_review.ipynb` (2b, 3b, 4b, 5b, 6b, 7b).
- Code whose error Colab's editor can see before running (syntax errors, undefined names, wrong
  arguments) is in a string run by `run_code("""...""")`, defined in each page's setup cell, so the
  editor doesn't underline the answer. `review.sh check` enforces this for syntax errors.
  See "Errors an editor can see" in `yr/README.md`.
- Answers are markdown `<details>` blocks. These can't contain a code cell, which is why the new
  layout is needed.

## Final plan: review pages that survive Colab's "Run all", with live answers hidden until clicked

**How this plan was made.** Three candidate plans were written and scored by three judges. This plan starts from the highest-scoring one, the risk-first staged rollout, and adds the best ideas from the other two:
- from the maintainability plan: one command that writes everything that can be derived, a committed self-test of the checks, an explicit marker for the question's code, and a hidden helper cell;
- from the student-experience plan: multi-part Answers with each part's live cell next to its explanation, exact wording edits, and a test link you can open today.

Two reviewers then checked the draft against the repo. This revision fixes everything they found. The main changes:
- a new **Step 0** saves this plan and the helper scripts before anything else, so nothing is lost if the session moves to your laptop;
- the picture rule now allows ch04 Q14's empty canvases;
- the build guard counts only Answer dropdowns, not the concept lists;
- a rule for where the summary text of a multi-part Answer goes;
- new wording edits for the setup sentences and two Answers;
- a `run_code` that Pyright doesn't flag;
- a fix that keeps fallback B working with Colab's import-error handler;
- picture checks that give the same result on any machine;
- `verify_live.py` and the publish skill join the change list;
- smoke tests reordered so one early stop can't hide the later results;
- corrected counts and claims.

Prototype v2 later replaced the helper cell and `run_code` with an inline `run_cell` and stored outputs (section 2.2). The bullets above are history.

**Status.**
- **Step 0 is done (2026-10-08).** This plan is in this file on `v3`. The research, the prototype and the agents' helper scripts (`make_smoke.py`, `exp.py`, `conv3.py`, `runvis.py`, the `final-rev` tests) are on branch `yr-runall-research` under `yr/plans/research/` (`scratch/` and `prototype/`). Prototype v2 is there too: `prototype-v2/` (the two A2 notebooks) and `v2-workflow/` (`files/scripts/`, the three reviews, logs and `fix-v2.md`). The virtualenv that the checkpoint script copied there by mistake was removed.
- **The live review pages are unchanged.** They still use the `run_code` layout published on 2026-10-08.
- **Next:** see the Status at the top: the Colab tests (Part A2 and the DRY tests), then rewriting sections 2–5 for E1–E20.
- **Sections 1–5 below describe v3** (rewritten 2026-10-09). Sections 6–8 and 10 are still v2's.

**Evidence labels.** **VERIFIED** = tested in this container or seen in primary sources. **BELIEVED** = strong but indirect evidence. **UNKNOWN** = only a live Colab session can tell (section 7).

---

### 0. Why research workers 3 and 4 failed

**Short answer.** The workers' own work didn't fail.
- **The interrupt.** At 17:20:58 UTC an interrupt in the main session stopped the **whole workflow run**. Your screenshot shows it: "review-pages-runall-plan … Workflow Stopped", Research 2/4.
- **Why only 3 and 4.** Workers 1 and 2 had already finished. Workers 3 and 4 were in the middle of a step, so they are the two marked "Error".
- **The helper.** The helper agent "Cloud equivalent of /workflows" ("Stopped 56s") was stopped by the same interrupt.
- **The resume.** At 17:24 I resumed the same run. Workers 3 and 4 re-ran from scratch and finished. Every later phase ran on their results: verify, design, judge, critique and this revision.

Nothing needs fixing. This plan is the "continue".

**Evidence** (VERIFIED in the session log `~/.claude/projects/-home-user-yrThinkPython/6571a165-….jsonl` and in `…/subagents/workflows/wf_f52e2176-172/`; times are UTC on 2026-10-08):
- **17:19:56** Claude started the claude-code-guide helper to answer your question about `/workflows`.
- **17:20:53.7** your next message ("Is Claude Code running on my laptop faster…") was queued while Claude was mid-turn.
- **17:20:58.398** both worker transcripts end with `[Request interrupted by user]`:
  - worker 3 (`research:repo`, agent `af37ec9a…`) was comparing error texts between Python 3.12 and 3.13;
  - worker 4 (`research:prototype`, `a1fdadad…`) was reading JupyterLab source.
  - Neither had hit an error.
- **17:20:58.405** the helper call was rejected ("The user doesn't want to proceed with this tool use"). Your queued message was delivered at 17:20:58.442.
- **17:24:00** the same run resumed:
  - workers 1 and 2 came back from cache;
  - workers 3 and 4 re-ran (`a20fcc3e…`, `a24699395…`) and finished at 17:36:47 and 17:55:29.
- **UNKNOWN:** the log can't tell whether Stop was pressed during the 5 seconds after the message was queued, or whether sending a message mid-turn interrupts the turn by itself.

**Not the cause.** The workers guessed at several environment traps: no `rsync`, `git rev-parse` failing in copies, a Playwright browser-version mismatch, and `pkill -f` killing its own shell. All are real, and section 6 avoids them, but none caused this.

**To avoid a repeat:**
- While a workflow runs, don't press Stop and don't reject a pending step.
- To ask something else, wait for Claude's current step to finish, or use a separate session.
- Before moving the session to your laptop, let Step 0 (section 8) save everything first: some helper scripts exist only in this container's temporary scratchpad.

---

### The design in one paragraph (v3, 2026-10-09)

This is prototype v2's design, revised for goals 9–12, decisions E1–E20 and the 2026-10-09 Colab results (variant B,
run-cell titles that name the question, Python 3.13). **The author types each fact once; `review.sh sync` generates
everything that can be derived, by running the code; `review.sh check` fails if running `sync` again would change anything.**

- **Question code** is highlighted text: a markdown cell holding a `~~~python` fence, a **run block**. Text can't run, so Run
  all can't reveal an answer through it, and Colab's editor doesn't check it.
- **Answer.** A `#### Answer` heading saved collapsed. Inside it: the explanation, and one generated **run cell** per run
  block that shows the code's real output once (code hidden, output stored). Multi-part questions alternate part text and
  part output, then the summary.
- **Errors (variant B, chosen 2026-10-09).** A run cell whose code raises, or prints a line number, calls the page's hidden
  helper `run_code(r"""…""")`, which runs the code as its own cell and prints the traceback **as text** (stderr). Nothing
  raises, so Colab shows no red (!) icon, no "Explain error" button, and no red mark on a closed Answer row (A2-4).
- **Write-code questions.** The author types the prompt, the example calls and the solutions. `sync` writes the "Start from
  this header" block (E4), every example output (E2), the import lines of each Answer block (E5) and a "Then try:" line
  (E19). `check` runs **every** Answer block against every example (E3).
- **Fixes and "what if" variants** in Answers are short ```` ```python ```` blocks; `sync` runs each one after the
  question's code and writes its output or picture below it (E9–E11).
- **Values in prose** (Answers and Concepts) are written as expressions with a marker; `sync` writes the value (E12).
- **Provided helpers** are runnable definition cells, typed once, where first provided (E6).
- **Question numbers are fixed during a semester** (goal 12, E16). `sync` writes the run-cell titles from them
  ("Output of Question 8a"); only `review.sh renumber`, run between semesters, renumbers.
- **The page frame** (title paragraph, intro, help note, credits) comes from one template (E15).
- **Generated text** sits inside the author's cells between invisible delimiters that `sync` writes (E17).
- **One pinned stack:** `sync` and `check` generate only on `colablike.lock`, which matches Colab: **Python 3.13**,
  IPython 7.34.0, ipykernel 6.17.1 (E18).
- **Website.** Each Answer is one closed dropdown with the explanation and the stored outputs, no code; prep strips every
  marker and delimiter, and each converted page passes a before/after diff of the built site (E20).

---

### 1. What students will see

#### Colab: opening a page
- **Unchanged:** the title, "Concepts covered" and the "Questions" intro (the intro's setup sentence is reworded, section 5).
- **Help note** "Using this page in Colab or Jupyter" (text in 2.1; approved as is, A2-7), hidden on the website.
- **Setup:** the page's own setup cell, then the hidden helper cell that defines `run_code` (variant B). ch03 had only
  `run_code` in its setup cell; it now has only the helper cell.
- **Each question shows** its heading and prompt ("…then open the Answer to check."), the code as a highlighted block,
  **Part a**, **Part b**, … in multi-part questions, and definition cells ("Run this cell to define `square` and `jump`").
- **Write-code questions** show the header block, the examples with their outputs (both generated, looking as today) and the
  `# Your code here` cell.
- **A closed Answer** with an "N cells hidden" row (VERIFIED in Colab, A2-1).
- **The only code cells outside Answers:** the setup and helper cells, definition cells (which display nothing) and
  `# Your code here`. No stored output sits outside an Answer.
- **No red underlines** (question code is text) and **no red marks** before Run all (VERIFIED, A2-1).

#### Colab: after Runtime → Run all
- The "not authored by Google" warning appears; the student chooses Run anyway (VERIFIED).
- **Every cell runs and Run all reaches the end** (VERIFIED with v1 and v2; B raises nothing, so it can't stop).
- **Visible afterwards:** only "Downloaded jupyturtle.py" (VERIFIED, A2-4).
- **No red marks anywhere** with variant B: error outputs are text, so there is no (!) icon, no "Explain error" and no red
  icon on a closed Answer row (VERIFIED on the A/B page, A2-6).
- The table of contents lists one entry per run cell under its Answer ("Output of Question 8a"), once the Answer is open
  or after Run all (A2-1); the titles name the question, so the entries are useful.

#### Opening an Answer
- Click the arrow next to **Answer** or the "N cells hidden" row.
- The explanation, each run cell's output once (printed lines, a traceback as text, a turtle drawing, a value like `12`)
  under its title and a **Show code** link (VERIFIED wording, A2-2); fix and "what if" blocks with their generated output;
  values in the prose that were generated by running the code.
- Before Run all, the stored output; after Run all, the live output.
- **▶ on one run cell before setup:** plain run cells show their output again; an error run cell shows
  `NameError: name 'run_code' is not defined` (B's setup dependency). The help note covers it ("It can differ from the
  saved output if the setup has not run yet").
- **Copying an Answer's code** into a new cell after Run all runs it (goal 11, check C4): it has its own imports and uses
  the helpers the question defined.

#### JupyterLab 4 / Notebook 7
As v2 (VERIFIED in JupyterLab 4.6.4): Answers closed on opening; question code highlighted; hidden code shows as a grey bar
with the title; Run All regenerates the outputs; stored drawings are PNG, so they show in untrusted notebooks; Shift+Enter
onto a closed heading opens it (section 9, D10).

#### The website (Jupyter Book; review pages are not executed there)
- One closed Answer dropdown per question with the explanation and the stored outputs, no code; no Answer or Credits
  entries in the contents (V7).
- Tracebacks shortened for the site only (no banner, file paths or `<cell line: 0>`; syntax errors keep the code line and
  caret).
- No marker, delimiter or helper cell is visible; the diff gate (E20) checks every converted page.

#### Other viewers
VS Code, GitHub's preview, nbviewer and classic Notebook 6 show the Answers open, the hidden code and the stored outputs.
Anyone browsing the repo sees the answers (accepted, D11, D14).

---

### 2. Page layout, per kind of question

#### 2.1 Page skeleton, in order (E15: written from one template by `sync`, except the author's text)
1. **Title cell** (template): "NNb. Prof. Rosenthal's Review", the link to the chapter, and "Each question has a suggested
   answer under **Answer**. Try the question first, then open the Answer."
2. **`## Concepts covered`**: the author's two lists; values in them use markers (E12, E14).
3. **`## Questions` intro**: the author's text plus the template's setup sentence (table in section 5).
4. **The help note** (template; tagged `remove-cell`), approved as is (A2-7):
   > **Using this page in Colab or Jupyter**
   > - Each question's **Answer** is closed: click the arrow next to **Answer** to open it. For questions about what code displays or draws, the Answer also shows that code's output. The output is saved with the page, so it is there before you run anything. The code that produced it is hidden: click **Show code** in Colab, or the grey bar in Jupyter, to see it.
   > - To run code yourself, start with **Runtime → Run all** (Jupyter: **Run → Run All Cells**). It runs the page's setup and re-runs the code in every Answer. The Answers stay closed, and Run all does not stop at the errors that are answers. If Colab warns that the notebook was not authored by Google, choose **Run anyway**.
   > - Run your own code with **Ctrl+Enter**.
   > - When an Answer's code runs again, its output comes from your session. It can differ from the saved output if the setup has not run yet, or if your own code changed a name that the question uses.
   > - VS Code, GitHub's preview and nbviewer show the Answers open.
5. **The page's setup cell** (author), tagged `setup`, if the page needs one.
6. **The helper cell** (template), tagged `setup`, code hidden, title "Helper for the Answers": defines `run_code` (2.2).
7. **The questions.**
8. **`## Credits`** (template); the website build removes the heading line.

#### 2.2 The building blocks (exact format, for Claude)

**Run block** (author): one `~~~python` fence in a markdown cell before the Answer; `**Part x**` label above it in
multi-part questions. Tildes mean "the Answer runs this"; ```` ```python ```` blocks are examples or solutions. Not allowed
inside: Colab form markup, a `%%` magic, a `~~~` line, or both `"""` and `'''`.

**Answer heading:** `#### Answer` with `metadata.id` and `jp-MarkdownHeadingCollapsed: true`; its id is listed in
`colab.collapsed_sections` (VERIFIED in Colab).

**Run cell** (generated): code hidden (`cellView: "form"`, `jupyter.source_hidden`), stored output.
- **Title** (generated from the question number, goal 12): `# @title Output of Question 8a` for part a of Question 8,
  `# @title Output of Question 1` for a one-part question. For a lettered question with parts, a comma keeps it readable:
  `Output of Question 3b, part a`.
- **Plain** (title line + the code) when the code, run alone, neither raises nor prints a line number.
- **Wrapped** otherwise: `run_code(` + newline + `r"""` + the code + `""")`. The traceback is printed as text.

**Helper cell** (generated, variant B; prototype `errors_A_vs_B.ipynb`, cell `ab0000h1`):
```python
# @title Helper for the Answers
def run_code(code):
    """Run code as a cell of its own; print an error's traceback as text instead of raising."""
    import sys
    from IPython import get_ipython
    ip = get_ipython()
    if ip is None:
        exec(code, globals())
        return
    def to_stderr(etype, evalue, stb):
        stb = getattr(stb, 'stb', stb)           # Colab passes a ColabTraceback for import errors
        print(ip.InteractiveTB.stb2text(stb), file=sys.stderr)
    ip._showtraceback = to_stderr
    try:
        ip.run_cell(code, store_history=False)
    finally:
        del ip._showtraceback
```
- Must stay Pyright-clean when Colab joins the cells (re-verify in Step 3; v2's inline `run_cell` was).
- The error name is read from stderr: the **last line matching the exception regex**, not the literal last line, because
  Colab appends a NOTE after ModuleNotFoundError (section 4.4).

**Stored outputs, normalized** (as v2): null `execution_count`; `ipykernel_<pid>` paths → `ipykernel_0`; `Cell In[N]` →
`Cell In[1]`; streams merged; ANSI kept (stripped on the site); drawings as PNG with `review_drawing` metadata; limits
8000 characters / 60 lines; no memory addresses.

**Markers** (author; all invisible in Colab, VERIFIED 2026-10-09 T1/T2, and stripped on the site):

| Form | Meaning |
|---|---|
| `` `EXPR` is <!--=-->`?` `` | sync writes the value of the code span just before the marker (E12) |
| `` <!--= EXPR -->`?` `` | sync writes the value of EXPR (E12) |
| `` <!--=error-->`?` `` | sync writes the error name this part's run cell raises (E8; replaces v2's `<!-- error: X -->` records) |
| `<!--do: CODE -->` | hidden context run before the values that follow in the same cell (rare) |
| `<!-- not a solution -->` | the next ```` ```python ```` block in a write-code Answer is not a full solution (E3) |
| `<!-- header: f g -->` | the header block shows these functions (overrides the guess, E4) |
| `<!-- derive: from=Q14 replace="OLD" with="NEW" -->` | sync writes the next block as Q14's code with one change (E9) |

- **Rule (Colab T1):** an inline marker (the first four) **never starts a line or a list item**: a line that begins with
  `<!--` and has text after the comment renders as raw HTML, so its backticks show. A block marker (the last three) is
  **alone on its line**. `check` enforces both.
- In the Answer prose, `?` is what the author types; `sync` replaces it with the value and keeps it in step.

**Generated regions** (E17): `sync` writes generated text between `<!-- begin generated: KIND -->` and
`<!-- end generated: KIND -->`, each alone on its line (invisible, VERIFIED T2). KIND is `header`, `example`, `imports`,
`then-try`, `fix-output`. `check` reports a hand edit inside a region before `sync` would overwrite it.

**Sync stamp** (notebook metadata `yr_review`): `code_sha1` (every code cell), `outputs_sha1` (every stored output),
`generated_sha1` (every generated region and filled value), and `stack` (python 3.13.x, ipython 7.34.0, ipykernel 6.17.1).

#### 2.3 Per kind of question (what the author types → what students see)

**What is displayed / drawn / happens.** Author: prompt + run block + Answer prose. Students: the code; in the Answer, the
real output under "Output of Question 1", then the prose with its values generated.
~~~~
[md]   ### Question 1 (easy): what is displayed?
       Predict what this code displays, then open the Answer to check.
[md]   ~~~python
       minutes = 135
       print(minutes // 60, minutes % 60)
       ~~~
[md]   #### Answer                                   <- saved collapsed
[code] # @title Output of Question 1                 <- generated; code hidden; stored "2 15"
[md]   135 minutes is 2 hours (`135 // 60` is <!--=-->`2`) and ...
~~~~

**Errors, several parts** (ch05 Q8; also ch02 Q9, Q10, Q14, ch03 Q10, ch04 Q14, Q15). Each part's run cell is wrapped;
its prose names the error with `<!--=error-->`:
~~~~
[md]   **Part a** + ~~~python ... ~~~     (and Part b, Part c)
[md]   #### Answer
[md]   **Part a:** `=` assigns; comparing needs `==`, so this is a <!--=error-->`SyntaxError`:
[code] # @title Output of Question 8a              <- run_code(r"""…"""); stored traceback as text
[md]   **Part b:** ...
[code] # @title Output of Question 8b ...
[md]   Python finds each of these mistakes before it runs ...   <- summary
~~~~
Placement rule as v2: one run cell per run block, right after its `**Part x:**` cell; a missing Part cell is created as
`**Part x:** TODO` and check fails until it is written.

**Write a function** (E2–E5, E19). Author types:
~~~~
[md]   ### Question 9 (medium): write a function
       Write a function called `end_hour` that takes `start` and `duration` ...
       <!-- begin generated: header -->  ...  <!-- end generated: header -->     <- sync
       **Examples**
       ```python
       end_hour(9, 3)
       ```
       <!-- begin generated: example --> ```text 12``` <!-- end generated: example -->   <- sync
[code] # Your code here
[md]   #### Answer
[md]   ```python
       def end_hour(start, duration):
           print((start + duration) % 24)
       ```
       <!-- begin generated: then-try --> Then try: `end_hour(9, 3)` <!-- end generated: then-try -->
~~~~
- **Example outputs** come from running the solution, then each example (E2). A drawing example gets a generated picture.
- **Every** ```` ```python ```` block in the Answer is a solution and must reproduce every example of the functions it
  defines (a block that redefines only `larger` is checked against `larger`'s examples), unless marked
  `<!-- not a solution -->` (today only ch06 Q17's halfway version, whose own output is still generated) (E3).
- **Imports**: sync writes, at the top of each block, the import lines for the names the block uses (E5), in a generated
  region; the author never types them.
- **No example calls, example inputs or provided helpers in Answer blocks** (goal 11, E5).
- "Two correct ways to call it" blocks are example pairs; their outputs are generated the same way (E2).
- No run cell in write-code Answers: it would overwrite the student's own function during Run all (D3).

**Write code without a function** (ch02 Q11, Q12, Q16, Q17). Example 1's inputs become a definition cell ("Run this cell to
assign `hours`, `minutes` and `seconds`"); its output is generated; the Answer holds only the computation.

**Provided helpers** (E6, E7). A definition cell where the helper is first provided ("Run this cell to define `square` and
`jump`."), typed once; later questions get a generated pointer ("uses `square` and `jump` from Question 11"). ch04: `square`
and `jump` in Q11; `polygon` stays in Q14 with its docstring; `describe` stays in both Q5 and Q15 (check: identical).
ch07: `run_doctests` where first used.

**Fixes** (E9, E10). Four ways to trim a fix, all VERIFIED by the C4 prototype: (1) only the changed lines, run after the
question's code (ch02 Q15, ch06 Q8); (2) only the new `def`, then the question's own calls (ch05 Q7, Q14, ch06 Q15);
(3) a fix that renames the function keeps its own call (ch06 Q5, ch07 Q12); (4) a change that must come before the question's
code keeps the whole block (ch07 Q8, 4 lines). sync writes each fix's output below it (or "(nothing is displayed)"). ch07 Q14, ch05 Q14 and ch05 Q10's
second approach use a derive marker, so the full fixed code is shown but not retyped. A fix that uses a name a later question
reassigns (ch02 Q4 `price`) keeps its own input line; a lint lists names assigned by more than one question.

**"What if" variants** (E11, all of them, drawings included): a small ```` ```python ```` block in the Answer ("With `elif`
only:" …, "`left(144)` instead:" …); sync writes its output or picture below it. Covers ch05 Q5, Q6, Q10, Q11, Q15,
ch02 Q16 and the drawing claims ("draws a flipped star", "below the starting line").

**Refactor / generalize** (ch03 Q12; ch04 Q18, Q19; ch06 Q12). The given code is a ```` ```python ```` block; check runs it
and the solution and requires identical stdout (text) or identical SVG hashes (drawings).

**Doctest** (ch07 Q14). One run block, wrapped because the output names a line; a doctest that prints a failure fails C4.

**Reading a file**: as "what is displayed".

**Values in prose** (E12, E13). Each "`X` is `V`" claim in Answers and Concepts gets a marker, claim by claim, with the
rendered page unchanged as the gate. ch05's "about 3000" frames becomes ``about <!--= sys.getrecursionlimit() -->`1000` (the exact number depends on the environment)``
 (Colab: 1000, VERIFIED). Claims that can't be generated (verdicts, traces,
general rules) are covered by checks C8, C9, C11 or listed for a reread (4.4).

#### 2.4 Format rules (README; enforced by `review.sh check` and `check_notebooks.py`)
1. **Extent of a question:** from `### Question N (level): kind` to the next heading of level 1–3. **N** is digits with an
   optional letter (`3b`), unique on the page.
2. **Numbers are stable** (goal 12): check compares the page's question numbers with the last published version (`v3`) and
   fails if a published number disappeared, was reused or changed, unless `--renumbered` (only after `review.sh renumber`).
   A lettered question `Nb` may not exist while Question N has a "Part b".
3. **One Answer heading** per question; no other headings inside a question.
4. **Run blocks:** `~~~python`, only before the Answer, one per markdown cell, part labels with 2 or more.
5. **Code cells before the Answer:** setup cells, the helper cell, definition cells (parse, display nothing, raise
   nothing) and `# Your code here`.
6. **Code cells inside an Answer:** only generated run cells (hidden code, canonical title, exactly the two metadata keys).
7. **Output belongs to code:** in an Answer, a ```` ```text ```` block or picture appears only in a generated region after
   the ```` ```python ```` block that produced it.
8. **Error names:** every error a run cell raises is named by `<!--=error-->` in its part's prose or in the summary;
   any other error name in prose must be one the part raises (C8).
9. **Stored outputs:** only on run cells; written by `sync` on the pinned stack, with a matching stamp; within the limits;
   drawings intact.
10. **Markers:** only the forms in 2.2; inline markers never start a line; block markers alone on their line; no `?` left.
11. **Generated regions:** only `sync` writes them; their content equals what `sync` would write.
12. **Answer code (goal 11, C4):** every Answer ```` ```python ```` block runs in the end-of-Run-all namespace with the setup
    cell's imported names removed; every solution reproduces the examples; a doctest prints nothing.
13. **NameError answers stay true** (as v2, S18).
14. **End and tags:** the page ends with `## Credits`; tags only `setup`, `no-signature`, and `remove-cell` on the help note.
15. **Hands off:** never edit run cells, stored outputs, generated regions, filled values, the stamp, the helper cell or the
    help note by hand; never save a page from Colab back to GitHub (`sync` repairs such a page).
16. **No `TODO` left.**

---

### 3. Don't Repeat Yourself: what is typed once, what is generated

| The author types (once) | `sync` generates |
|---|---|
| question code (run blocks) | run cells, their stored outputs, run-cell titles |
| the error explanation, with `<!--=error-->` | the error name |
| each helper, in one definition cell | "uses X from Question N" pointers |
| the prompt, the example calls | the header block, every example output and picture |
| the solutions (no imports, helpers or example calls) | each block's import lines, the "Then try:" line |
| fixes (changed lines only) and "what if" blocks | their outputs and pictures; derived fixes |
| each prose value as an expression | the value |
| the question number (stable) | nothing (only `review.sh renumber`, between semesters) |
| the Concepts and Answer prose | the page frame, the help note, the helper cell, the credits |

**`review.sh sync NB… [--accept] [--force]`** (as v2, extended):
1. **Normalize** (static, stdlib): reconcile run cells with run blocks; regenerate a changed run cell and clear its outputs;
   canonical titles and metadata; template cells; `collapsed_sections`; drop Colab's metadata; clear other outputs.
2. **Reference run** on the pinned stack (fresh kernel, `TMPDIR=/tmp`, `allow_errors`): each run cell's code alone; each
   write-code example after each solution; each fix and variant after the question's code; each marker's expression.
3. **Stored run:** the page as it will be saved must show the same outputs.
4. **Refusals** (exit 2): wrong stack (`--force` writes, `check` then fails); over the limits or a memory address; a bad run
   block; solutions that disagree; a marker that starts a line.
5. **Snapshot acceptance:** a stored output, generated region or value that changes is shown as a diff and not written
   unless `--accept` (reread the prose first). New ones are written and printed.
6. **Store** outputs, regions, values and the stamp. **A second `sync` changes nothing.**

**`review.sh check NB`** fails if `sync` would change anything (static lint plus a fresh run, byte-identical on the pinned
stack), plus the rules in 2.4.

**What still repeats, by design (checked):** code quoted in prose (C9) and parameter names in prompts (C11); the OLD token
of a derive marker; example inputs quoted in a prompt; the `def` line in each full solution; ch04 `describe` in Q5 and Q15;
a fix's input line under E10; `#### Answer` and the difficulty labels; Concepts entries that overlap a question (E14; a lint
warns about shared code lines of 15+ characters).

**Rejected:** design-2's `%%question` / `%answer` magics (Colab may underline errors before students predict; Answer cells
overwrite the student's function during Run all; clicking before setup wipes the stored output); variant A for errors (red
marks on closed Answers, A2-4).

---

### 4. Tool, README and skill changes

#### 4.1 `yr/tools/review_format.py` (new, stdlib)
As v2 (start from `review_v2.py`), plus: marker parsing and filling (`markers`, `fill_values`), generated regions
(`regions`, `write_region`), the helper-cell text, the run-cell title from the question number, `stable_numbers` (compare
with `git show v3:PATH`), and lint rules for 2.4.

#### 4.2 `yr/tools/review_cells.py`
- **Done 2026-10-09:** lettered numbers (`3b`) in headings and `--before`; `renumber` documented as between-semesters only.
- **Spec kinds** (new format): `%%% markdown`, `%%% run [a]`, `%%% code [tags]` (definition cells), `%%% placeholder`,
  `%%% answer`, `%%% part a`; write-code examples are written without outputs.
- **`add`** never renumbers; it suggests the next free number (`3b` between 3 and 4).
- **`renumber`** also rewrites the "Question N" pointers and run-cell titles, and records the renumbering for check's
  stable-number rule.
- **`normalize NB…`**: the static repair after a page was saved in Colab.

#### 4.3 `yr/tools/sync_review.py` (new), run as `review.sh sync NB…`
Implements section 3 (prototype `sync_v2.py` plus design-3's `proto_writecode.py` and design-1's `gen_static.py` /
`inline_values.py`, all on `yr-runall-research` under `yr/plans/research/`). Needs nbclient, cairosvg and the pinned kernel.

**`yr/tools/ensure_colab_venv.sh` + `colablike.lock`:** `uv venv -p 3.13`, `uv pip sync` of the lock (ipython 7.34.0,
ipykernel 6.17.1, jupyter_client, pygments, traitlets, pyzmq, …), kernel `colablike`. The lock moves from 3.12 to 3.13
(VERIFIED: Colab is Python 3.13.16, 2026-10-09). Re-check that IPython 7.34 runs on 3.13 locally, as it does on Colab.

#### 4.4 `yr/tools/check_review.py` (new-format path)
- Static: `review_format.lint`. Runtime: the page as stored and the reference page, on a fresh kernel.
- **Error lines (variant B):** read from stderr: the last line matching the exception regex (Colab appends a NOTE after
  ModuleNotFoundError). The self-test gets a stderr mutation and a NOTE mutation.
- **Rules:** S1–S20 as v2, adapted to 2.4; R0 pinned stack; R1 Run all reaches the end; R2 nothing visible outside closed
  Answers but the setup cell's stdout; R3 stored = fresh (byte-identical on the pinned stack); R4 wrapped exactly when the
  code raises or names a line, and definition cells display nothing; R5 title and wrapper invisible.
- **New checks:**
  - **C4** (replaces S13; goal 11): each Answer ```` ```python ```` block runs after Run all with the setup cell's imported
    names removed (a missing import fails); every solution reproduces the examples (E3); a doctest that prints fails;
    a block followed by a generated output must print exactly it.
  - **C8** verdicts and "nothing is displayed" against the stored outputs; **C9** each code span in an explanation appears
    in the question code or a solution; **C11** names in the prompt appear in the header.
  - **Stable numbers** (2.4 rule 2) and the `3b` / Part b clash.
  - Generated regions and filled values equal what `sync` writes; markers well formed (rule 10).
  - "Same output before and after" for refactor questions (text: stdout; drawings: SVG hash).
  - Name-reuse lint (E10); Concepts overlap lint (E14).
- **C4 prototype (VERIFIED 2026-10-09, `yr/plans/research/c4-prototype/` on `yr-runall-research`):** all 11 fix blocks pass
  trimmed; a block missing its input line (ch02 Q4 prints `19.9919.99` once Q16's inputs are a cell), a missing import and a
  failing doctest all fail. **Each block must run in its own fresh end-of-Run-all namespace**: in one shared kernel an
  earlier block's `price = 4` hid the hazard. Run on the book venv; repeat on the pinned 3.13 stack in Step 3.

#### 4.5 `yr/tools/turtle_images.py`
As v2 (SVG hash, `--check`, hardening), plus: example pictures in write-code questions and "what if" pictures are
generated regions written by `sync`.

#### 4.6 `jb/prep_notebooks.py` (`process_review`)
As v2 (Answer dropdowns with stored outputs, shortened tracebacks, Credits heading removed, guard), plus: strip every marker
and delimiter (values stay), drop the helper cell, render definition cells as code. **Diff gate (E20):** build the site
before and after converting a page and compare the rendered review page; only intended changes may appear.
`verify_site.py` (prototype, `v2-workflow/files/scripts/`) joins the tools and checks that no `<!--`, `@title`, `run_code`
or `ipykernel_[1-9]` reaches the HTML.

#### 4.7 Other files
As v2: `check_notebooks.py` (lint yr/ pages; outputs only on run cells), `run_notebooks.sh` (skip yr/), `verify_live.py`
(dropdowns, no `@title`, no `<!--`, no `run_code`), the yrpublish pre-flight (`review.sh selftest`), `build-book` SKILL,
`review.sh` (`sync`, `renumber`, `selftest`, ROOT fallback), CI lint step, and `selftest_review.py` with a fixture that
covers every kind in 2.3 (including variant B errors, write-code examples, a fix, a "what if" drawing, markers and a lettered
question).

#### 4.8 README, guide for people, skills (goals 7 and 8; keep in step with every change)
- **Rule:** every design decision or tool change updates `yr/README.md` and the two skills **in the same change**
  (Prof. Rosenthal, 2026-10-09). Rules that already apply to today's pages go in at once (done: stable numbers); rules for
  the new format go in with the tools that implement them (Step 3), so the skills never describe tools that don't exist.
- **`yr/README.md`:** the guide for people near the top (one recipe per kind of 2.3: what to type, `review.sh sync`,
  `review.sh check`, or "ask Claude"), the marker table, generated regions, stable numbers and `renumber`, "if you edit a
  page in Colab", the tool list.
- **`yr-review-questions` SKILL:** what the author types per kind (2.3), the marker rules (inline never starts a line),
  never write run cells, generated regions, imports or example outputs by hand; numbers stay fixed (`3b`); workflow
  add → `review.sh sync` → `review.sh check` → `check_notebooks.py` → `build_book.sh`; C4 explained.
- **`yr-review-page` SKILL:** the template skeleton (2.1), the helper cell, the new verification steps.
- **`notebook-conventions` SKILL:** point to the README's Answer sections. **`CLAUDE.md`:** tools in "Where things are";
  delete "Pending work" at the end.
- **No new skill** (D12).

---

### 5. Converting the six pages

**The script.** The one-off converter (`convert_v2.py` + gate `verify_removed.py`, on `yr-runall-research`), extended for
v3. Not committed to v3 (D13). Per page:
1. **Question code cells → run blocks** (as v2; same ids; `run_code` wrappers removed with `ast`; part labels folded in).
2. **Answers** (as v2): `<details>` → `#### Answer` + explanation, part and summary cells (split points table below);
   every expected-output block of a part is removed and its run cell goes there; each removed error line becomes the
   prose's `<!--=error-->` marker on the error name it already names, or a short added clause where it names none.
3. **Write-code questions:** the typed example outputs become generated regions; gate: each generated output equals the
   typed one (86 of 86 already do, VERIFIED by the audit). Header blocks become generated (29 of 30 identical; one needs
   `<!-- header: … -->`). Answer blocks are trimmed: example calls, inputs and provided helpers removed; imports become
   generated; gate: C4 passes.
4. **Helpers:** ch04 `square`/`jump` → a definition cell in Q11; `polygon` stays in Q14; ch07 `run_doctests` at first use;
   pointers generated.
5. **Fixes and "what if" claims:** fix blocks trimmed to the changed lines (derive markers for ch07 Q14, ch05 Q14, ch05 Q10
   approach 2); "what if" claims become variant blocks (E11); their outputs generated.
6. **Prose values:** markers added claim by claim (only 86 of 275 are found automatically); gate: the rendered page is
   unchanged except where a value was wrong.
7. **Page-level:** template cells (title, help note, helper cell, credits); remove old `run_code` definitions and all
   `raises-exception` tags; ch03's setup cell goes; the stale "defines `run_code`" intro sentences are replaced (table below).
8. **`review.sh sync`**, then all gates, `review.sh check`, the site diff (E20).

**Question numbers are kept as they are** (goal 12).

**Answer split points** (VERIFIED in v2): ch02 Q10 "All three are a `TypeError`."; ch02 Q14 "A syntax error (here, a space
in a name)…"; ch04 Q14 "In all three parts the caller broke a precondition…"; ch04 Q15 "Some correct calls: …"; ch05 Q8
"All three are found before the cell runs…" (reworded below). ch02 Q9's last paragraph stays in Part e; ch04 Q15's
"(Python versions before 3.13 …)" stays in Part c (true: Colab is 3.13 and shows the suggestion); ch03 Q10 has no summary.

**Wording edits** (each must match exactly once; then grep question and Answer markdown for `\bcells?\b`, `run (it|this)`
and `run_code`):

| Page / question | Old | New |
|---|---|---|
| ch02–ch05, ch07 intro | "Some questions show their code inside `run_code("""...""")`. …" | (deleted) |
| ch02 intro | "Run the next cell first: it imports `math` and defines `run_code`." | "The setup cell below imports `math`." |
| ch03 intro | "Run the next cell first: it defines `run_code`." | (deleted) |
| ch04 intro | "Run the next cell first: it downloads `jupyturtle`, imports the functions the questions use, and defines `run_code`." | "The setup cell below downloads `jupyturtle` and imports the functions the questions use." |
| ch05 intro | "Run the next cell first: it downloads `jupyturtle`, imports those functions, and defines `run_code`." | "The setup cell below downloads `jupyturtle` and imports those functions." |
| ch06 intro | "Run the next cell first: it imports `math`." | "The setup cell below imports `math`." |
| ch07 intro | "Run the next cell first: it downloads `words.txt` and defines `run_code`." | "The setup cell below downloads `words.txt`." |
| all pages | "then run it to check" / "then run the cell(s) to check" | "then open the Answer to check" |
| ch02 Q4 | "What does this cell display when you run it in a notebook?" | "What does this code display when it is run as a notebook cell?" |
| ch02 Q9 | "For each cell, predict …" | "For each part, predict …" |
| ch02 Q14 | "Each cell has an error …" / "what each cell displays before the error" | "Each part has …" / "what each part displays …" |
| ch03 Q9 | "What does this cell display in a notebook?" | "What does this code display when it is run as a notebook cell?" |
| ch03 Q10, ch04 Q14 | "For each of the next three cells" | "For each of the three parts" |
| ch03 Q14 Answer | "first the line `outer('hi')` in the cell" | "first the line `outer('hi')` in the question's code" |
| ch04 Q7 | "… run only the setup cell … and this cell" | "… run only the setup cells (at the start of the Questions), and then this code" |
| ch05 Q8 | "Each cell has one mistake." | "Each part has one mistake." |
| ch05 Q8 Answer | "All three are found before the cell runs, so nothing is displayed or assigned." | "Python finds each of these mistakes before it runs any of that part's code, so nothing is displayed and `x` is never assigned." |
| ch05 Q14 | "… How would you fix the function?" | "… How would you fix the function? (Try your fix in a new cell, so that the cell above keeps the original code.)" |
| ch05 Concepts | "about 3000" frames | ``about <!--= sys.getrecursionlimit() -->`1000` (the exact number depends on the environment)`` (E13) |
| ch07 Q15 | "(… then run it …)" | "(… then open the Answer to see the number …)" |

Also fix what the audit found in v2's dry run (final.md section 3): dangling lead-ins where a text block was removed (ch03
Q10a, Q14; ch04 Q2, Q7, Q14, Q15; ch07 Q14), ch02 Q10's run cells relying on the setup cell's `import math` (each run
block carries its own import), and unused imports (generated imports remove them). Delete ch04's repeated jupyturtle
paragraph in the Questions intro and the facts listed twice in ch02 Concepts (E14).

**Order:** ch05 first (pilot), then ch02, ch03, ch06, ch07, and ch04 last (most helpers and pictures).

**Cell ids:** every cell that stays keeps its id; new: run cells, template cells, split explanation cells, definition
cells.

---

### 6. Verification here, before anything reaches you

- **V1. Checks on two stacks.** `check` on the pinned stack (byte comparison), and `check --kernel bookvenv --semantic`.
- **V2. Nothing changed.** For all 103 questions:
  - the conversion gate (`verify_removed.py`, section 5) compares every removed block and picture with the stored outputs;
  - `check` R3 compares the stored outputs with a fresh run, on both stacks.
  - Expect 0 differences except the intended ones.
  - v1's `exp.py` can't read v2 pages: it finds run cells only by `run_code(`, `# Part` or `%%run_question`, and runs kernel `python3`. Adapting it to `parse_run_cell` and the colablike kernel is optional.
- **V3. Run-all simulation.** nbclient with `allow_errors=False` and `force_raise_errors=True`, ignoring tags as Colab does, with `TMPDIR=/tmp`, on both stacks (`runall_sim.py`, prototype v2, saved under `v2-workflow/files/scripts/`). It must reach the end with no visible output except the setup lines.
- **V4. Idempotent.** Byte-identical results for: a re-sync, two syncs from the converted page, a venv rebuilt from the lock, and TMPDIR set elsewhere. All VERIFIED on ch05.
- **V5. Self-test.** `review.sh selftest` catches every mutation.
- **V6. Lint.** `check_notebooks.py` passes, including the new lint, on Python 3.12 as in CI.
- **V7. Website.** `build_book.sh` gives no warnings beyond `known_warnings.txt`. A script over `yr/chap0*_review.html` asserts:
  - "Answer" dropdowns equal the number of questions (17/16/19/17/17/17) and none is open, while the concept-list dropdowns are unchanged;
  - 0 `h4` headings, and 0 "Answer" or "Credits" contents entries;
  - no help text and no `def run_code`;
  - dropdown text identical to today's site, except the intended changes: ch02 Q4 now shows its stored `12`, and error Answers show their shortened tracebacks (for ch05: Q8 and Q14, section 1);
  - no traceback paths, banner, `<cell line` or `<!-- error`;
  - each run-block Answer shows each stored output once;
  - no new `<pre>` overflow at 1300 px compared with today's page.

  For pages still in the old format: prep's output notebooks (`jb/yr/*.ipynb` after `prep_notebooks.py`) must be identical with old and new tools; identical HTML is a nice-to-have. Screenshots: ch04 Q2 and Q14, ch05 Q8 and Q17, ch07 Q14, with the D7 alternative side by side.
- **V8 (pilot only).** Headless JupyterLab 4.6.4: the page opens collapsed, and Run All keeps outputs hidden.
- **V9. Pyright.** Run it on every visible code cell together with the cells above it. Expect nothing beyond the known jupyturtle import note. Run cells, including the wrapped `__import__('IPython').get_ipython().run_cell` form, are Pyright-clean in basic and off modes (VERIFIED, section 1).
- **V10. Diff.** `git diff` touches only the intended files. Outputs are stored only on run cells (lint), and ids are preserved: 62 of 64 kept; the two Part-label cells are folded into their run blocks.

**Environment traps to avoid:**
- there is no `rsync`: use `cp -a` or `tar`;
- work on a real branch, or rely on the ROOT fallback;
- Playwright needs `executable_path=/opt/pw-browsers/chromium-1194/chrome-linux/chrome`;
- start JupyterLab with `--allow-root --LabApp.expose_app_in_browser=True`;
- never run `pkill -f PATTERN` when the pattern appears in the same command line;
- don't press Stop during workflows (section 0).

---

### 7. Colab test checklist for you

Use Chrome, signed in, with default settings. Take a screenshot wherever it says [shot]. Between notebooks, use Runtime → Disconnect and delete runtime.

#### Part A: prototype v1 (DONE 2026-10-08; results under "Colab test results so far")
History: Part A is done, and Part A2 replaces it. Its items are labelled "v1 A1" to "v1 A4", so they don't clash with Part A2's A2-1 to A2-7. The v1 page, on the research branch (the URL returns HTTP 200, VERIFIED):
`https://colab.research.google.com/github/y-rosenthal/yrThinkPython/blob/yr-runall-research/yr/plans/research/prototype/out/all/chap05_review.ipynb`

**How v1 differed from the plan of that time** (history; prototype v2 replaced that plan, section 2.2). Part A tested the key questions: collapse on open, Run all, live answers and the keyboard. The differences:
- question code sits inside the heading cell, not in separate run-block cells;
- the code blocks lack the word `run`;
- the run cells sit at the end of each Answer, not next to each part;
- `run_code` is appended to the setup cell, with no plain-Python fallback, no Stop fix and no raw strings;
- there is no help note.

1. **v1 A1. Closed on open.** Before running anything: is every Answer closed, with an "N cells hidden" row? Write down the exact wording. [shot]
2. **v1 A2. Run all.** Choose Runtime → Run all.
   - If a "not authored by Google" warning appears, write down its exact text and choose Run anyway.
   - Wait until nothing is running.
   - Did it stop anywhere, or show an error popup?
   - Did any Answer open by itself, or did the page jump into one?
   - Is anything visible outside the Answers besides "Downloaded jupyturtle.py"?
   - How long did it take? [shot]
3. **v1 A3. Live answers.**
   - Open Q8: are there three errors (SyntaxError, SyntaxError, IndentationError), each shown once?
   - Open Q14 (RecursionError, expected to be short) and Q17 (a stored picture plus a live drawing). [shot]
4. **v1 A4. Keyboard.** Reload the page. Click Question 1's text and press **Shift+Enter** repeatedly through Question 3: does an Answer open? Repeat with the **Down arrow**, then with **Ctrl+Enter** followed by Down.

**Not reported:** v1 A1 (whether every Answer was closed on open, and the exact wording), v1 A2's run time, and v1 A4 (keyboard).

#### Part A2: prototype v2

The checklist below was written with prototype v2. Its source is key `colab_checklist_v2` in the scratchpad file `v2_final.json`, which will not last; a copy is also in `yr/plans/research/v2-workflow/fix-v2.md` on `yr-runall-research`. This plan adds two questions to it: error-record text in A2-3, and the run time in A2-4.

**Prototype v2: Colab test (about 15 minutes).** Use Chrome, signed in, default settings. Take a screenshot wherever it says [shot].

Both notebooks are pushed to branch `yr-runall-research` (it never deploys; pushed 2026-10-08):
- Main page: https://colab.research.google.com/github/y-rosenthal/yrThinkPython/blob/yr-runall-research/yr/plans/research/prototype-v2/chap05_review.ipynb
- A/B page: https://colab.research.google.com/github/y-rosenthal/yrThinkPython/blob/yr-runall-research/yr/plans/research/prototype-v2/errors_A_vs_B.ipynb

Don't use the page's own "Run this page on Colab" link: it opens today's page.

**Before you run anything (don't connect):**
1. **A2-1. Opening the page.**
   - Are all 17 Answers closed? Q1 should say "2 cells hidden" and Q8 "7 cells hidden".
   - Does the contents sidebar list any "Output" entries?
   - Is there a red mark on any Answer row?
   - Is the question code coloured, like the examples, with no stray symbols? [shot]
2. **A2-2. Open Q1's Answer.**
   - "2 15 / 2 0 3 / 3 -4" appears exactly once.
   - Its cell shows only the title "Output" and a "Show code" link. Write down the exact wording; there should be no code.
   - The explanation follows.
   - Double-click "Output": does the code appear? [shot]
3. **A2-3. Open Q8's Answer.**
   - Expected order: Part a text, its traceback, Part b, its traceback, Part c, its traceback, then the summary.
   - No `run_code` and no code anywhere.
   - Each header reads `/tmp/ipykernel_0/…py", line 2`.
   - Before running: is there any red (!) icon or "Explain error" button?
   - Is any `<!-- error` text visible in the Part a/b/c explanations?
   - Then open Q17: is the tree about the size of a 300×220 canvas, not double size? [shot]

**After Run all:**

4. **A2-4. Run all.** Choose Runtime → Run all, then Run anyway, and wait until it is idle.
   - Did all Answers stay closed?
   - Is anything visible outside them except "Downloaded jupyturtle.py"?
   - Any red marks on closed rows?
   - How long did Run all take? [shot]
5. **A2-5. Open Q8 and Q14 again.**
   - Headers now show a number other than 0, and the run cells have counters: proof that they re-ran.
   - Are there red (!) icons or "Explain error" buttons?
   - Q14 should still show `<cell line: 0>` and "last 1 frames repeated". If it shows `Cell In[`, Colab has upgraded IPython; tell Claude. [shot]
6. **A2-6. Open the A/B page.**
   - Look at Answer A and Answer B, then Run all and look again.
   - Which way should error answers look: A (normal red error, with Colab's icon and button) or B (the same traceback as plain text)?
   - Copy the END line: it shows Colab's Python, IPython and ipykernel versions. [shot]
7. **A2-7. Wording and a write-code question.**
   - In Q9, type code in "# Your code here" and press Ctrl+Enter: does it run?
   - Does the help note match what you saw ("Show code", the arrow, the warning dialog)?
   - Does anything still look repeated or confusing?

**What the A2 results decide:**

| Result | Action |
|---|---|
| Code visible in A2-2 | Add `{ display-mode: "form" }` back (one constant) |
| "Output" entries in the sidebar | Use an empty title, or one that names the question |
| Q17 tree double size | Store the PNG at scale 1 |
| Question code not coloured, or "~~~" visible | Use a cell-tag marker |
| `<!-- error` text visible in A2-3 | Move the error records into cell metadata (S10 then reads them there) |
| Prefers B in A2-6 | Switch to variant B: a helper cell again, stderr parsing in the checks (4.4), and a failing-import test (Part B) |
| END line shows Python 3.13 or IPython 8+ | Update `colablike.lock`, re-sync with `--accept`, and re-run V1 (section 10 item 7); nested `run_cell` already looks normal on 9.17 |

#### Part B: smoke-test notebooks (about 10 minutes; needs your OK to push branch `colab-smoke-test`, which never deploys)
**Before pushing, the generator `make_smoke.py` is updated to v2:**
- question code is a `~~~python` run block;
- a wrapped run cell is the inline `__import__('IPython').get_ipython().run_cell(r"""…""");`, with no helper;
- it keeps only the tests that v1 and Part A2 don't settle (below);
- it is committed with the notebooks.

**Dropped, because v1 or Part A2 settles them:**
- variant A getting past Run all (old Tests 10–12, B4): VERIFIED with v1;
- variant B on syntax errors (old Tests 7–9): A2-6;
- outputs without errors, red marks, and anything visible after Run all (old Tests 4–5, B5–B7): A2-1 to A2-5;
- the word "run" (old B2): the marker is now `~~~python` (A2-1);
- Colab's versions (old B10): A2-6's END line;
- the Stop test (old Notebook 3, S1): the Stop fix was dropped with the helper (2.2).

Each test is followed by a visible MARKER cell.

**Notebook 1** (`colab_tests/colab_test_runall.ipynb`). Test order:
- **Tests 1–3: collapse markers.** Test 1 has all markers; Test 2 only Colab's list with the top-level id; Test 3 only the JupyterLab key.
- **Test 4: fallback C,** only if A2-1 or A2-4 shows an Answer that is not closed or that opens by itself. "Show the output" boxes, including a failing import.
- **Test 5: variant B with two failing imports,** only if D15 picks B. It tests the ColabTraceback unwrap that ch02 Q14a needs, and that Colab's handler still works for the second import (section 10 item 1).
- **END.**

Checks:
5. **B1.** Before running: which of Tests 1–3 are closed? Is any "SECRET n" text visible without clicking?
6. **B3.** Run all. Which "MARKER n" lines appear, and is "END" printed?
   - **If Run all stopped at Test N:** click the first cell after Test N, choose Runtime → Run cell and below, and repeat until END.
   - Write down every stop.
7. **B7.** Test 5 (if present): do both Answers show the ModuleNotFoundError as plain text, with Colab's NOTE? [shot]
8. **B8.** Test 4 (if present): do both "Show the output" boxes open and show their contents, including the import error?
9. **B9.** Reload. Step through Test 1 with Shift+Enter, then with the Down arrow, then with Ctrl+Enter followed by Down. Which ones open the Answer?
10. **B11.** File → Save a copy in Drive. Open one Answer in the copy and save. Then File → Download .ipynb and send the file: it shows what Colab writes when it saves.

**Notebook 2** (`colab_test_editor.ipynb`; don't run it, just press Connect):
11. **E1–E7.** Click into each cell and wait 5 seconds. Is it underlined? Is it coloured?
    - E6 is a custom `%%magic`: is there an "unsupported magic" warning?
    - Repeat with Tools → Settings → Editor → Code diagnostics set to "Syntax and type checking". Write down every option in that list and which one is the default, then restore the default.

#### Part C: the real chapter 5 pilot (about 15 minutes, from branch `yr-review-runall`)
`https://colab.research.google.com/github/y-rosenthal/yrThinkPython/blob/yr-review-runall/yr/chap05_review.ipynb`

12. **P1.** On opening: all 17 Answers closed, question code shown as text, the help note visible, no underlines anywhere. Each Answer shows its stored output before Run all.
13. **P2.** Run all (accept the "not authored by Google" warning) reaches the end. Afterwards nothing is visible except "Downloaded jupyturtle.py".
14. **P3.** Q8 shows three errors, each shown once, before and after Run all, interleaved with their Part a/b/c explanations, then the summary.
15. **P4.** Q14 shows the RecursionError; Q17 shows one tree (stored before Run all, live after).
16. **P5.** Q9 (write code): your own code in `# Your code here` runs with Ctrl+Enter, and the Answer shows the solution text.
17. **P6.** Close an Answer again: it hides again.
18. **P7.** Does the help note's wording match what you saw (arrow, "cells hidden", the warning dialog)? Suggest changes.

#### What the results decide
Prototype v2's outcomes are in the A2 table above ("What the A2 results decide"). v1's results are under "Colab test results so far". This table covers Part B:

| Result | Action |
|---|---|
| B1: Test 1 closed; B3: END reached without help | Main design (no change) |
| B1: Test 2 also closed | No change; keep writing `metadata.id` (harmless) |
| B1: Test 1 **not** closed, or A2-1 / A2-4 show an Answer that is not closed or that opens by itself | Fallback C (section 10) |
| B9: Shift+Enter or Down opens Answers | Keep the design; help note says "use Run all; run your own code with Ctrl+Enter" (D10) |
| B7: Test 5's import error is not plain text, or the second import loses Colab's NOTE | Fix the unwrap (section 10 item 1) before switching to variant B |

---

### 8. Rollout: one page first

Your plan file's to-do list says "convert chapter 5 first and publish it". So for a while, the tools must handle both formats:
- each tool checks `review_format.page_format`;
- old-format pages go through today's code, kept unchanged in a `legacy` module;
- a mixed page is an error;
- `prep_notebooks.py` handles both (`answer_sections` does nothing on old pages);
- the legacy code is deleted after all six pages are converted.

**Steps:**
0. **Step 0, save the work. DONE on 2026-10-08** (see Status above).
   - Write this plan into `yr/plans/runall-collapsible-answers.md`: replace "Draft plan", set the Status line, tick to-do item 1. Commit it on a branch from `origin/v3` and push it to v3, the same way the earlier plan commits went (it changes only plan files; the site rebuilds unchanged).
   - Commit the scratchpad scripts the plan depends on to `yr-runall-research` under `yr/plans/research/prototype/scripts/`: `plan-risk/make_smoke.py`, `plan-maint/exp.py`, `plan-maint/conv3.py`, `verify-repo/runvis.py`, and this revision's `final-rev/` tests.
     - Saved on 2026-10-08 under `yr/plans/research/scratch/` (with the other agents' scripts and logs).
   - After this step, moving the session to your laptop loses nothing.
1. **Step 1.**
   - **1a. DONE (2026-10-08).** You ran Part A on prototype v1; the results are at the top ("Colab test results so far").
   - **1b. DONE.** Prototype v2 was built and reviewed by three reviewers, and every blocking and major issue was fixed.
   - **1c. DONE (2026-10-08).** Prototype v2 (2 notebooks) was pushed to `yr-runall-research` under `yr/plans/research/prototype-v2/`.
   - **1d.** You run Part A2 and decide D1–D18 (the defaults are the recommendations).
   - The files the checkpoint skipped were saved on 2026-10-08 (see To do).
2. **Step 2.** Update `make_smoke.py` to v2 (Part B lists the changes). With your OK, push `colab-smoke-test`, and you run Part B. If the results call for variant B or fallback C, the plan is adjusted before any page is touched.
3. **Step 3.** Branch `yr-review-runall` from `origin/v3`.
   - **Build:**
     - `review_format.py`, `sync_review.py`, the new `check_review.py` and `turtle_images.py`, with legacy paths;
     - `ensure_colab_venv.sh` and `colablike.lock` (4.3);
     - `prep_notebooks.py` with its guard;
     - `review_cells.py`, `check_notebooks.py`, `run_notebooks.sh`, `review.sh` and `build_book.sh` (ROOT fallback);
     - `verify_live.py` and the yrpublish, build-book and yr-review skills;
     - the self-test and fixture;
     - the README (with the guide for people) and `CLAUDE.md` "Where things are".
   - **Gate:**
     - old pages pass the old checks unchanged;
     - prep output for old pages is identical;
     - the self-test is green;
     - `check_notebooks` passes on Python 3.12;
     - the Colab-like venv recipe works.
4. **Step 4.** Convert **chapter 5 only** and run V1–V10. Push the branch; you run Part C from the branch link (D9).
5. **Step 5.** Publish chapter 5 with the yrpublish skill: the tools and ch05 go to v3 in one merge.
   - `verify_live.py` checks the live page.
   - Then a 2-minute check by you: open the live "Run this page on Colab" link, Run all, open one Answer.
6. **Step 6.** Convert ch02, ch03, ch06, ch07, then ch04, one commit each. Each passes V1–V7 plus a Colab spot-check by you (one error question, one turtle question).
7. **Step 7. Cleanup:**
   - remove the legacy paths; `check` then rejects `<details>` Answers;
   - add the CI lint step;
   - confirm on the live pages that your three reported problems are gone: underlines, Run all stopping, answers visible;
   - mark the plan file done and delete "Pending work" from `CLAUDE.md`;
   - stop the checkpoint scripts `checkpoint.sh` and `checkpoint_v2.sh` if they are still running (they exit by themselves when their workflow finishes), then `git worktree remove` the scratchpad worktrees `v3wt` and `v3main`;
   - with your OK, delete the `colab-smoke-test` and `yr-runall-research` branches.
     - **`yr-runall-research` must never be merged.** Its history contains a committed Python venv: 2,525 files under `prototype/venv-colablike/`, removed from the tip in `d8da395` (VERIFIED).
     - Keep it until Part A2 is done, since Part A2's links point at `prototype-v2/`.

**Rollback.** `git revert` of a page commit on v3 brings back the old page. The tools read both formats until Step 7, the site redeploys on push, and Colab links follow v3 immediately. A bad tools commit is reverted the same way.

---

### 9. Decisions needed from you (recommendation first)

**Status of D1–D18, restated for v3 (2026-10-09).** Settled ones are marked; the rest still need Prof. Rosenthal's answer.

| | Topic | Status in v3 |
|---|---|---|
| D1 | Overall design | **Settled** by E1 (v2 + sync fills markdown) |
| D2 | Permission to push | **Decided 2026-10-09: yes** — (a)–(c) done; (d) `colab-smoke-test` and (e) `yr-review-runall` may be pushed when the plan reaches them (neither deploys) |
| D3 | No runnable solution cell in write-code questions | **Decided 2026-10-09: as recommended** (solutions are markdown blocks, trimmed and checked by C4; E3, E5) |
| D4 | Multi-part Answers interleaved | **Settled** (VERIFIED in Colab, A2-3) |
| D5 | `~~~python` marker for question code | **Settled** (renders coloured in Colab, A2-1) |
| D6 | Wrap only code that raises or names a line | **Changed**: wrapped cells call the variant B helper `run_code` (2.2) |
| D7 | Question code as highlighted code blocks on the site | **Decided 2026-10-09: as recommended** |
| D8 | `## Credits` heading, removed on the site | **Settled** by E15 (template) |
| D9 | Test chapter 5 from the branch link before publishing | **Decided 2026-10-09: as recommended** (Claude can run it in Prof. Rosenthal's Chrome) |
| D10 | Shift+Enter / Down arrow may open Answers | **Decided 2026-10-09: accept** |
| D11 | Accept the cosmetic side effects | **Decided 2026-10-09: accept** (the contents entries now name the question) |
| D12 | No new skill | **Decided 2026-10-09: as recommended** |
| D13 | One-off conversion scripts not on v3 | **Decided 2026-10-09: as recommended** |
| D14 | Store outputs in the notebook | **Settled** by E2, E12, E17, E18 (outputs, examples and values are generated and stored) |
| D15 | Error variant A or B | **Settled: B** (2026-10-09) |
| D16 | Run-cell titles | **Settled**: name the question, "Output of Question 8a" (2026-10-09) |
| D17 | ch04 Q15c: accept the Python 3.12 output | **Moot**: Colab is Python 3.13 and shows "Did you mean 'sides'?", as the page already says |
| D18 | ch04 Q14's empty canvases stay | **Decided 2026-10-09: keep them** |

**All of D1–D18 are now decided** (2026-10-09: Prof. Rosenthal took the recommendation for every one still open). The original text follows.

- **D1. The overall design.** Question code as text; a closed Answer heading with the explanation plus hidden run cells that show the code's stored output, re-run by Run all. *Recommended.*
- **D2. Permission to push.** *Recommended.* Pushes (a) and (b) are done. The pushes:
  - (a) Step 0: the plan file to v3, and the scripts to `yr-runall-research` (done);
  - (b) prototype v2 to `yr-runall-research` (done 2026-10-08);
  - (c) the files the checkpoint skipped, to `yr-runall-research` (see To do);
  - (d) `colab-smoke-test` (never deploys);
  - (e) later, `yr-review-runall`.
- **D3. Write-code questions get no runnable solution cell.** *Recommended.* A solution cell would replace the student's own function during Run all.
- **D4. Multi-part Answers interleaved,** with each part's explanation followed by its run cell's output and the summary at the end. *Recommended.*
- **D5. Marker for the question's code:** a `~~~python` fence. *Recommended.* The alternative is a cell tag.
- **D6. Wrap only code that raises or names a line,** with the inline `run_cell` and no helper cell. *Recommended.* The alternative is to wrap every run cell: a simpler rule, but untested in Colab for printed output and drawings.
- **D7. On the website, question code shows as highlighted code blocks.** *Recommended* for simplicity. The alternative, a small extra build step, keeps today's code-cell look; decide from the V7 screenshots.
- **D8. A `## Credits` heading** in the notebooks, removed on the website. *Recommended.*
- **D9. Test chapter 5 from the branch link before publishing it.** *Recommended.* Your to-do order, publish first and then test, also works, but students could see a broken page.
- **D10. If Colab's Shift+Enter or Down arrow opens Answers,** accept it, with the help note's advice. *Recommended.*
- **D11. Accept the cosmetic side effects.** *Recommended.*
  - Colab's and JupyterLab's contents sidebars list an "Answer" per question, and possibly an "Output" entry per run cell (D16, A2-1).
  - "N cells hidden" reveals the number of parts.
  - Answers show open in VS Code, "Colab in VS Code/Cursor", GitHub's preview, nbviewer and classic Notebook 6.
  - Anyone browsing the repo sees the answers, including the stored outputs (D14).
- **D12. No new skill.** Update `yr-review-questions` and `yr-review-page`, and put the guide for people near the top of `yr/README.md`. *Recommended.*
- **D13. Don't commit the one-off conversion scripts to v3.** `convert_v2.py` and `verify_removed.py` are saved on `yr-runall-research` under `yr/plans/research/v2-workflow/files/scripts/`, and `make_smoke.py` also goes on the smoke branch. *Recommended.*
- **D14. Store outputs in the notebook,** generated by `sync` on the pinned Colab-like stack and stamped. *Recommended.*
  - Gain: Answers show their output before Run all and on the site.
  - Costs: a lint exception, running `ensure_colab_venv.sh` on your laptop, and answers visible to anyone browsing GitHub.
- **D15. Errors:** variant A (a normal red error; Colab adds its (!) icon and "Explain error" button after Run all) or variant B (the same traceback as text). Decide from `errors_A_vs_B.ipynb`. *Recommended: A,* unless the icons bother you.
  - B needs a hidden helper cell again (a setup dependency).
  - With B, the checks must read the error from text.
- **D16. Run-cell titles** "Output" / "Output of part a", with no display-mode annotation. *Recommended.* Revisit if A2 shows the titles in Colab's contents sidebar.
- **D17. ch04 Q15c: accept the Python 3.12 output.** The stored output has no "Did you mean 'sides'?", because Colab's Python 3.12 doesn't add it; the old block was written on 3.13. The prose already explains the version difference (section 5, dry run). *Recommended.*
- **D18. ch04 Q14's empty canvases stay,** stored as Colab shows them: an empty canvas before each traceback (2.3). *Recommended.* The alternative, dropping them, is one rule in `normalize_outputs`.

---

### 10. Known uncertainties and fallbacks

**The kernel side is VERIFIED on Colab's last known versions (Python 3.12, IPython 7.34.0, ipykernel 6.17.1); A2-6's END line confirms them. These are not verified:**

1. **Run all past caught errors:** VERIFIED in Colab (v1). Fallback B remains only as the D15 option, not as a fix for Run all.
   - **Fallback B** (variant B of D15; `errors_A_vs_B.ipynb` uses a shorter copy, `run_code_b`, without the Stop fix): route the traceback to stderr. No error output at all, the same traceback text, status ok:
     ```python
     def run_code(code):                       # variant B (D15)
         import sys
         try:
             from IPython import get_ipython
             ip = get_ipython()
         except ImportError:
             ip = None
         if ip is None:
             exec(code, globals())
             return
         def to_stderr(etype, evalue, stb):
             stb = getattr(stb, 'stb', stb)    # Colab passes a ColabTraceback for ImportError
             print(ip.InteractiveTB.stb2text(stb), file=sys.stderr)
         ip._showtraceback = to_stderr
         try:
             result = ip.run_cell(code, store_history=False)
         finally:
             del ip._showtraceback
         if isinstance(result.error_in_exec, KeyboardInterrupt):
             raise KeyboardInterrupt
     ```
   - **Why the unwrap line.** Colab's custom ImportError handler passes an object, not a list, as the traceback. Without the unwrap, ch02 Q14a would print a TypeError and turn off Colab's handler for the session (found by a reviewer).
   - **What is VERIFIED.** On IPython 7.34 and 9.17, with a simulated copy of Colab's handler:
     - the unwrap gives the ModuleNotFoundError plus Colab's NOTE on stderr, with status ok;
     - the handler keeps working for later cells.
   - **Not verified:** real Colab. A2-6 shows variant B's look on syntax errors only. The unwrap (ch02 Q14a's failing import) stays unverified in Colab until a failing-import test runs (Part B Test 5, if D15 = B).
   - **The checks** must then parse stderr, skipping the NOTE (4.4). v1's checks did; v2's do not yet, and v2's self-test has no such mutation.
2. **Are Answers closed on open from GitHub?** (A2-1, B1) The format matches real Colab-saved files exactly; Part B's Tests 2 and 3 isolate the markers, to show which ones Colab really needs.
   - **Fallback C**, if closed sections don't work or Run all opens them:
     - the run cells sit outside any closed section and call `run_hidden(r"""…""")`;
     - that captures stdout, the traceback text (with the same unwrap), the last drawing and the last value into one closed HTML "Show the output" box, with the exact values in metadata for `check_review`;
     - the explanation stays a `<details>` block.
   - **Status:** VERIFIED locally on both stacks; B8 tests rendering in Colab (Part B Test 4, run only if needed).
   - **Costs:** no live animation, and tracebacks lose colour.
   - **Not a one-function change.** It also changes check rules 2 and 6, since run cells would sit outside Answers, plus the turtle rules, the prep step and the README. That would be a separate small plan revision.
3. **Error badges:** VERIFIED after Run all: the red (!) icon and "Explain error" button on each error output (v1). UNKNOWN on stored errors before Run all (A2-3), and on closed Answer rows (A2-1, A2-4).
4. **Keyboard stepping** (B9). In JupyterLab, Shift+Enter opens closed Answers (VERIFIED). A 2018 Colab issue says the Down arrow did too. In Colab it stays UNKNOWN until B9 or Part C: v1 A4 was not reported, and A2 has no keyboard step. Mitigation: D10.
5. **The `~~~python` run-block marker in Colab** (A2-1). Highlighting VERIFIED in JupyterLab 4.6.4 and on the site, BELIEVED in Colab. Fallback: a cell tag.
6. **Editing a page in Colab and saving** (B11).
   - Colab may add outputs and `metadata.id`, and may change the closed layout (it has a separate "Save collapsed section layout" command).
   - `normalize` repairs all of this, and `check_notebooks` (also in CI) fails until it is repaired.
7. **Version drift.**
   - Stored outputs come from the pinned stack: Python 3.12, IPython 7.34, ipykernel 6.17.1.
   - If Colab moves to Python 3.13 or IPython 8+ (A2-6's END line shows its versions), update the lock and re-sync every page with `--accept`; the diffs show what changed.
   - Harmless differences after Run all:
     - live tracebacks show Colab's pid, and Q14's definition-cell frames read `/tmp/ipython-input-<hash>.py` (BELIEVED);
     - ch02 Q14a gains Colab's NOTE and "Open Examples".
8. **Stop button.** The Stop fix was dropped with the helper (2.2). Stop during a wrapped cell no longer halts Run all. This is accepted, because wrapped cells take milliseconds. Variant B's `run_code` (item 1) would bring the fix back.
9. **Nested `run_cell`:** in v1, Colab ran it for errors without duplicated output (VERIFIED). Printed output and drawings stay plain cells.
10. **Other viewers** (VS Code, GitHub preview, nbviewer, classic Notebook 6): Answers show open (BELIEVED). Accepted and documented.
11. **The January 2026 Colab redesign.** Labels like "↳ N cells hidden" and the Settings path may differ. The help note's final wording waits for A2-2, A2-7 and P7.
12. **Run all on ch04** animates several turtle drawings in hidden cells, so it may take a minute or two. A2-4 records the time for ch05.
13. **Students' own names.** A student who redefines a name that a question uses (for example `import jupyturtle` before ch04 Q7) changes that Answer's live output. Rule 2.4.12 covers re-runs of the page itself; the help note covers the rest.
14. **Hidden run cells and Pyright:** run cells are Pyright-clean, so "Show code" should show no underline (VERIFIED locally, BELIEVED in Colab).
15. **Drawing tamper gap:** a hand-replaced but valid PNG passes if its png_sha1 and the stamp are recomputed. This is deliberate: the PNG is not re-rendered while the SVG is unchanged, because cairo output differs between machines.

**Scratch artifacts used by this plan** (temporary until Step 0 saves the scripts; under `/tmp/claude-0/-home-user-yrThinkPython/6571a165-f8cc-5e43-8b74-c00357a4a6f6/scratchpad/ultra/`):
- `plan-risk/`: smoke notebook generator and logs;
- `plan-maint/`: equivalence script `exp.py`, conversion script `conv3.py`;
- `plan-student/`: run_code and Stop tests;
- `proto/`: prototype converter, adapted tools, mutations;
- `verify-repo/`: `runvis.py`, mutations;
- `verify-jupyter/`: traceback and interrupt tests;
- `critic-feas/`: Colab ImportError-handler simulation;
- `final-rev/`: this revision's tests (Pyright-clean `run_code` on both stacks, the fallback B unwrap).
- `v2/`: prototype v2 (`scripts/`, `out/chap05_review.ipynb`, `out/errors_A_vs_B.ipynb`, logs). Saved under `v2-workflow/files/` except `scripts/colablike.lock`, `scripts/ensure_colab_venv.sh`, `scripts/make_all.sh` and `scripts/build_site.sh` (see To do);
- `v2fix_exp/`: the fix-round experiments (inline `run_cell`, Pyright, labfence) and the ch02–ch07 dry-run notebooks. Not saved yet (see To do); `colab-fresh/` inside it is a venv;
- `v2_before_fix/`: prototype v2 before the review fixes;
- `v2review_colab/`, `v2review_student/`: the v2 reviewers' probes.

This revision also registered two test kernelspecs (`rk_yrThinkPython`, `rk_venv-ipy7`) under `/root/.local/share/jupyter/kernels`, outside the repo. The prototype is also on branch `yr-runall-research` under `yr/plans/research/prototype/`.

## How to resume (for a future Claude session)

**Latest first (2026-10-09):** goals 9-12 came after prototype v2. The DRY audit for them is done, and Prof. Rosenthal decided
E1–E20 (section "DRY audit and decisions E1–E20"; full results on branch `yr-runall-research` in `yr/plans/research/dry-audit/`).
On the laptop, that branch is checked out as a worktree at `../yrThinkPython-research`, and the agents' scratch folder is
`../yrThinkPython-work/`. Next: the Colab tests (Part A2 plus the DRY tests), then rewrite sections 2–5 for E1–E20. Don't change
the live review pages before Prof. Rosenthal's go-ahead.


The research was done by a multi-agent workflow in a cloud session on 2026-10-08. While it ran, a
background script pushed each finished agent's result to the branch **`yr-runall-research`**, in
`yr/plans/research/`: one markdown file per agent (research, verify, plan, judge, synthesize, critic,
revise) plus the prototype's files in `prototype/` (converted chapter 5 notebook, modified
`prep_notebooks.py`, conversion scripts). Start there: `git fetch origin yr-runall-research`. The final
plan (`revise.md`) is copied into this file. Prototype v2 is in the same folder: `prototype-v2/` holds the two Part A2 notebooks, and `v2-workflow/` holds its scripts (`files/scripts/`: `review_v2.py`, `sync_v2.py`, `check_v2.py`, `selftest_v2.py`, `convert_v2.py`, `verify_removed.py`, …), the three reviews, logs, and `fix-v2.md` (the plan delta and the A2 checklist). Before implementing, ask Prof. Rosenthal for the decisions in section 9.
Originally, if the plan had been missing, the instructions were to redo only the missing parts: map every question on the six pages and every tool that
would change, build a prototype of the chapter 5 conversion in a scratch folder (convert the page,
run it top to bottom with nbclient `allow_errors=False`, build the website from it), then write the
final plan here and ask Prof. Rosenthal for the decisions above before changing the live pages.
