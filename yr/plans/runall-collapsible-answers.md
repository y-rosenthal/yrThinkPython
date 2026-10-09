# Plan: review pages that work with Colab's "Run all", with answers hidden until clicked

**Status (2026-10-08): prototype v2 is built, reviewed by three reviewers and fixed. It is pushed to `yr-runall-research` (`yr/plans/research/prototype-v2/`, 2 notebooks) and ready for Prof. Rosenthal's Colab test (checklist Part A2). Nothing is implemented in the repo yet: the live review pages are unchanged.**

**Next step:** Prof. Rosenthal runs checklist Part A2 (section 7, about 15 minutes) and decides D1–D18 (section 9; each has a recommendation). The two notebooks:
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
- [ ] Step 1d: Prof. Rosenthal runs Part A2 and decides D1–D18
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
    An audit of every question against goals 9 and 10 is in progress (workflow wf_4a14bc8a-617).

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
- **Next:** Step 1d (see the Status at the top): Part A2 and D1–D18.

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

### The design in one paragraph

- **Question.** The code is highlighted text: a markdown cell holding a `~~~python` fence, called a **run block**. The tildes mean "the Answer runs this"; ```` ```python ```` blocks are never run.
  - Text can't run, so Run all can't reveal an answer through it.
  - Colab's editor is BELIEVED never to check markdown.
- **Answer.** A `#### Answer` heading saved collapsed (Colab and JupyterLab). Inside it, the explanation and one **run cell** per run block, which shows the code's **real output once**, next to its explanation. Multi-part questions alternate: Part a's text, Part a's output, Part b's text, …, then the summary.
- **Run cell.** Generated by `review.sh sync`.
  - Its code is hidden: Colab form view and JupyterLab `source_hidden`. "Show code" still works.
  - Its **output is stored in the notebook**, so the Answer shows it before Run all, on GitHub's preview and on the website. Run all re-runs it.
- **Errors.** A run cell whose code raises, or prints a line number, is wrapped as `__import__('IPython').get_ipython().run_cell(r"""…""");`.
  - The error looks like a normal cell's, with the question's line numbers.
  - Run all continues: VERIFIED in Colab with v1.
  - There is no helper cell, so the run cell also works before setup.
- **One copy of the code; outputs are generated, never typed.** `sync` writes the run cells, the stored outputs and a stamp. `check`, the lint and the build refuse stale, hand-edited or wrong-stack outputs.
- **Website.** Each Answer is one closed dropdown holding the explanation and the stored outputs (tracebacks shortened), with no code.

---

### 1. What students will see

#### Colab: opening a page from its "Run this page on Colab" link
- **Unchanged:** the title, "Concepts covered" and the "Questions" intro (the setup sentence is reworded, see section 5).
- **Help note** "Using this page in Colab or Jupyter", hidden on the website. The text is in 2.1.
- **One setup cell:** the page's own. The managed `run_code` cell is dropped. ch03 has none, because its old setup cell held only `run_code`.
- **Each question shows:**
  - its heading and prompt ("…then open the Answer to check.");
  - the code as a highlighted block;
  - **Part a**, **Part b**, … in multi-part questions.
- **A closed Answer** with an "N cells hidden" row. The format is VERIFIED from Colab-saved notebooks; that Colab honours it when opened from GitHub is BELIEVED (A2-1).
- **The only code cells outside Answers:** the setup cell, definition cells (which display nothing) and `# Your code here`. No stored output sits outside an Answer (VERIFIED, rules S8 and R2).
- **No red underlines.** Question code is text. Every code cell is Pyright-clean when the cells are joined as Colab does: Pyright 1.1.414, basic and off modes, reports only today's jupyturtle import notes (VERIFIED).

#### Colab: after Runtime → Run all
- **First run:** a "not authored by Google" warning is BELIEVED; the student chooses Run anyway.
- **Every cell runs,** including the hidden ones, and **Run all reaches the end**:
  - VERIFIED in Colab with v1, which uses the same mechanism;
  - VERIFIED for v2 in nbclient simulations on both stacks: 21/21 cells, every reply status ok.
- **Visible afterwards:** only "Downloaded jupyturtle.py" (VERIFIED: simulation and JupyterLab 4.6.4).
- **After Run all, each error output inside the closed Answer gets Colab's red (!) icon and "Explain error" button** (VERIFIED with v1). Whether a closed Answer row also gets a red mark is UNKNOWN (A2-4).
- **What visibly changes, proving the cells re-ran:**
  - execution counters appear;
  - Q8's headers change from `ipykernel_0` to Colab's process id;
  - Q14's frames from the definition cell read `/tmp/ipython-input-3568901665.py` (BELIEVED, harmless).

#### Opening an Answer
- **How:** click the arrow next to **Answer**, or the "N cells hidden" row.
- **What appears:** the explanation and each run cell's output, once: printed lines, a red traceback, the turtle drawing (stored as a PNG; the live SVG after Run all), or a value like `12`. A run cell shows only its title ("Output" or "Output of part a") and "Show code". The 2026 wording is BELIEVED (A2-2).
- **Before Run all,** the stored output, with no execution counter. **After Run all,** the live output.
- **▶ on one run cell before setup:**
  - wrapped cells show exactly their stored output;
  - Q14 and Q17 show a plain NameError that doesn't reveal the hidden code;
  - VERIFIED on the Colab-like kernel. The help note covers it.
- **Errors look like a normal cell's:** no wrapper frame, the question's line numbers, and the code line with a caret for syntax errors (VERIFIED on 7.34 and 9.17).

#### Write-code questions
- **No change on the question side:** header, at least 2 examples, and the `# Your code here` cell.
- **The Answer:** the same closed heading, containing the suggested solution(s) as text. It has no run cell: one would overwrite the student's own function during Run all.

#### JupyterLab 4 / Notebook 7
VERIFIED in JupyterLab 4.6.4 on v2:
- **On opening:** 17 closed Answers and 0 outputs visible.
- **Question code is highlighted.** The first v2 marker, ```` ```python run ````, gave 0 highlight spans; `~~~python` gives the same highlighting as ```` ```python ````.
- **An expanded Answer** shows the stored outputs. Hidden code shows as a grey bar: `# @title Output of part a •••`.
- **Run All** regenerates the outputs (headers read `Cell In[N]` on its IPython 9 kernel), and nothing becomes visible outside the Answers.
- **Downloaded pages are untrusted, but stored drawings still show,** because they are stored as PNG (untrusted HTML/SVG would render blank).
- **Shift+Enter onto a closed heading opens it** (D10).

#### The website (Jupyter Book; review pages are not executed there)
- **One closed Answer dropdown per question,** holding the explanation and the stored outputs, with no code. There are no Answer or Credits entries in the contents, and no new warnings (VERIFIED, V7).
- **Tracebacks are shortened for the site only:**
  - no banner, dashed line, file paths or `<cell line: 0>`;
  - syntax errors keep the code line, the caret and the message.
- **Overflow:** Q14 no longer overflows its box at 1300 px. The one overflow left, Q8a's 73-character message, is identical on today's site.
- **Dropdown text is identical to today's for 15 of 17 questions.**
  - Q8 adds each error's code line and caret, and its summary is reworded.
  - Q14 adds the traceback frames.
- **Question code shows as highlighted code blocks** (D7).

#### Other viewers
- **VS Code, GitHub's preview, nbviewer and classic Notebook 6:** Answers open, code visible including the title line, stored outputs shown (BELIEVED; GitHub and nbviewer were not checked).
- **Anyone browsing the repo sees the answers,** including the stored outputs. Accepted (D11, D14). The Colab link stays the way students open the page.

---

### 2. Page layout, per kind of question

#### 2.1 Page skeleton, in order
1. **Title cell.** Same text, plus one sentence that works everywhere: "Each question has a suggested answer under **Answer**. Try the question first, then open the Answer."
2. **`## Concepts covered`**: unchanged.
3. **`## Questions` intro.**
   - The paragraph about `run_code("""...""")` is deleted.
   - "Run the next cell first: …" becomes a per-page sentence that is true in Colab and on the site (table in section 5).
4. **The help note:** a managed markdown cell tagged `remove-cell`; `sync` writes it.
   > **Using this page in Colab or Jupyter**
   > - Each question's **Answer** is closed: click the arrow next to **Answer** to open it. For questions about what code displays or draws, the Answer also shows that code's output. The output is saved with the page, so it is there before you run anything. The code that produced it is hidden: click **Show code** in Colab, or the grey bar in Jupyter, to see it.
   > - To run code yourself, start with **Runtime → Run all** (Jupyter: **Run → Run All Cells**). It runs the page's setup and re-runs the code in every Answer. The Answers stay closed, and Run all does not stop at the errors that are answers. If Colab warns that the notebook was not authored by Google, choose **Run anyway**.
   > - Run your own code with **Ctrl+Enter**.
   > - When an Answer's code runs again, its output comes from your session. It can differ from the saved output if the setup has not run yet, or if your own code changed a name that the question uses.
   > - VS Code, GitHub's preview and nbviewer show the Answers open.
5. **The page's own setup cell**, tagged `setup`. The old `run_code` is removed from it, and ch03's then-empty setup cell is deleted. **There is no managed `run_code` cell.**
6. **The questions.**
7. **`## Credits`** (unchanged): the heading is added to the existing credit cell.
   - Without it, the last Answer would swallow the credits.
   - The website build removes the heading line, so the site's contents list is unchanged (checked in V7).

#### 2.2 The building blocks (exact format, for Claude)

**Run block.** The question's code, written once: a markdown cell before the Answer, holding one fence. In a multi-part question it starts with a part label.
~~~~
**Part a**

~~~python
x = 5
if x = 5:
    print('five')
~~~
~~~~
- **Tildes mark a run block.** Examples, headers and solutions use ```` ```python ````.
- **Highlighting.** The info string is plain `python`, so every renderer highlights it: VERIFIED in JupyterLab 4.6.4 and on the site, BELIEVED in Colab (A2-1).
- **Not allowed inside a run block:** Colab form markup (`#@title`, `#@param`, `#@markdown`, anywhere on a line; Colab parses it), a `%%` cell magic, a `~~~` line, or code containing both `"""` and `'''`.

**Answer heading:** unchanged (`metadata.id` plus `jp-MarkdownHeadingCollapsed`). `metadata.id` equals `id`, which is what Colab itself writes for nbformat 4.5 files.
```json
{"cell_type": "markdown", "id": "9c41e7b2",
 "metadata": {"id": "9c41e7b2", "jp-MarkdownHeadingCollapsed": true},
 "source": ["#### Answer"]}
```

**Run cell.** A code cell inside the Answer, generated by `sync`, with hidden code and stored output:
```json
{"cell_type": "code", "id": "846ec840", "execution_count": null,
 "metadata": {"cellView": "form", "jupyter": {"source_hidden": true}},
 "outputs": [{"output_type": "error", "ename": "SyntaxError", "evalue": "…", "traceback": ["…"]}],
 "source": ["# @title Output of part a\n", "__import__('IPython').get_ipython().run_cell(\n", "r\"\"\"\n",
            "x = 5\n", "if x = 5:\n", "    print('five')\n", "\"\"\");"]}
```
- **Title.** `# @title Output`, or `# @title Output of part x` in multi-part questions.
  - Colab shows it above the output; JupyterLab shows it in the hidden-code bar.
  - It still names the output after its explanation has scrolled away.
  - "Answer" or "Solution" were rejected: the cell shows Python's output, not a model answer.
- **No `{ display-mode: "form" }` annotation.**
  - `cellView: "form"` alone is what Colab's own hide-code command writes. Strong evidence: 332 of about 420 titled cells in a corpus of Colab-saved notebooks, and TF docs rely on it for GitHub links.
  - The annotation read as jargon in JupyterLab's bar.
  - A2-2 confirms the code opens hidden; the fallback is one constant.
  - The parser accepts any `#\s*@title` line, and `sync` rewrites Colab's variants.
- **Plain or wrapped.** Plain means the title line plus the code. A cell is wrapped exactly when the code, run alone, raises or prints a line number (`line N`, `<>:N:`, `Cell In[`).
  - Why: the title is line 1 of a plain cell and shifts such numbers by one (VERIFIED: a failing doctest reports line 7 instead of 6).
  - Inside `run_cell` the title has no effect.
- **Why an inline `run_cell` and no `run_code` helper:**
  - it is the mechanism Colab ran in v1 (`ip.run_cell`);
  - there is no setup dependency: ▶ before setup shows the stored error again, not `NameError: run_code` with the wrapper;
  - there is no managed cell to show or keep in step;
  - it is Pyright-clean in basic and off modes. Bare `get_ipython()` is "not defined"; `from IPython import get_ipython` gives "run_cell is not a known attribute of None".
- **The trailing `;`** hides the ExecutionResult. It also hides a value shown by the code's last line, so `sync` refuses a wrapped cell that would lose one (R5).
- **Dropped with the helper:**
  - the Stop fix: a KeyboardInterrupt inside a wrapped cell no longer stops Run all (wrapped cells take milliseconds);
  - the plain-Python fallback: no tool runs run cells outside IPython.
- **Quoting.**
  - `r"""…"""`, or `r'''…'''` when the code contains `"""`.
  - The opening quote goes on its own line; otherwise IPython 9 empties doctests.
  - `sync` refuses code that contains both styles.
  - `>>>` lines are allowed (VERIFIED on 7.34 and 9.17).
- **Stored outputs, normalized:**
  - `execution_count` is null;
  - any `…ipykernel_<pid>/` path (any TMPDIR) becomes `/tmp/ipykernel_0/`;
  - `Cell In[N]` becomes `Cell In[1]`;
  - consecutive stream outputs are merged (ipykernel splits them by timing);
  - ANSI colours are kept (stripped only on the site);
  - a jupyturtle drawing is stored as a PNG shown at its SVG size, with output metadata `review_drawing: {svg_sha1, png_sha1}`. The PNG is re-rendered only when the SVG changes, and reused only if intact.
  - **Limits:** 8000 characters / 60 lines of text, and no memory addresses.

**Error record.** The author's expected error, at the end of that part's explanation:
```
**Part a:** `=` assigns; comparing needs `==`:

<!-- error: SyntaxError -->
```
- It is invisible: VERIFIED in JupyterLab and on the site (prep strips it), BELIEVED in Colab.
- `check` compares it with the real error (S10).
- The converter writes it from the error line of the removed text block, so the prose stays as the author wrote it. v2's first build had added "…, so this is a `SyntaxError`", which echoed the traceback.

**Sync stamp** (notebook metadata):
```json
"yr_review": {"code_sha1": "…", "outputs_sha1": "…",
              "stack": {"python": "3.12.3", "ipython": "7.34.0", "ipykernel": "6.17.1"}}
```
- `code_sha1` covers every code cell's source: setup, definition and run cells.
- `outputs_sha1` covers every stored output.
- Lint recomputes both and reports "code changed since the last sync" or "stored outputs differ from what sync wrote".

**Notebook metadata:** `colab.collapsed_sections` (as before) and `yr_review`. `collapsed_sections` lists exactly the Answer heading ids, in page order; `sync` writes both.
```json
"metadata": {"colab": {"collapsed_sections": ["9c41e7b2", "…one per Answer…"]},
             "kernelspec": {"display_name": "Python 3 (ipykernel)", "language": "python", "name": "python3"},
             "language_info": {"name": "python"},
             "yr_review": {"…": "the sync stamp above"}}
```

#### 2.3 Tiny examples

**What is displayed** (one run block). A new run cell goes right after the Answer heading, output first. If the author moves it, `sync` keeps the new position.
~~~~
[md]   ### Question 1 (easy): what is displayed?
       Predict what this code displays, then open the Answer to check.
[md]   ~~~python
       minutes = 135
       print(minutes // 60, minutes % 60)
       ~~~
[md]   #### Answer                                      <- saved collapsed
[code] # @title Output                                  <- generated; code hidden; stored output "2 15"
       minutes = 135
       print(minutes // 60, minutes % 60)
[md]   135 minutes is 2 hours (`135 // 60`) and 15 minutes left over ...
~~~~

**Errors, several parts** (ch05 Q8; also ch02 Q9, Q10, Q14, ch03 Q10, ch04 Q14, Q15):
~~~~
[md]   **Part a** + ~~~python ... ~~~     (and Part b, Part c)
[md]   #### Answer
[md]   **Part a:** `=` assigns; comparing needs `==`:   <!-- error: SyntaxError -->
[code] # @title Output of part a                         <- wrapped; stored traceback
       __import__('IPython').get_ipython().run_cell(
       r"""
       x = 5
       if x = 5:
           print('five')
       """);
[md]   **Part b:** ...   <!-- error: SyntaxError -->
[code] # @title Output of part b ...
[md]   **Part c:** ...   <!-- error: IndentationError -->
[code] # @title Output of part c ...
[md]   Python finds each of these mistakes before it runs any of that part's code, so nothing is displayed and `x` is never assigned.   <- summary
~~~~

**Placement rule** (`sync` applies it, lint checks it):
- **One run block:** one run cell. A new one goes right after `#### Answer`; an existing one keeps its place.
- **Two or more run blocks:**
  - the run blocks are labelled `**Part a**`, `**Part b**`, …;
  - the Answer has one `**Part x:**` cell per part, in order;
  - run cell x goes right after its `**Part x:**` cell, and `sync` moves it there;
  - a missing Part cell is created as `**Part x:** TODO`, and lint fails until it is written.
- **Matching:** run cells are matched to run blocks by the part letter in their title. An orphan run cell is deleted.
- **Summary cells:** markdown cells after the last run cell.
- **Parts without an error** (ch02 Q9 a and e, ch04 Q14 c) are plain cells.

**Last value shown** (ch02 Q4 `price * 3`, ch03 Q9 `greet`): the plain run cell stores the value (VERIFIED in the dry run for ch03 Q9). **No text block is added to ch02 Q4.**

**Wrong calls** (ch03 Q10, Q14; ch04 Q14, Q15; ch05 Q14; ch06 Q15):
- the definition cell stays a visible code cell that displays nothing;
- the call is a run block, and the Answer's run cell is wrapped;
- ch05 Q14's prompt adds "(Try your fix in a new cell, so that the cell above keeps the original code.)".

**What is drawn** (ch04 Q2, Q6, Q7; ch05 Q17):
- The Answer picture is the run cell's stored PNG, byte-identical to today's (VERIFIED: ch05 Q17 and ch04's three). The Answer has no `<img data-turtle>` of its own.
- **Empty canvases** (ch04 Q14 a–c) are stored as Colab shows them: an empty canvas before the traceback. Recommended, not yet reviewed by Prof. Rosenthal (D18). Dropping them would be one rule in `normalize_outputs`, applied to stored and fresh outputs alike.

**Doctest** (ch07 Q14): one run block, wrapped because the output names a line (`File "__main__", line 9`), so the number matches the question's code. VERIFIED in the dry run: `sync` wrapped it, and the check passes.

**Unchanged:**
- **Write code:** no run cell.
- **Refactor / generalize / simplify:** the given code is a ```` ```python ```` block, never run.
- **Reading a file:** as "what is displayed".

#### 2.4 Format rules (go in the README; enforced by `review.sh check` and `check_notebooks.py`)
1. **Extent of a question:** from `### Question N (level): kind` to the next heading of level 1–3.
2. **One Answer heading:** exactly one cell whose source is `#### Answer`.
3. **No other headings inside a question:** no ATX, setext or HTML `<hN>` headings, checked outside fences.
4. **Run blocks:**
   - `~~~python` fences, only before the Answer, one per markdown cell;
   - with 2 or more, `**Part x**` labels and the placement rule of 2.3;
   - no form markup, `%%` lines or `~~~` lines inside;
   - `~~~` fences nowhere else, and the old ```` ```python run ```` marker is rejected.
5. **Code cells before the Answer:** only setup cells, definition cells (which parse, display nothing and raise nothing) and `# Your code here`.
6. **Code cells inside an Answer:** only generated run cells: hidden code, canonical title, exactly the two metadata keys.
7. **Output belongs in the run cell.** In an Answer of a question with run blocks, an output-like block is allowed only right after a ```` ```python ```` block in the same cell, with at most one short line between them (e.g. "That displays:"). Output-like means any non-python fence, indented code, `<pre>` or a data-turtle picture. A ```` ```text ```` block there must equal what that code prints.
8. **Error names:**
   - every error a run cell raises is named in its part's prose or in the summary, visibly or as `<!-- error: Name -->`;
   - every error name in a part's prose is raised by that part;
   - a record lists exactly the errors raised;
   - summary names are raised by some part.
9. **Stored outputs:**
   - only on run cells;
   - written by `sync` on the pinned stack, with a matching stamp;
   - within the limits, with no memory addresses;
   - drawings intact.
10. **End and tags:** the page ends with `## Credits`. The only tags are `setup`, `no-signature`, and `remove-cell` on the help note.
11. **Hands off.** Never edit run cells, stored outputs, the stamp or the help note by hand: edit the run block or the prose, then run `review.sh sync`. Never save a review page from Colab back to GitHub (Colab adds its own metadata and outputs); `sync` repairs such a page.
12. **NameError answers stay true:** a name that a run cell's NameError reports may not be bound at module level by another code cell or by another question's run block. VERIFIED in the dry run: ch03 Q10a, ch04 Q7 and ch07 Q8 pass.
13. **No `TODO` left in an Answer.**

---

### 3. Don't Repeat Yourself: how the code stays in one place

- **Single source.** The question's code is written once, in a `~~~python` run block. Outputs are never typed: `sync` generates them.
- **`review.sh sync NB… [--accept] [--force]`:**
  1. **Normalize** (static, stdlib; also `review_cells.py normalize`):
     - reconcile run cells with run blocks (2.3): create, delete orphans, move multi-part cells;
     - regenerate a run cell whose block changed, **and clear its outputs**;
     - make titles and layout canonical, and set exactly the two metadata keys;
     - write the help note, the heading metadata and `collapsed_sections`;
     - drop the metadata Colab adds on save;
     - clear the outputs of non-run cells.
  2. **Reference run.** Every run cell holds only the question's code: what a student gets by pasting it into a new cell.
     - Fresh kernel of the **pinned Colab-like stack**, `TMPDIR=/tmp`, tags ignored, `allow_errors`.
     - A cell is wrapped exactly when its code raises or names a line.
  3. **Stored run.** The page as it will be saved. Each run cell must show what it showed in the reference run (semantically, line numbers included); otherwise `sync` refuses.
  4. **Refusals** (exit 2, nothing written):
     - the kernel is not the pinned stack (`--force` writes anyway, and `check` then fails);
     - an output is over the limits or contains a memory address;
     - a run block has form markup, a cell magic, a `~~~` line or both quote styles.
  5. **Snapshot acceptance.** A stored output that was not empty and changes is printed with a semantic and a byte diff, and is **not written** (exit 1) unless `--accept`. The README says: reread the Answer prose before accepting. New outputs are written and printed.
  6. **Store** the normalized outputs and the stamp.
  7. **A second `sync` changes nothing.** VERIFIED byte-identical, also with a venv rebuilt from the lock and with TMPDIR set elsewhere.
- **`review.sh check NB` fails if `sync` would change anything.** Static part: the lint, including the stamp. Runtime part: a fresh run, byte-identical on the pinned stack.
- **Rejected:**
  - B (a string variable), C (reading the notebook at run time), a `%%run_question` magic, `# type: ignore`;
  - a cell-tag marker: invisible to authors; kept as the fallback if Colab renders `~~~python` badly;
  - the expected output kept in metadata: snapshot acceptance does that job visibly.

---

### 4. Tool, README and skill changes

#### 4.1 New `yr/tools/review_format.py`
- **Stdlib only, Python 3.12.** It works on raw JSON dicts (for `check_notebooks.py`, CI and prep) and on nbformat nodes.
  - Start from the prototype `review_v2.py`, whose parse and render code already uses dict access.
  - The static part of `check_v2.py` still uses attribute access and must be moved over.
- **Constants:** `ANSWER_HEADING`, `RUN_FENCE`, `PLACEHOLDER`, `CREDITS_HEADING`, `HELP_CELL`, `RUN_CELL_METADATA`, `WRAP_CALL`, `PINNED_STACK`, the output limits and `STAMP_KEY`.
- **Helpers:**
  - `parse_page`, `heading_level`;
  - `render_run_cell` and `parse_run_cell` (any `#\s*@title` first line), `quote`, `run_block_problems`;
  - `normalize_outputs`, `semantic`, `canon_outputs`, `needs_wrap`, `output_problems`, `drawing_problems`;
  - `make_stamp`, `stamp_problems`;
  - the site renderer `render_outputs` and `site_traceback`, shared with prep.
- **`normalize(nb)`, `lint(nb)`** (rules 2.4 = S1–S20) and **`page_format(nb)`** (`new`, `old` or `mixed`, which is an error).

#### 4.2 `yr/tools/review_cells.py` (stays stdlib)
- **Spec kinds:**
  - `%%% markdown`;
  - **`%%% run`** or **`%%% run a`**: plain code, which becomes a run-block cell. With a letter, the `**Part a**` label line is written above the fence;
  - `%%% code [tags]` (definition cells only);
  - `%%% placeholder`;
  - **`%%% answer`**: the `#### Answer` heading cell, plus one explanation cell if the body is not empty;
  - **`%%% part a`**: an Answer cell starting with `**Part a:**` (added if missing);
  - a `%%% markdown` after the Answer's parts becomes a summary cell.
  - Headings in Answer bodies are rejected.
- **`add` / `renumber`:** call `normalize`, then print "run `review.sh sync NB`, then `review.sh check NB`".
- **New `normalize NB…`:** the static repair, e.g. after a page was saved in Colab.
- **`new` skeleton:** title sentence, help note (written by `sync`), setup cell, `## Credits`, and `"colab": {"collapsed_sections": []}`.
- **Docstring:** full spec examples, including a multi-part error question with a summary.

#### 4.3 New `yr/tools/sync_review.py`, run as `review.sh sync NB…`
Implements section 3 (prototype: `sync_v2.py`). It needs nbclient and cairosvg (the book venv) and the pinned kernel.

**New `yr/tools/ensure_colab_venv.sh` + `yr/tools/colablike.lock`:**
- runs `uv venv -p 3.12`, then `uv pip sync` of the lock, which pins every package: ipython 7.34.0, ipykernel 6.17.1, jupyter_client 7.4.9, pygments, traitlets, pyzmq, …;
- registers the kernel `colablike`;
- VERIFIED: a venv rebuilt from the lock gives byte-identical stored outputs;
- the Python patch version is not pinned; the stamp records it, and a change would show as a byte diff that needs `--accept`.

#### 4.4 `yr/tools/check_review.py` (new-format path)
**How it runs.**
- Static part: `review_format.lint`.
- Runtime part: two executions on a fresh kernel, with `allow_errors`, tags ignored and `TMPDIR=/tmp`. `on_cell_executed` records reply statuses.
  - the page as stored;
  - the reference page, where each run cell holds only the question's code.

**What counts as an error line:**
- error names come from `error` outputs only (variant A; `review_v2.errors_of`, used by `needs_wrap` and S10);
- if D15 picks B, add stderr parsing: the **last line matching the exception regex**, not the literal last line, because Colab appends a NOTE after ModuleNotFoundError (VERIFIED in simulation with v1's check);
- then add a stderr mutation and a NOTE mutation to the self-test, so that switching to variant B can't silently disable the checks.

**Rules** (prototype `check_v2.py`; none of today's checks is weakened):
- **S1–S20:** rules 2.4, including S14 (the stamp), S9 (output belongs in the run cell), S10 (error records), S17 (drawing integrity) and S18 (NameError names).
- **R0 pinned stack.** On any other stack the byte check is impossible: the run is reported WEAK and fails unless `--semantic` is given.
- **R1** Run all reaches the end.
- **R2** Nothing is visible outside collapsed Answers except the setup cell's stdout.
- **R3 Stored output equals a fresh run:**
  - byte-identical after normalization on the pinned stack (drawings re-rendered unless the stored PNG is intact);
  - semantically equal elsewhere.
- **R4** Wrapped exactly when the fresh run raises or names a line; definition cells display nothing.
- **R5** The title line and the wrapper are invisible: the reference run shows the same output.
- **S13** Answer ```` ```python ```` blocks run on their own, and a ```` ```text ```` block after one equals its output.

**Kernel choice:** `--kernel colablike` by default. A second stack runs with `--kernel X --semantic`. This replaces `REVIEW_PYTHON`.

**Today's rule 5 is retired:** outputs are generated, not typed. The author's intent is kept by:
- the error records (S10);
- snapshot acceptance (`sync`);
- the conversion gate (section 5);
- S13, for code in the prose.

#### 4.5 `yr/tools/turtle_images.py`
- **What it runs:** it uses `parse_page`. Per question it runs:
  1. the setup cells;
  2. the Answer's ```` ```python ```` blocks;
  3. the definition cells and run blocks, in page order.
  - It **never runs run cells**.
- **Example pictures only.** `turtle_images` draws the pictures in write-code questions and Answer examples.
  - Each `<img data-turtle>` is drawn from the nearest ```` ```python ```` block above it in the same cell.
  - With no such block it reports an error, because a picture of a run block is the run cell's stored output (S9).
- **Two separate hashes:** `data-svg-sha1` on img tags (examples) and the `review_drawing` output metadata (run cells).
- **SVG hash:** it writes `data-svg-sha1` and re-renders the PNG only when the hash changes.
- **New `--check`:** compares hashes, writes nothing, and exits 1 on any difference.
- **Hardening:** if an example picture's code raises, it exits 1 without writing anything. Today's tool silently rewrote 19 ch04 pictures with partial drawings on the new layout (VERIFIED).

#### 4.6 `jb/prep_notebooks.py` (`process_review`)
1. Drop `# Your code here` cells (as now).
2. `raw_pictures` and `details_to_dropdown`, as now. The concept lists stay `toggle-shown` dropdowns, and old-format pages use the same path.
3. **`answer_sections`:** each `#### Answer` section becomes one `:::{admonition} Answer` / `:class: dropdown` cell, with no code. It holds:
   - the markdown cells, without the `<!-- error: -->` records;
   - each run cell's **stored outputs**, rendered by `review_format.render_outputs`:
     - text and tracebacks in ```` ```text ```` blocks without ANSI, tracebacks shortened by `site_traceback`;
     - PNG drawings as an `<img>` at display size, inside a raw-HTML div.
4. **New:** remove the `## Credits` line from the credit cell.
5. `process_cell` (as now). Never tag run cells `solution`: prep would blank them.
6. **Guard.** Stop the build if:
   - a new-format page's stamp does not match;
   - the number of Answer dropdowns ≠ the number of questions;
   - a `#### Answer` survives;
   - **any** cell sits between an Answer dropdown and the next question, section or credits;
   - a code cell inside an Answer is not a run cell;
   - an output exceeds the limits;
   - any other code cell has outputs.

   The concept-list dropdowns ("Python Syntax and Semantics", …) are not counted. Without the guard, new pages with old tools publish every answer openly with zero warnings (VERIFIED risk).

Old-format pages: prep output is byte-identical with old and new tools (VERIFIED for ch02, ch03, ch04, ch06, ch07).

The help note is removed by myst-nb's standard `remove-cell` tag; V7 checks this.

#### 4.7 Other files
- **`check_notebooks.py`** (`.claude/skills/check-notebooks/`):
  - for `yr/*.ipynb`, call `review_format.lint(nb)`;
  - allow outputs **only** on yr/ run cells, with `execution_count` null, output types stream / error / display_data / execute_result, no `transient`, and within the limits;
  - chapters keep "no stored outputs";
  - today it reports 13 "has stored outputs" on the v2 page, and nothing else (VERIFIED).
- **`.claude/skills/check-notebooks/run_notebooks.sh`:** skip `yr/` pages and point to `review.sh check`. Its tag logic (line 62) would report the caught errors as failures (VERIFIED in simulation).
- **`verify_live.py`** (`.claude/skills/yrpublish/`), per yr page:
  - Answer dropdowns == questions, and none starts open;
  - each run-block Answer has a `pre` or an `img`;
  - no `@title`, `display-mode`, `run_cell`, `ipykernel_[1-9]` or `<!-- error`;
  - no h4, and no Answer or Credits contents entries.
- **`.claude/skills/yrpublish/SKILL.md` pre-flight:** add `yr/tools/review.sh selftest`, next to `review.sh check`.
- **`.claude/skills/build-book/SKILL.md`, lines 25–31** (how prep handles yr/): mention `answer_sections` and the guard.
- **`yr/tools/review.sh`:**
  - new `sync` and `selftest` cases; `images` stays as an alias for the picture step;
  - **ROOT fallback** for copies without `.git`. It walks up to `jb/_config.yml`, so it works at any depth (`yr/tools/` is 2 levels down, `.claude/skills/X/` is 3):
    `ROOT="$(git -C "$(dirname "$0")" rev-parse --show-toplevel 2>/dev/null)" || ROOT="$(cd "$(dirname "$0")" && while [ ! -f jb/_config.yml ] && [ "$PWD" != / ]; do cd ..; done; pwd)"`
  - The same line goes in `build_book.sh` and `run_notebooks.sh` (BELIEVED; tested in Step 3).
- **`.github/workflows/deploy-book.yml`:** add `python3 .claude/skills/check-notebooks/check_notebooks.py` before the build. It is static, fast, and passes on today's 48 notebooks (VERIFIED).
- **New `yr/tools/selftest_review.py`, run as `review.sh selftest`.**
  - **The fixture:** `yr/tools/selftest/fixture_review.ipynb`, about 10 questions covering every kind, including ch04 Q14's empty-canvas case and a multi-part question with a summary. It is outside `yr/*.ipynb`, so it never reaches the site.
  - **The test:** each mutation is applied to a copy and must make `check` fail with the expected message; the unmutated fixture must pass.
  - **Self-test.** The prototype has 49 mutations and 9 scenarios; all pass.
    - **Stale or edited outputs:**
      - a block edited (S4); a block edited, then statically normalized (S14);
      - an output edited (S14); an output edited and restamped (R3); outputs cleared (S14);
      - a wrong stack in the stamp (S14); never synced (S14);
      - a corrupt PNG, a wrong PNG size (S17).
    - **Format:**
      - ATX, setext and HTML headings (S2); part labels (S3);
      - swapped run cells, a moved summary (S6);
      - code not hidden, a Colab-rewritten title, Colab metadata (S5);
      - the old marker, a stray `~~~` (S19); form markup or `%%` in a run block (S16);
      - code before the Answer (S7); tags, credits (S12);
      - output on the setup cell, an execution_count (S8); a TODO (S20).
    - **S9:** a duplicate text block, a plain fence, a contradicting block, an ```` ```output ```` fence, an indented block, an error block, an error line in a part, a duplicate picture.
    - **Errors:**
      - a record contradicting a part that no longer raises, a wrong name, a missing record, a wrong summary name (S10);
      - wrapped but not raising, a line number in a plain cell (S11);
      - a plain raising cell (R1); a definition cell that prints (R4);
      - a NameError name bound elsewhere (S18); a wrong text block after an Answer example (S13).
    - **Scenarios:**
      - an unaccepted change is refused and the file is left unchanged;
      - static normalize repairs a Colab-saved page;
      - new questions: placement, a split stream merged, a doctest wrapped and passing on both stacks;
      - a part added, then removed;
      - refusals: a lost value, a memory address, the wrong stack;
      - TMPDIR paths normalized.
    - **The fixture should add:** ch02 Q4's last value, stdout followed by an error, an empty canvas and a NameError answer.

#### 4.8 README, guide for people, skills (goals 7 and 8)
- **`yr/README.md`:**
  - **New section near the top, "Adding a question: a guide for people"** (goal 8). One short recipe per kind: what is displayed, what is drawn, an error answer, several parts (with a summary), wrong calls, write code, refactor, doctest. Each recipe gives:
    - the exact text to type;
    - the commands `review.sh sync`, `review.sh check`, `check_notebooks.py`;
    - "or ask Claude: *add a question to chapter N's review page*".

    It also covers "If you edit a page in Colab or Jupyter": download it, then run `review_cells.py normalize` or `review.sh sync`.
  - **Rewrite these sections:**
    - "Layout of a page", "Answers", "Cell conventions": replace the `<details>`, `raises-exception` and "Errors an editor can see" sections;
    - "Turtle pictures" (SVG hash);
    - "Tools" (`sync`, `normalize`, `selftest`, `--check`, `--kernel` / `--semantic`, and how to make the Colab-like venv with `ensure_colab_venv.sh`);
    - the `review.sh check` list;
    - "How the build handles yr/".
  - **The file tree at the top:** add `review_format.py`, `sync_review.py`, `selftest_review.py`, `selftest/`, `ensure_colab_venv.sh`, `colablike.lock` and the temporary `legacy` module.
- **`.claude/skills/yr-review-questions/SKILL.md`** (goal 7):
  - **Rules:** question code goes in `%%% run` blocks; one way per kind (a table); never write run cells or `run_code` by hand; no headings in Answers; no `raises-exception`.
  - **Spec examples:** an error question and a multi-part question with a summary.
  - **Workflow:** add → `review.sh sync` → `review.sh check` → `check_notebooks.py` → `build_book.sh`.
- **`.claude/skills/yr-review-page/SKILL.md`:** the new skeleton and verification steps.
- **`.claude/skills/notebook-conventions/SKILL.md`, line ~86:** point to the README's Answer sections.
- **`CLAUDE.md`:**
  - update "Where things are": the review tools and `review.sh selftest`;
  - at the end of the rollout, delete "Pending work".
- **No new skill** (D12).
- **The plan file `yr/plans/runall-collapsible-answers.md`:**
  - **Step 0** writes this plan into it, replacing "Draft plan". It also updates the Status line and to-do list and ticks item 1, as its own to-do order asks.
  - **Step 7** marks it done.

---

### 5. Converting the six pages

**The script.** A one-off converter: prototype v2's `convert_v2.py`, with the gate `verify_removed.py`. Both are saved on `yr-runall-research` under `yr/plans/research/v2-workflow/files/scripts/`. They are not committed to v3 (D13). They replace v1's `convert.py` and `plan-maint/conv3.py`. For each page:
1. **Question code cells.** Every question code cell that isn't `# Your code here` and isn't definition-only becomes a `~~~python` run-block markdown cell **with the same id**.
   - "Definition-only" means: by `ast`, only def/class/import/assignment, no output in an executed copy, and not tagged `raises-exception`. It finds exactly the 6 definition cells (VERIFIED).
   - The `run_code("""…""")` wrapper is removed with `ast`.
   - A trailing `**Part x**` line in the cell above, or a `**Part x**` cell, is folded into the run-block cell.
2. **Answers** (`convert_v2.py`; the gate is `verify_removed.py`):
   - The `<details>` Answer becomes `#### Answer` (keeping the old id) plus explanation cells, split at `**Part x:**` and at the listed summary starts. The tails were read (VERIFIED):

     | Question | The summary starts with |
     |---|---|
     | ch02 Q10 | "All three are a `TypeError`." |
     | ch02 Q14 | "A syntax error (here, a space in a name)…" |
     | ch04 Q14 | "In all three parts the caller broke a precondition…" |
     | ch04 Q15 | "Some correct calls: …" |
     | ch05 Q8 | "All three are found before the cell runs…" (reworded below) |

     - ch02 Q9's last paragraph is about part e and stays in the Part e cell. ch04 Q15's "(Python versions before 3.13 …)" stays in the Part c cell. ch03 Q10 has no summary.
   - **Every** expected-output block of a part is removed: text blocks, and the Answer picture of a run block.
     - The run cell goes where the first removed block was.
     - Each removed error line becomes an `<!-- error: Name -->` record.
   - **Conversion gate** (`verify_removed.py`), per part:
     - the removed text blocks equal stdout plus displayed values, then the error lines (substring match);
     - trailing spaces are ignored;
     - a removed picture is byte-identical to the stored PNG.
3. **Page-level changes:**
   - remove the old `run_code` definitions (ch02–ch05, ch07);
   - delete ch03's then-empty setup cell;
   - remove all `raises-exception` tags;
   - add `## Credits`.
4. **`review.sh sync`** writes the run cells (plain or wrapped), their stored outputs, the help note, the heading metadata and the stamp. Then the conversion gate of step 2 runs. `review.sh images` adds `data-svg-sha1` to the 19 example pictures (all in ch04); their PNGs must come out byte-identical (a conversion gate here). Counts: see the dry run below.

**Dry run here on all six pages: mechanical conversion only, VERIFIED.**
- Convert, sync, the gate and the full check pass on all six pages: 86 removed blocks, and 4 pictures byte-identical.
- One expected difference: ch04 Q15c's block was written on Python 3.13 and ends "Did you mean 'sides'?". Colab's Python 3.12 does not add that hint. The stored output shows what Colab shows, and the prose already explains the version difference. Needs Prof. Rosenthal's OK (D17).
- **Wrapping:** 25 wrapped run cells, the 24 raising cells plus ch07 Q14 (its doctest names a line). This replaces the earlier count of 24.

**Wording edits.** Each must match exactly once; any that don't are printed. Afterwards, grep **both question and Answer markdown** for `\bcells?\b`, `run (it|this)` and `run_code`, and review each hit. "Run this cell to define …" stays, since it is still true. ch02 Q4's Answer line "In a notebook cell, only the value of the *last* expression is displayed" stays too.

| Page / question | Old | New |
|---|---|---|
| ch02–ch05, ch07 intro | "Some questions show their code inside `run_code("""...""")`. … before you have made your prediction." | (deleted) |
| ch02 intro | "Run the next cell first: it imports `math` and defines `run_code`." | "The setup cell below imports `math`." |
| ch03 intro | "Run the next cell first: it defines `run_code`." | (deleted; no page setup cell) |
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
| ch07 Q15 | "(… then run it …)" | "(… then open the Answer to see the number …)" |

- No error-name prose edits are needed, because the records carry the names.
- Still to reread by hand: prose that leads into a removed block (ch02 Q14a, ch03 Q14).

The new intro sentences are true both in Colab (the help note sits between the intro and the setup cell) and on the site (the setup cell is shown, the help note is hidden). The instruction to run first moves into the help note. Optionally, ch02 Q14a's Answer can mention the NOTE that Colab adds to ModuleNotFoundError.

**Order.**
1. **ch05 first, as the pilot:** it has syntax errors, a RecursionError, a turtle tree and write-code questions.
2. **Then ch02, ch03, ch06 and ch07.**
3. **ch04 last.** It has 22 pictures, Q7's "assume restarted" premise, Q14's empty canvases, Q15's version-dependent message and Q18's `jump`.

**Cell ids.** Every cell that stays keeps its id.
- New: run cells, the help note, and the explanation, Part and summary cells split from the old `<details>`.
- Answer headings keep the old `<details>` id.
- Two Part-label cells are folded into their run blocks (V10).

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
