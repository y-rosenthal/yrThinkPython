# Plan: review pages that work with Colab's "Run all", with answers hidden until clicked

**Status (2026-10-08): the final plan is written (below). Nothing is implemented yet: the live review pages are unchanged.**

**Next step:** Prof. Rosenthal runs the Colab checklist Part A (section 7 of the plan, about 10 minutes, nothing needs pushing) and decides D1–D13 (section 9; each has a recommendation).

The review pages that are live today (2b–7b) are complete and working; this plan changes how
their questions and answers are laid out. Early research notes:
[runall-research-notes.md](runall-research-notes.md). Everything else the research produced (each
agent's report, the three candidate plans, the judges, the critics, the prototype and the helper
scripts) is on branch `yr-runall-research` in `yr/plans/research/`.

## To do

Step numbers refer to section 8 of the plan below.

- [x] Finish the plan (research, prototype, review) and write it into this file (Step 0)
- [x] Step 1a: Prof. Rosenthal ran Part A on prototype v1 (results above): Run all OK; Answers too repetitive
- [ ] Step 1b: build prototype v2 (no repetition); Prof. Rosenthal tests it in Colab and decides D1–D13
- [ ] Step 2: with his OK, push `colab-smoke-test`; he runs checklist Part B; adjust the plan if the results call for it
- [ ] Step 3: build the new tools (`review_format.py`, `sync_review.py`, new `check_review.py`, `turtle_images.py`,
      `prep_notebooks.py` guard, self-test), keeping old pages working
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

**2026-10-08, prototype v1** (chapter 5, opened from the `yr-runall-research` branch; Run all, then Answers opened):
- **Run all does not stop at caught errors (variant A works in Colab).** The page has 21 code cells; the screenshots show
  Question 8's three error cells numbered [9], [10], [11] and Question 2's cell [3], exactly their positions, and Question 1
  re-run later as [22]. So Run all executed every cell in order.
- **Problem: repetition.** Each Answer showed the expected output as text, then the question's code again in a code cell, then
  the real output again (Questions 1 and 2).
- **Problem: Question 8 "not exactly right".** The three run cells were bunched at the end of the Answer instead of next to each
  part; each showed the `run_code("""...""")` wrapper; each error appeared twice (text block and live output); tracebacks were
  headed `File "/tmp/ipykernel_.../...py", line 2` (off by one); each error cell had a red (!) icon and an "Explain error" button.
- **Response (in progress):** prototype v2, in which each Answer shows the real output **once**, next to its explanation: the
  repeated code is hidden (Colab form view, "Show code" still available), outputs are stored in the notebook (visible before
  Run all and on the website), and parts are interleaved. The plan sections below will be updated when v2 is reviewed.

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

**Status.**
- **Step 0 is done (2026-10-08).** This plan is in this file on `v3`. The research, the prototype and the agents' helper scripts (`make_smoke.py`, `exp.py`, `conv3.py`, `runvis.py`, the `final-rev` tests) are on branch `yr-runall-research` under `yr/plans/research/` (`scratch/` and `prototype/`). The virtualenv that the checkpoint script copied there by mistake was removed.
- **The live review pages are unchanged.** They still use the `run_code` layout published on 2026-10-08.
- **Next:** Step 1, Prof. Rosenthal runs checklist Part A and decides D1–D13.

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

- **Question.** Each question shows its code as **highlighted text**: a markdown block fenced with ```` ```python run ````.
  - Text can't be run, so Run all can't reveal an answer through it.
  - Colab's editor is BELIEVED never to check markdown, so nothing is underlined.
- **Answer.** Under the question, a small **`#### Answer` heading is saved collapsed**, for Colab and JupyterLab. It holds:
  - the explanation with the expected output, as today;
  - a **code cell that runs exactly the question's code**, so the student sees the real output when opening the Answer.
- **Errors.** Code whose result is an error is wrapped in `run_code(r"""…""")`.
  - The error looks like a normal cell's, and the kernel does not stop Run all (VERIFIED on Colab's kernel versions).
  - Whether Colab's browser side also lets Run all continue is UNKNOWN (test B4). A tested fallback is ready.
- **One copy of the code.** The question's code is typed once. `review.sh sync` generates everything derived from it, and `review.sh check` fails if anything is out of date.
- **Website.** Each Answer is folded back into today's closed "Answer" dropdown.

---

### 1. What students will see

#### Colab: opening a page from its "Run this page on Colab" link
- **Unchanged:** the title, the "Concepts covered" lists (still open) and the "Questions" intro look as today. The intro's setup sentence is reworded (section 5).
- **A short "Using this page in Colab or Jupyter" note,** hidden on the website. Its text is in section 2.1.
- **Setup cells.**
  - Most pages show two: the page's own setup cell, then a small cell defining `run_code`.
  - **ch03 shows only the `run_code` cell:** its old setup cell held nothing else and is deleted.
- **Each question shows:**
  - its heading and the prompt ("Predict what this code displays, then open the Answer to check.");
  - the code as a highlighted block;
  - multi-part questions show **Part a**, **Part b**, … above each block.
- **A closed Answer** under each question: a bold **Answer** heading with a "↳ N cells hidden" row.
  - **File format:** VERIFIED from real Colab-saved notebooks.
  - **Honoured when opened from GitHub:** BELIEVED (published course notebooks rely on it). Test A1/B1.
  - **Exact wording after Colab's January 2026 redesign:** UNKNOWN.
- **The only code cells outside the Answers:**
  - the setup cells;
  - "Run this cell to define `countdown_by_two`" cells, which display nothing;
  - the `# Your code here` cells of write-code questions.
- **No red underlines** before anything runs.
  - Question code is text: markdown is BELIEVED not to be sent to Colab's checker, and Pyright ignores code inside strings (VERIFIED).
  - Every visible code cell is valid, Pyright-clean code (`review.sh check` and V9 enforce this; the new `run_code` cell is Pyright-clean, VERIFIED).

#### Colab: after Runtime → Run all
- **First run:** Colab may first ask to confirm a notebook "not authored by Google" (BELIEVED; A2 records the exact text). Students choose **Run anyway**; the help note says so.
- **What runs:** every cell, including the hidden ones inside closed Answers. BELIEVED: a published notebook collapses its setup sections and still tells users to use Run all. Test A2/B3.
- **Run all reaches the end, kernel side:** `run_code` shows an error while the cell still counts as having succeeded.
  - VERIFIED on Colab's kernel versions (ipykernel 6.17.1, IPython 7.34.0), with cells queued the way Run all queues them. An unwrapped error aborts the remaining cells; a `run_code` error does not.
  - Whether Colab's **browser side** also stops on a red error output is UNKNOWN (B4). Fallback B is ready (section 10).
- **What stays visible:** only the setup cell's one-time "Downloaded jupyturtle.py" / "Downloaded words.txt" line (ch04, ch05, ch07). Every other output is inside a closed Answer.
  - VERIFIED in a Run-all simulation of all six prototype pages on both kernel stacks.
  - VERIFIED in a real JupyterLab 4.6.4 for the converted ch05 and a test notebook.
  - In Colab this is UNKNOWN until B3–B6.
- **Students' own code:** an error in a student's `# Your code here` code stops Run all there, as in any notebook.

#### Opening an Answer
- **How:** click the arrow next to **Answer**, or the "N cells hidden" row.
- **What appears:**
  - the explanation with the expected output (a text block or the stored turtle picture);
  - then the code cell, with the same code as the question and its real output: printed lines, a red traceback, the live turtle drawing, or a value like `12`.
- **Multi-part questions are interleaved:** "**Part a:** explanation", then Part a's live cell, then "**Part b:** …", and so on. A closing summary comes after the last live cell.
- **How errors look:** like a normal cell's error. There is no `run_code` frame, line numbers match the question's code, and syntax errors show the code line and a caret (VERIFIED on IPython 7.34 and 9.17).
- **If Run all wasn't used:** the Answer's cell has no output yet. The help note says to use Run all first; a single cell's ▶ also works after the setup cells have run.

#### Write-code questions
- **No change on the question side:** header, at least 2 examples, and the `# Your code here` cell.
- **The Answer:** the same closed heading, containing the suggested solution(s) as text. It has no run cell: one would overwrite the student's own function during Run all.

#### JupyterLab 4 / Notebook 7
- **Opening and Run all** (VERIFIED in JupyterLab 4.6.4 on the converted ch05 and a test notebook; Notebook 7 is BELIEVED, since it shares the same code):
  - the page opens with every Answer closed;
  - "Run All Cells" runs the hidden cells, and their outputs stay hidden.
- **Known side effect (VERIFIED):** pressing **Shift+Enter** onto a closed Answer heading opens it.
  - Questions are text now, so students don't need to step through cells.
  - The help note says to use Run all, and Ctrl+Enter for their own code.
  - Colab's behaviour is UNKNOWN (A4/B9).

#### The website (Jupyter Book; review pages are not executed there)
- **It should look as it does today:**
  - one closed **Answer** dropdown per question, with the same text and pictures;
  - no "Answer" entries in the right-hand contents list;
  - no new build warnings.
- **Evidence:** VERIFIED for the prototype variant (zero warnings; dropdown text identical to today's site). The prototype differed in two ways: it added a "Credits" contents entry, and it had no help cell, `remove-cell` managed cell or `run` fences. The final variant is checked by V7.
  - The ```` ```python run ```` fence itself renders as Python with no warning (VERIFIED with the book's MyST).
- **Hidden on the site:** the help note and the `run_code` cell.
- **One visible change:** question code shows as highlighted code blocks, like the examples already on the page, instead of a code-cell box. Decision D7 can keep the old look.

#### Other viewers
- **VS Code, "Colab in VS Code/Cursor" (launched January 2026), GitHub's notebook preview, nbviewer and classic Notebook 6:** these ignore the collapse markers we write, so Answers show open (BELIEVED, from source and experience). The help note says so; D11 accepts it.

---

### 2. Page layout, per kind of question

#### 2.1 Page skeleton, in order
1. **Title cell.** Same text, plus one sentence that works everywhere: "Each question has a suggested answer under **Answer**. Try the question first, then open the Answer."
2. **`## Concepts covered`**: unchanged.
3. **`## Questions` intro.**
   - The paragraph about `run_code("""...""")` is deleted.
   - "Run the next cell first: …" becomes a per-page sentence that is true in Colab and on the site (table in section 5).
4. **The help note**, a *managed* markdown cell tagged `remove-cell`. The website drops it, and `sync` writes the same text on all six pages. Draft text (final wording after A1/P7):
   > **Using this page in Colab or Jupyter**
   > - Start with **Runtime → Run all** (Jupyter: **Run → Run All Cells**). It runs the setup cells and the code in every Answer. The Answers stay closed, and Run all does not stop at the errors that are answers. If Colab warns that the notebook was not authored by Google, choose **Run anyway**.
   > - To check a question, click the arrow next to its **Answer**: you see the expected output and the code's real output. An Answer opened before Run all has no output yet.
   > - Run your own code with **Ctrl+Enter**.
   > - The real output reflects the notebook's current state. If your own code redefined a name that a question uses, the output can differ from the Answer.
   > - VS Code, GitHub's preview and nbviewer show the Answers open.
5. **The page's own setup cell**, tagged `setup`: imports and downloads.
   - The old `run_code` definition is removed from it.
   - ch03's setup cell becomes empty and is deleted.
6. **The managed `run_code` cell**, tagged `["setup", "remove-cell"]`. `sync` writes it, it is hidden on the website, and it now exists on every page, ch06 included.
7. **The questions.**
8. **`## Credits`** heading added to the existing credit cell.
   - Without it, the last Answer would swallow the credits.
   - The website build removes the heading line, so the site's contents list is unchanged (checked in V7).

#### 2.2 The building blocks (exact format, for Claude)

**Run block.** The question's code, written once. It is a markdown cell before the Answer holding one fenced block. In a multi-part question it starts with a part label.

~~~
**Part a**

```python run
x = 5
if x = 5:
    print('five')
```
~~~

- **The marker.** `run` says "the Answer runs this".
- **Other blocks.** Plain ```` ```python ```` blocks are never run by the Answer: examples, headers, refactor questions' given code, solutions.
- **Rendering.** Markdown renderers use only the first word after the fence: VERIFIED on the site, BELIEVED in Colab (test B2).

**Answer heading.** Collapsed for Colab and JupyterLab. `metadata.id` equals `id`, which is what Colab itself writes for nbformat 4.5 files.
```json
{"cell_type": "markdown", "id": "9c41e7b2",
 "metadata": {"id": "9c41e7b2", "jp-MarkdownHeadingCollapsed": true},
 "source": ["#### Answer"]}
```

**Run cell.** A code cell inside the Answer, generated by `sync`.
- Plain code if the code runs without error; otherwise wrapped in `run_code`.
- No tags and no comment lines: an added line shifts traceback and doctest line numbers.
```json
{"cell_type": "code", "id": "3f0a77c1", "execution_count": null, "metadata": {}, "outputs": [],
 "source": ["run_code(r\"\"\"\n", "x = 5\n", "if x = 5:\n", "    print('five')\n", "\"\"\")"]}
```

**Managed `run_code` cell.** `review_format.RUN_CODE_CELL`, byte-identical on every page.
- **Pyright:** clean in both basic and off modes (Pyright 1.1.414). The old bare `get_ipython()` was flagged "not defined".
- **Kernels:** on IPython 9.17 and on 7.34/ipykernel 6.17.1 the result is the same:
  - SyntaxError, ZeroDivisionError and ModuleNotFoundError show as errors with reply status "ok";
  - `price * 3` shows `12`;
  - the next cell runs.
- **Plain Python:** it just runs the code.

All of this is VERIFIED (`scratchpad/ultra/final-rev/`).
```python
def run_code(code):
    """Run code (a string) as if it were a cell of its own.

    Some Answers use it for code whose result is an error: the error is shown as
    usual, but it does not stop Runtime > Run all.
    """
    try:
        from IPython import get_ipython
        ip = get_ipython()
    except ImportError:
        ip = None
    if ip is None:                    # plain Python (the review tools): just run it
        exec(code, globals())
        return
    result = ip.run_cell(code, store_history=False)
    if isinstance(result.error_in_exec, KeyboardInterrupt):
        raise KeyboardInterrupt       # the Stop button still stops Run all
```

**Notebook metadata.** `collapsed_sections` lists exactly the Answer heading ids, in page order; `sync` writes both.
```json
"metadata": {"colab": {"collapsed_sections": ["9c41e7b2", "…one per Answer…"]},
             "kernelspec": {"display_name": "Python 3 (ipykernel)", "language": "python", "name": "python3"},
             "language_info": {"name": "python"}}
```

#### 2.3 Tiny examples

Cells are listed top to bottom; `[md]` is markdown, `[code]` is code.

**What is displayed** (most of the 69 predict questions). With one run block, the run cell goes at the end of the Answer.
~~~
[md]   ### Question 1 (easy): what is displayed?
       What does this code display? Predict, then open the Answer to check.
[md]   ```python run
       x = 3
       if x > 2:
           print('big')
       print('done')
       ```
[md]   #### Answer                                   <- saved collapsed
[md]   ```text
       big
       done
       ```
       x > 2 is True, so the first print runs ...
[code] x = 3                                         <- generated; plain (no error)
       if x > 2:
           print('big')
       print('done')
~~~

**Errors, several parts** (ch05 Q8; also ch02 Q9, Q10, Q14, ch03 Q10, ch04 Q14, Q15):
~~~
[md]   ### Question 8 (medium): find the error
       Each part has one mistake. Predict the error for each, then open the Answer to check.
[md]   **Part a**  + ```python run  x = 5 / if x = 5: / print('five') ```
[md]   **Part b**  + ```python run  ... ```
[md]   **Part c**  + ```python run  ... ```
[md]   #### Answer
[md]   **Part a:** `=` assigns; comparing needs `==`:  ```text SyntaxError: invalid syntax. ...```
[code] run_code(r"""
       x = 5
       if x = 5:
           print('five')
       """)
[md]   **Part b:** ...
[code] run_code(r"""...""")
[md]   **Part c:** ...
[code] run_code(r"""...""")
[md]   Each is found before any of that part's code runs, so nothing is displayed or assigned.   <- summary cell
~~~

**Placement rule** (used by `normalize` and `lint`), for a question with 2 or more run blocks:
- every run block starts with `**Part a**`, `**Part b**`, …;
- the Answer has exactly one markdown cell starting with `**Part a:**`, one with `**Part b:**`, …, in order;
- run cell *x* goes right after the `**Part x:**` cell;
- markdown cells after the last part cell are **summary cells** and go after the last run cell;
- text that belongs to a part stays inside that part's cell.

Parts that run without error (ch02 Q9 a and e, ch04 Q14 c) are plain cells.

**Last value shown** (ch02 Q4 `price * 3`, ch03 Q9 `greet`):
- Same layout as "what is displayed". The plain run cell shows `12`, and the check now verifies it.
- ch02 Q4's Answer gets the missing ```` ```text 12 ``` ```` block.

**Wrong calls** (ch03 Q10, Q14; ch04 Q14, Q15; ch05 Q14; ch06 Q15):
~~~
[md]   ### Question 14 ... prompt
[code] def countdown_by_two(n): ...          <- "Run this cell to define it"; stays a code cell; must display nothing
[md]   Two correct ways to call it: ```python ... ``` ```text ... ``` (x2)
[md]   ```python run
       countdown_by_two(5)
       ```
[md]   #### Answer
[md]   explanation (+ the fixed function as a ```python block)
[code] run_cell(r"""
       countdown_by_two(5)
       """)
~~~

**What is drawn** (ch04 Q2, Q6, Q7; ch05 Q17):
- **Question:** a run block starting with `make_turtle()`.
- **Answer:** the explanation with `<img data-turtle … src="data:…">`, drawn by `sync` from the question's run block; the website shows it.
- **Run cell:** draws live, visible only when the Answer is open.
- **Empty canvases need no picture.** ch04 Q14's parts call `make_turtle()` and then fail or draw nothing. Their canvases have 0 `<line>` elements (VERIFIED), and the Answer has no picture.

**Doctest** (ch07 Q14):
- One run block with the whole program.
- The run cell is plain (the code doesn't raise) and byte-identical to the block, so the report's `line 9` stays right.
- **Rule:** `run_code` strings may never contain `>>>` lines. IPython 8 and later strips them even inside strings (VERIFIED on 9.17).

**Write code** (34 questions):
~~~
[md]   ### Question 4 (easy): write a function
       Write sign(n) ... header block ```python def sign(n): ... ```, 2+ examples (```python + ```text or a picture)
[code] # Your code here
[md]   #### Answer
[md]   ```python  def sign(n): ...  ``` + explanation          <- no run cell
~~~

**Refactor / generalize / simplify** (ch03 Q12; ch04 Q11, Q17, Q18, Q19; ch06 Q12): the given code is a plain ```` ```python ```` block, without `run`, so it is never run. The prototype's guessing rule misfired on exactly these six questions (VERIFIED).

**Reading a file** (ch07 Q9, Q15): same as "what is displayed"; words.txt comes from the setup cell.

#### 2.4 Format rules (go in the README; enforced by `review.sh check` and `check_notebooks.py`)
1. **Extent of a question:** from `### Question N (level): kind` to the next heading of level 1–3.
2. **One Answer heading:** exactly one cell whose whole source is `#### Answer`.
3. **No other headings inside a question.** That means no `#`–`######`, no setext `===`/`---` underlines and no HTML `<h1>`–`<h6>`, checked outside code fences. A heading inside an Answer ends the closed section early (VERIFIED, mutation M3).
4. **Run blocks:** only before the Answer heading, one per markdown cell, holding valid fenced code. With 2 or more, each starts with `**Part x**`, and the placement rule of 2.3 applies.
5. **Code cells before the Answer heading:** only setup cells, definition cells (must parse, display nothing, raise nothing) and `# Your code here`.
6. **Code cells inside an Answer:** only generated run cells.
7. **Answer pictures:** a picture with no ```` ```python ```` block above it in its cell shows what the question's run block draws. Allowed only when the question has exactly one run block.
8. **End of page:** the page ends with `## Credits`.
9. **Tags:** only `setup`, `no-signature` and `remove-cell` (managed cells only). `raises-exception` is no longer used.
10. **Hands off:** never edit run cells or managed cells by hand; edit the run block and run `review.sh sync`.
11. **Answers that are NameErrors stay true when cells run again.** A name that a run cell's NameError reports may not be bound at module level by any *other* code cell or run block on the page. Today's three cases pass (ch03 Q10a `total`, ch04 Q7 `jupyturtle`, ch07 Q8 `num_letters`; VERIFIED with an `ast` scan). The help note covers names that students define.

---

### 3. Don't Repeat Yourself: how the code stays in one place

- **Single source.** The question's code is written **once**, as a ```` ```python run ```` block. This is option A, with an explicit marker.
  - **Why a fence and not a cell tag:** it is part of the text, so it survives any editor and is visible to authors.
  - **Fallback:** if B2 shows Colab renders it badly, switching to a tag is one constant in `review_format.py`.
- **One command derives everything else: `yr/tools/review.sh sync NB`.**
  1. **normalize** (static, stdlib-only, in `review_format.py`) regenerates:
     - the run cells, placed by the rule in 2.3, keeping existing ids and wrapped/plain state;
     - the two managed cells;
     - the Answer heading metadata and `colab.collapsed_sections`;
     - it strips outputs and execution counts;
     - it drops metadata Colab adds on save: `executionInfo`, `outputId`, `colab` on cells, and `metadata.id` except on Answer headings.
  2. **Run the page once** (nbclient). Wrap each run cell that produced an error in `run_code(…)`, and unwrap any wrapped cell that didn't.
  3. **Quoting.**
     - Use `r"""…"""`, or `r'''…'''` when the code contains `"""`.
     - Check that `ast.literal_eval` gives back exactly the code.
     - **Refuse with a clear message** if the code contains both quote styles, ends with a backslash, or contains `>>>` lines.
  4. **Pictures.** For each picture, compute jupyturtle's SVG and its SHA-1, stored in the tag as `data-svg-sha1="…"`.
     - The PNG is re-rendered only when the hash changes, so a different cairo library on another machine doesn't rewrite all 23 pictures.
     - The attribute name avoids the text `data-turtle`, which `verify_live.py` counts.
  5. **Second run.** Running `sync` again changes nothing.
- **`review.sh check NB` fails if `sync` would change anything.**
  - **Static part:** "normalize is a no-op". Run cells are compared with run blocks after unwrapping with `ast`. This also runs in `check_notebooks.py` and CI.
  - **Runtime part:** "wrapped exactly when it raises".
  - **Pictures:** `turtle_images --check` compares SVG hashes, so it gives the same answer on any machine.
- **Rejected options:**
  - **B,** code in a string variable `q8a = """…"""`: one-colour question text, `q8a = """` on the site, and the Answer depends on the question cell having run.
  - **C,** reading the notebook file at run time: doesn't work in Colab.
  - **A custom `%%run_question` magic:** it works in IPython (VERIFIED). But Colab has an "unsupported magics" check, linted `%%writefile` bodies in 2022, and may show unknown magics uncoloured. E6 records Colab's behaviour; only `render_run_cell` would change.
  - **`# type: ignore` in question cells:** not needed (question code is text), and probably ineffective in Colab, which most likely joins cells into one document.

---

### 4. Tool, README and skill changes

#### 4.1 New `yr/tools/review_format.py`
- **Stdlib only, and must run on Python 3.12:** CI runs prep and `check_notebooks.py` with Python 3.12 (`deploy-book.yml`). It defines the format in one place.
- **Imported by:** `review_cells.py`, `sync_review.py`, `check_review.py`, `turtle_images.py`, `check_notebooks.py`, and `jb/prep_notebooks.py` (via `sys.path`).
- **Constants:** `ANSWER_HEADING`, `RUN_FENCE`, `PLACEHOLDER`, `CREDITS_HEADING`, `HELP_CELL`, `RUN_CODE_CELL`, and an `EXAMPLE` regex that never stretches across blocks and never counts run blocks.
- **Helpers:**
  - `source(cell)`;
  - fence-aware `headings(md)`;
  - `run_blocks(md)` (with part labels);
  - `render_run_cell(code, wrapped)`;
  - `unwrap(src)` (ast-based);
  - `parse_page(cells)`: setup cells, managed cells, questions (question cells, run blocks, definition cells, placeholders, Answer heading, part cells, summary cells, run cells) and the credits cell.
- **`normalize(nb)`:** returns the list of changes, with a diff for any run cell it rewrites.
- **`lint(nb)`:** static rules 2.4, plus "normalize would change …".
- **`page_format(nb)`:** returns `new`, `old` or `mixed` (`mixed` is an error).

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
- **`new` skeleton:** title sentence, help cell, setup cell, `run_code` cell, `## Credits`, and `"colab": {"collapsed_sections": []}`.
- **Docstring:** full spec examples, including a multi-part error question with a summary.

#### 4.3 New `yr/tools/sync_review.py`, run as `review.sh sync NB…`
Implements section 3. It needs the venv (nbclient), like `check`.

#### 4.4 `yr/tools/check_review.py` (new-format path)
**How it runs.** One execution with `allow_errors=True`. nbclient's `on_cell_executed` hook (nbclient 0.11.0, VERIFIED) records every cell's reply status. This gives full outputs and an exact model of where Run all would stop, ignoring tags as Colab does.

**What counts as an error line:**
- error lines come from `error` outputs, and from the ANSI-stripped stderr of a run cell;
- for stderr, the check takes the **last line matching the exception regex**, not the literal last line, because Colab appends a NOTE after ModuleNotFoundError (VERIFIED in simulation);
- so switching to fallback B can't silently disable the checks (mutation M15).

**Rules** (none of today's checks is weakened; several gaps are closed):
1. **Run all reaches the end:** no cell has reply status "error".
2. **Nothing visible after Run all:** every code cell with output, except the stdout of `setup` cells, sits inside a collapsed Answer. This uses the real section rule.
3. **Visible cells are harmless:**
   - definition cells parse, display nothing and raise nothing;
   - placeholders are exactly `# Your code here`;
   - no visible code cell has a syntax error.
4. **Wrapped exactly when it raises** (restores today's "tagged but raised nothing" guard).
5. **Live output matches the Answer text:**
   - **stdout and values:** a run cell's stdout plus any `execute_result` text, in output order, equals one ```` ```text ```` block exactly. **New:** closes the unchecked `12` in ch02 Q4 and ch03 Q9.
   - **error lines:** every error line appears in a text block (substring match, so wording differences between Python versions are tolerated).
   - **New, reverse rule:** every Answer text-block line matching `^(?:[A-Z]\w*)?(?:Error|Exception|Warning|Interrupt|Exit|Iteration)\b` must match an error produced by a run cell (substring, either direction).
     - It matches per part: a Part x cell's lines against run cell x; summary cells against the whole question.
     - VERIFIED on today's six pages: 24 such lines, 0 unmatched. This closes mutation M1.
   - **New, pictures:** a run cell whose live drawing is non-empty must have a data-turtle picture in its Answer. Non-empty means the SVG has at least one `<line>` element. Empty canvases need none (ch04 Q14).
   - **New:** stderr that isn't a traceback and isn't in the Answer is reported.
6. **Standalone Answer blocks:** each ```` ```python ```` block in an Answer runs as a standalone `.py` file (existing).
7. **Write-code questions:** a header plus at least 2 examples (existing). Examples are counted in prose only; these questions have no run blocks or run cells.
8. **Wrong-call questions** (a run cell raises and the question defines a function): at least 2 correct calls (existing).
9. **Pictures:** up to date (SVG hash) and not empty.
10. **No hazard symbols:** no `(c)`, `(r)`, `(tm)`, `+-` (existing).
11. **Static rules** from `review_format.lint`, including rule 2.4.11 (NameError names).

**Option `REVIEW_PYTHON=/path/to/python`.** Runs the kernel with that interpreter through a temporary kernelspec, so nothing is installed into the user's Jupyter config. Used with the Colab-like venv (section 6, V1).

#### 4.5 `yr/tools/turtle_images.py`
- **What it runs:** it uses `parse_page`. Per question it runs:
  1. the setup cells (the managed `run_code` cell only defines a function);
  2. the Answer's ```` ```python ```` blocks;
  3. the definition cells and run blocks, in page order.
  - It **never runs run cells**.
- **Picture rule:**
  - use the nearest ```` ```python ```` block above the picture in the same cell;
  - otherwise use the question's single run block;
  - with 0 or 2+ run blocks, it reports an error instead of guessing.
- **SVG hash:** it writes `data-svg-sha1` and re-renders the PNG only when the hash changes.
- **New `--check`:** compares hashes, writes nothing, and exits 1 on any difference.
- **Hardening:** if an example picture's code raises, it exits 1 without writing anything. Today's tool silently rewrote 19 ch04 pictures with partial drawings on the new layout (VERIFIED).

#### 4.6 `jb/prep_notebooks.py` (`process_review`)
1. Drop `# Your code here` cells (as now).
2. `raw_pictures` and `details_to_dropdown`, as now. The concept lists stay `toggle-shown` dropdowns, and old-format pages use the same path.
3. **New `answer_sections`:**
   - merge each `#### Answer` heading and its markdown cells into one `:::{admonition} Answer` / `:class: dropdown` cell, keeping the heading's id;
   - drop the run cells;
   - each markdown cell is parsed separately, so a dropdown can't span cells (VERIFIED).
4. **New:** remove the `## Credits` line from the credit cell.
5. `process_cell` (as now). Never tag run cells `solution`: prep would blank them.
6. **New guard.** Stop the build with a clear message if:
   - a `#### Answer` heading survives;
   - a code cell sits inside a question's Answer;
   - **the number of dropdowns titled exactly "Answer" ≠ the number of `### Question` headings.**

   The concept-list dropdowns ("Python Syntax and Semantics", …) are not counted. Without the guard, new pages with old tools publish every answer openly with zero warnings (VERIFIED risk).

The managed cells are removed by myst-nb's standard `remove-cell` tag; V7 checks this.

#### 4.7 Other files
- **`.claude/skills/check-notebooks/check_notebooks.py`:** for `yr/*.ipynb`, call `review_format.lint(nb)`. `KNOWN_MAGICS` is unchanged.
- **`.claude/skills/check-notebooks/run_notebooks.sh`:** skip `yr/` pages and point to `review.sh check`. Its tag logic (line 62) would report the caught errors as failures (VERIFIED in simulation).
- **`.claude/skills/yrpublish/verify_live.py`:** today it only checks that the word "Answer" appears (line 55), so answers published openly would pass. New checks per `yr/` page:
  - the number of "Answer" dropdowns equals the number of `### Question` headings in the local notebook, and none is open;
  - there are no `h4` headings;
  - there are no "Answer" or "Credits" contents entries;
  - there is no `def run_code` and no help-note text;
  - optionally, fetch the raw v3 notebook and check that `colab.collapsed_sections` lists every Answer heading.
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
  - **Mutations:**
    - M1: a part edited so it no longer raises, while the Answer still claims an error;
    - M2: `price*3` changed to `price*4` in the run block and the run cell, with the Answer unchanged;
    - M3: `#### Note` inside an Answer;
    - a setext heading in an Answer;
    - an HTML `<h4>` in an Answer;
    - M15: the stderr `run_code` combined with wrong error text;
    - the stderr variant with a Colab-style NOTE after the error line (must still parse);
    - a run block edited without running sync;
    - run cells swapped;
    - a summary cell placed before the last run cell;
    - a wrapped cell that doesn't raise;
    - a plain cell that raises;
    - a missing collapse key;
    - a stale id in `collapsed_sections`;
    - `## Credits` removed;
    - a `raises-exception` tag left in;
    - a `>>>` line inside `run_code`;
    - a definition cell that prints;
    - a visible syntax error;
    - an Answer block that isn't standalone;
    - wrong expected stdout;
    - missing error text;
    - a wrong-call question with one correct call;
    - a write-code question with one example;
    - a non-empty drawing with no picture (must fail); an empty canvas with no picture (must pass);
    - a stale `data-svg-sha1`;
    - a NameError name bound by another cell;
    - a managed cell edited;
    - a leftover `<details>` Answer.

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
    - "Tools" (`sync`, `normalize`, `selftest`, `--check`, `REVIEW_PYTHON`, and how to make the Colab-like venv);
    - the `review.sh check` list;
    - "How the build handles yr/".
  - **The file tree at the top:** add `review_format.py`, `sync_review.py`, `selftest_review.py`, `selftest/` and the temporary `legacy` module.
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

**The script.** A one-off script based on the prototype's `convert.py` and `plan-maint/conv3.py`. Step 0 saves it on `yr-runall-research`; it is not committed to v3 (D13). For each page:
1. **Question code cells.** Every question code cell that isn't `# Your code here` and isn't definition-only becomes a run-block markdown cell **with the same id**.
   - "Definition-only" means: by `ast`, only def/class/import/assignment, no output in an executed copy, and not tagged `raises-exception`. It finds exactly the 6 definition cells (VERIFIED).
   - The `run_code("""…""")` wrapper is removed with `ast`.
   - A trailing `**Part x**` line in the cell above, or a `**Part x**` cell, is folded into the run-block cell.
2. **The old `<details>` Answer** becomes a new `#### Answer` heading plus explanation cell(s); the first keeps the old id.
   - For multi-part questions, the body is split before each `**Part x:**` paragraph.
   - **Summary paragraphs are split off into their own trailing cell, using an explicit list.** The tails were read (VERIFIED):

     | Question | The summary starts with |
     |---|---|
     | ch02 Q10 | "All three are a `TypeError`." |
     | ch02 Q14 | "A syntax error (here, a space in a name)…" |
     | ch04 Q14 | "In all three parts the caller broke a precondition…" |
     | ch04 Q15 | "Some correct calls: …" |
     | ch05 Q8 | "All three are found before the cell runs…" (reworded below) |

     - ch02 Q9's last paragraph is about part e and stays in the Part e cell. ch04 Q15's "(Python versions before 3.13 …)" stays in the Part c cell. ch03 Q10 has no summary.
   - All 7 multi-part questions are printed for a manual look.
3. **Page-level changes:**
   - remove the old `run_code` definitions (ch02–ch05, ch07);
   - delete ch03's then-empty setup cell;
   - remove all `raises-exception` tags;
   - add `## Credits`.
4. **`review.sh sync`** adds the run cells, wrapping, managed cells, metadata and picture hashes.
   - **Wrapping:** of the 21 existing `run_code` cells, the 19 that raise stay wrapped, and ch02 Q9 parts a and e become plain. The 5 plain raising cells become wrapped: ch03 Q14, ch04 Q14 a and b, ch05 Q14, ch06 Q15. That makes **24 wrapped run cells, one per raising cell** (VERIFIED counts).
   - **Pictures:** in this container all 23 stored PNGs (22 in ch04, 1 in ch05) must come out byte-identical. This is a conversion gate here, not a rule `check` enforces elsewhere.

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
| ch02 Q4 | "What does this cell display when you run it in a notebook?" | "What does this code display when it is run as a notebook cell?" (+ ```` ```text 12 ``` ```` in the Answer) |
| ch02 Q9 | "For each cell, predict …" | "For each part, predict …" |
| ch02 Q14 | "Each cell has an error …" / "what each cell displays before the error" | "Each part has …" / "what each part displays …" |
| ch03 Q9 | "What does this cell display in a notebook?" | "What does this code display when it is run as a notebook cell?" |
| ch03 Q10, ch04 Q14 | "For each of the next three cells" | "For each of the three parts" |
| ch03 Q14 Answer | "first the line `outer('hi')` in the cell" | "first the line `outer('hi')` in the question's code" |
| ch04 Q7 | "… run only the setup cell … and this cell" | "… run only the setup cells (at the start of the Questions), and then this code" |
| ch05 Q8 | "Each cell has one mistake." | "Each part has one mistake." |
| ch05 Q8 Answer | "All three are found before the cell runs, so nothing is displayed or assigned." | "Each is found before any of that part's code runs, so nothing is displayed or assigned." |
| ch07 Q15 | "(… then run it …)" | "(… then open the Answer, which runs it …)" |

The new intro sentences are true both in Colab (the help note sits between the intro and the setup cell) and on the site (the setup cell is shown, the `run_code` cell is hidden). The instruction to run first moves into the help note. Optionally, ch02 Q14a's Answer can mention the NOTE that Colab adds to ModuleNotFoundError.

**Order.**
1. **ch05 first, as the pilot:** it has syntax errors, a RecursionError, a turtle tree and write-code questions.
2. **Then ch02, ch03, ch06 and ch07.**
3. **ch04 last.** It has 22 pictures, Q7's "assume restarted" premise, Q14's empty canvases, Q15's version-dependent message and Q18's `jump`.

**Cell ids.** Every cell that stays keeps its id. Only Answer headings, run cells, summary cells and managed cells are new.

---

### 6. Verification here, before anything reaches you

- **V1. Checks on two stacks.** `review.sh check` must pass on every converted page on:
  - **(a) the book venv** as `ensure_venv.sh` creates it: system Python 3.12 on your laptop (build-book SKILL.md), Python 3.13 / IPython 9.17 in this container;
  - **(b) a Colab-like kernel** via `REVIEW_PYTHON`: Python 3.12, `ipython==7.34.0`, `ipykernel==6.17.1`, `jupyter_client==7.4.9`. This stack is VERIFIED here.
  - The README gives the recipe: `python3.12 -m venv ~/.venvs/colablike && ~/.venvs/colablike/bin/pip install ipython==7.34.0 ipykernel==6.17.1 jupyter_client==7.4.9`. The recipe is BELIEVED; it is tested in Step 3. The scratchpad venvs are temporary.
- **V2. Nothing changed.** For all 103 questions, compare stdout, error lines, displayed values and turtle displays between old and new pages, on both stacks (`exp.py`, saved in Step 0). Expect 0 differences except the intended ones.
- **V3. Run-all simulation.** nbclient with `allow_errors=False` and `force_raise_errors=True`, ignoring tags as Colab does, on both stacks (`runvis.py`, saved in Step 0). It must reach the end with no visible output except the setup lines.
- **V4. Idempotent.** A second `sync` changes nothing; `turtle_images --check` reports 0 differences; ids are preserved.
- **V5. Self-test.** `review.sh selftest` catches every mutation.
- **V6. Lint.** `check_notebooks.py` passes, including the new lint, on Python 3.12 as in CI.
- **V7. Website.** `build_book.sh` gives no warnings beyond `known_warnings.txt`. A script over `yr/chap0*_review.html` asserts:
  - "Answer" dropdowns equal the number of questions (17/16/19/17/17/17) and none is open, while the concept-list dropdowns are unchanged;
  - 0 `h4` headings, and 0 "Answer" or "Credits" contents entries;
  - no help text and no `def run_code`;
  - dropdown text identical to today's site, except ch02 Q4.

  For pages still in the old format: prep's output notebooks (`jb/yr/*.ipynb` after `prep_notebooks.py`) must be identical with old and new tools; identical HTML is a nice-to-have. Screenshots: ch04 Q2 and Q14, ch05 Q8 and Q17, ch07 Q14, with the D7 alternative side by side.
- **V8 (pilot only).** Headless JupyterLab 4.6.4: the page opens collapsed, and Run All keeps outputs hidden.
- **V9. Pyright.** Run it on every visible code cell together with the cells above it. Expect nothing beyond the known jupyturtle import note; the new `run_code` cell is clean (VERIFIED).
- **V10. Diff.** `git diff` touches only the intended files, no outputs are stored, and ids are preserved.

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

#### Part A: today, nothing needs pushing (about 10 minutes)
Open the prototype chapter 5 page, already on the research branch (the URL returns HTTP 200, VERIFIED):
`https://colab.research.google.com/github/y-rosenthal/yrThinkPython/blob/yr-runall-research/yr/plans/research/prototype/out/all/chap05_review.ipynb`

**How the prototype differs from the final design.** Part A still tests the key questions: collapse on open, Run all, live answers and the keyboard. The differences:
- question code sits inside the heading cell, not in separate run-block cells;
- the code blocks lack the word `run`;
- the run cells sit at the end of each Answer, not next to each part;
- `run_code` is appended to the setup cell, with no plain-Python fallback, no Stop fix and no raw strings;
- there is no help note.

1. **A1. Closed on open.** Before running anything: is every Answer closed, with an "N cells hidden" row? Write down the exact wording. [shot]
2. **A2. Run all.** Choose Runtime → Run all.
   - If a "not authored by Google" warning appears, write down its exact text and choose Run anyway.
   - Wait until nothing is running.
   - Did it stop anywhere, or show an error popup?
   - Did any Answer open by itself, or did the page jump into one?
   - Is anything visible outside the Answers besides "Downloaded jupyturtle.py"?
   - How long did it take? [shot]
3. **A3. Live answers.**
   - Open Q8: are there three errors (SyntaxError, SyntaxError, IndentationError), each shown once?
   - Open Q14 (RecursionError, expected to be short) and Q17 (a stored picture plus a live drawing). [shot]
4. **A4. Keyboard.** Reload the page. Click Question 1's text and press **Shift+Enter** repeatedly through Question 3: does an Answer open? Repeat with the **Down arrow**, then with **Ctrl+Enter** followed by Down.

#### Part B: smoke-test notebooks (about 20 minutes; needs your OK to push branch `colab-smoke-test`, which never deploys)
**Before pushing, the generator `make_smoke.py` is updated:**
- it uses ```` ```python run ```` and the final `run_code`;
- it adds failing-import tests;
- it **reorders** the tests, so tests that cannot stop Run all come first;
- it is committed with the notebooks.

Each test is followed by a visible MARKER cell.

**Notebook 1** (`colab_tests/colab_test_runall.ipynb`). Test order:
- **Tests 1–3: collapse markers.** Test 1 has all markers; Test 2 only Colab's list with the top-level id; Test 3 only the JupyterLab key.
- **Tests 4–5: no errors.** Test 4 is the last value `12`; Test 5 is a turtle square.
- **Test 6: fallback C.** "Show the output" boxes, including a failing import.
- **Tests 7–9: variant B** (traceback on stderr): a syntax error; a print then a NameError; a failing import.
- **Tests 10–12: variant A** (normal red error): a syntax error; the outer/inner traceback order; a failing import.
- **END.**

Checks:
5. **B1.** Before running: which of Tests 1–3 are closed? Is any "SECRET n" text visible without clicking?
6. **B2.** Do the question code blocks look like normal highlighted Python, without the word "run"?
7. **B3.** Run all. Which "MARKER n" lines appear, and is "END" printed?
   - **If Run all stopped at Test N:** click the first cell after Test N, choose Runtime → Run cell and below, and repeat until END.
   - Write down every stop.
8. **B4.** Did Run all get past Tests 10–12 (variant A) without help? Past Tests 7–9 (variant B)?
9. **B5.** Without clicking anything: is there a red icon or mark on any Answer heading, its "cells hidden" row, or the contents sidebar? Compare Tests 7–9 with Tests 10–12. [shot]
10. **B6.** Is any "LIVE n", traceback or drawing visible outside an Answer?
11. **B7.** Open each Answer and check:
    - Test 4 shows `12`;
    - Test 5 shows a square;
    - Tests 7–9 show stderr-style text, and Test 9 includes Colab's NOTE;
    - Test 10 shows the error, Test 11 lists `outer` before `inner`, and Test 12 includes the NOTE. [shot]
12. **B8.** Test 6: do both "Show the output" boxes open and show their contents, including the import error?
13. **B9.** Reload. Step through Test 4 with Shift+Enter, then with the Down arrow, then with Ctrl+Enter. Which ones open the Answer?
14. **B10.** Copy the setup cell's version line (for example `Python 3.12.x | IPython 7.34.0 | ipykernel 6.17.1`).
15. **B11.** File → Save a copy in Drive. Open one Answer in the copy and save. Then File → Download .ipynb and send the file: it shows what Colab writes when it saves.

**Notebook 2** (`colab_test_editor.ipynb`; don't run it, just press Connect):
16. **E1–E7.** Click into each cell and wait 5 seconds. Is it underlined? Is it coloured?
    - E6 is a custom `%%magic`: is there an "unsupported magic" warning?
    - Repeat with Tools → Settings → Editor → Code diagnostics set to "Syntax and type checking". Write down every option in that list and which one is the default, then restore the default.

**Notebook 3** (`colab_test_stop.ipynb`):
17. **S1.** Run all, then press Stop (Runtime → Interrupt) after about 10 seconds. Pass = "END" never appears. A doubled KeyboardInterrupt message is expected.

#### Part C: the real chapter 5 pilot (about 15 minutes, from branch `yr-review-runall`)
`https://colab.research.google.com/github/y-rosenthal/yrThinkPython/blob/yr-review-runall/yr/chap05_review.ipynb`

18. **P1.** On opening: all 17 Answers closed, question code shown as text, the help note visible, no underlines anywhere.
19. **P2.** Run all (accept the "not authored by Google" warning) reaches the end. Afterwards nothing is visible except "Downloaded jupyturtle.py".
20. **P3.** Q8 shows three live errors interleaved with their Part a/b/c explanations, then the summary.
21. **P4.** Q14 shows the RecursionError; Q17 shows the stored and the live tree.
22. **P5.** Q9 (write code): your own code in `# Your code here` runs with Ctrl+Enter, and the Answer shows the solution text.
23. **P6.** Close an Answer again: it hides again.
24. **P7.** Does the help note's wording match what you saw (arrow, "cells hidden", the warning dialog)? Suggest changes.

#### What the results decide
| Result | Action |
|---|---|
| A1/B1 Test 1 closed; A2/B3 END reached without help; B5/B6 clean | Main design, variant A (normal red tracebacks) |
| B3/B4: Run all stops at Test 10, 11 or 12 (variant A blocks it) | Switch `run_code` to variant B with the ColabTraceback unwrap (section 10). One function changes; the checks already read stderr |
| B5 shows red marks only on Tests 10–12 | Switch to variant B, so nothing hints which Answers are errors |
| B1: Test 2 also closed | No change; keep writing `metadata.id` (harmless) |
| A1/B1: Test 1 **not** closed, or A2/B3 open Answers by themselves | Fallback C (section 10) |
| A4/B9: Shift+Enter or Down opens Answers | Keep the design; help note says "use Run all; run your own code with Ctrl+Enter" (D10) |
| B2: the word "run" shows, or there is no colour | Switch the marker to a cell tag (one constant) |
| E6 clean, and you dislike the `run_code(r"""…""")` look inside Answers | Optional later switch to the `%%run_question` magic (one function) |
| S1: END printed | Investigate; minor, documented |
| B10 shows IPython 8 or later, or Python 3.13 | Re-run V1(b) with that version; nested `run_cell` already looks normal on 9.17 |

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
1. **Step 1, today.** You run Part A and decide D1–D13 (the defaults are the recommendations).
2. **Step 2.** With your OK, push `colab-smoke-test`, and you run Part B. If the results call for variant B or fallback C, the plan is adjusted before any page is touched.
3. **Step 3.** Branch `yr-review-runall` from `origin/v3`.
   - **Build:**
     - `review_format.py`, `sync_review.py`, the new `check_review.py` and `turtle_images.py`, with legacy paths;
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
   - stop the checkpoint script if it is still running (it exits by itself when the workflow finishes), then `git worktree remove` the scratchpad worktree `v3wt`;
   - with your OK, delete the `colab-smoke-test` and `yr-runall-research` branches.
     - **`yr-runall-research` must never be merged.** It contains a committed Python venv: 2,525 files under `prototype/venv-colablike/` (VERIFIED).
     - Keep it until Part A is done, since Part A's link points at it.

**Rollback.** `git revert` of a page commit on v3 brings back the old page. The tools read both formats until Step 7, the site redeploys on push, and Colab links follow v3 immediately. A bad tools commit is reverted the same way.

---

### 9. Decisions needed from you (recommendation first)

- **D1. The overall design.** Question code as text; a closed Answer heading with the explanation plus live code cells. *Recommended.*
- **D2. Permission to push.** *Recommended.* Push (a) is done. The remaining pushes:
  - (a) Step 0: the plan file to v3, and the scripts to `yr-runall-research`;
  - (b) `colab-smoke-test` (never deploys);
  - (c) later, `yr-review-runall`.
- **D3. Write-code questions get no runnable solution cell.** *Recommended.* A solution cell would replace the student's own function during Run all.
- **D4. Multi-part Answers interleaved,** with each part's explanation followed by its live cell and the summary at the end. *Recommended.*
- **D5. Marker for the question's code:** a ```` ```python run ```` block. *Recommended.* The alternative is an invisible cell tag.
- **D6. Wrap only the code that raises** in `run_code(r"""…""")`; everything else stays a plain cell. *Recommended.* The `%%run_question` magic stays an option to try only if E6 is clean.
- **D7. On the website, question code shows as highlighted code blocks.** *Recommended* for simplicity. The alternative, a small extra build step, keeps today's code-cell look; decide from the V7 screenshots.
- **D8. A `## Credits` heading** in the notebooks, removed on the website. *Recommended.*
- **D9. Test chapter 5 from the branch link before publishing it.** *Recommended.* Your to-do order, publish first and then test, also works, but students could see a broken page.
- **D10. If Colab's Shift+Enter or Down arrow opens Answers,** accept it, with the help note's advice. *Recommended.*
- **D11. Accept the cosmetic side effects.** *Recommended.*
  - Colab's and JupyterLab's contents sidebars list an "Answer" per question.
  - "N cells hidden" reveals the number of parts.
  - Answers show open in VS Code, "Colab in VS Code/Cursor", GitHub's preview, nbviewer and classic Notebook 6.
- **D12. No new skill.** Update `yr-review-questions` and `yr-review-page`, and put the guide for people near the top of `yr/README.md`. *Recommended.*
- **D13. Don't commit the one-off conversion script to v3.** It is saved on `yr-runall-research` in Step 0, and `make_smoke.py` also goes on the smoke branch. *Recommended.*

---

### 10. Known uncertainties and fallbacks

**The kernel side is VERIFIED on Colab's exact versions. These are not verified:**

1. **Does Colab's browser stop Run all on a red error output?** (B4) The reply status is "ok", so the kernel doesn't stop it.
   - **Fallback B:** route the traceback to stderr. No error output at all, the same traceback text, status ok:
     ```python
     def run_code(code):                       # variant B (only if B3/B4/B5 call for it)
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
   - **Not verified:** real Colab.
   - **The checks** already parse stderr, skipping the NOTE (mutation M15 and the NOTE mutation).
2. **Are Answers closed on open from GitHub?** (A1/B1) The format matches real Colab-saved files exactly; Tests 2 and 3 show which markers Colab really needs.
   - **Fallback C**, if closed sections don't work or Run all opens them:
     - the run cells sit outside any closed section and call `run_hidden(r"""…""")`;
     - that captures stdout, the traceback text (with the same unwrap), the last drawing and the last value into one closed HTML "Show the output" box, with the exact values in metadata for `check_review`;
     - the explanation stays a `<details>` block.
   - **Status:** VERIFIED locally on both stacks; B8 tests rendering in Colab.
   - **Costs:** no live animation, and tracebacks lose colour.
   - **Not a one-function change.** It also changes check rules 2 and 6, since run cells would sit outside Answers, plus the turtle rules, the prep step and the README. That would be a separate small plan revision.
3. **Error badges** (B5). A red mark on a closed section would hint which Answers are errors → variant B.
4. **Keyboard stepping** (A4/B9). In JupyterLab, Shift+Enter opens closed Answers (VERIFIED). A 2018 Colab issue says the Down arrow did too. Mitigation: D10.
5. **The `python run` marker in Colab** (B2). Verified on the website; BELIEVED in Colab. Fallback: a cell tag.
6. **Editing a page in Colab and saving** (B11).
   - Colab may add outputs and `metadata.id`, and may change the closed layout (it has a separate "Save collapsed section layout" command).
   - `normalize` repairs all of this, and `check_notebooks` (also in CI) fails until it is repaired.
7. **Version drift.**
   - **Versions:**
     - Colab pins IPython 7.34 / ipykernel 6.17.1. Its pinned 2026.07 runtime is Python 3.12.13, while its backend-info now reports Python 3.13.16;
     - IPython 7.34 on Python 3.13 is untested;
     - the local checks run whatever the book venv has.
   - **How the checks cope:** error lines are compared by substring, and V1 runs both stacks.
   - **Traceback headers differ by stack:** `/tmp/ipykernel_…` on Colab, `Cell In[N]` locally (N is one more than the prompt number). Answers never quote headers.
   - **ModuleNotFoundError:** Colab appends a NOTE (ch02 Q14a). This is harmless.
8. **Stop button.** Re-raising KeyboardInterrupt makes Stop halt Run all (VERIFIED on the kernel side; S1 tests Colab). Cost: the interrupt message prints twice.
9. **Running a cell inside a cell.** `run_code` runs IPython's hooks twice per cell. This is untested in Colab; watch B7 for duplicated output.
10. **Other viewers** (VS Code, GitHub preview, nbviewer, classic Notebook 6): Answers show open (BELIEVED). Accepted and documented.
11. **The January 2026 Colab redesign.** Labels like "↳ N cells hidden" and the Settings path may differ. The help note's final wording waits for A1/P7.
12. **Run all on ch04** animates several turtle drawings in hidden cells, so it may take a minute or two. A2 records the time for ch05.
13. **Students' own names.** A student who redefines a name that a question uses (for example `import jupyturtle` before ch04 Q7) changes that Answer's live output. Rule 2.4.11 covers re-runs of the page itself; the help note covers the rest.

**Scratch artifacts used by this plan** (temporary until Step 0 saves the scripts; under `/tmp/claude-0/-home-user-yrThinkPython/6571a165-f8cc-5e43-8b74-c00357a4a6f6/scratchpad/ultra/`):
- `plan-risk/`: smoke notebook generator and logs;
- `plan-maint/`: equivalence script `exp.py`, conversion script `conv3.py`;
- `plan-student/`: run_code and Stop tests;
- `proto/`: prototype converter, adapted tools, mutations;
- `verify-repo/`: `runvis.py`, mutations;
- `verify-jupyter/`: traceback and interrupt tests;
- `critic-feas/`: Colab ImportError-handler simulation;
- `final-rev/`: this revision's tests (Pyright-clean `run_code` on both stacks, the fallback B unwrap).

This revision also registered two test kernelspecs (`rk_yrThinkPython`, `rk_venv-ipy7`) under `/root/.local/share/jupyter/kernels`, outside the repo. The prototype is also on branch `yr-runall-research` under `yr/plans/research/prototype/`.

## How to resume (for a future Claude session)

The research was done by a multi-agent workflow in a cloud session on 2026-10-08. While it ran, a
background script pushed each finished agent's result to the branch **`yr-runall-research`**, in
`yr/plans/research/`: one markdown file per agent (research, verify, plan, judge, synthesize, critic,
revise) plus the prototype's files in `prototype/` (converted chapter 5 notebook, modified
`prep_notebooks.py`, conversion scripts). Start there: `git fetch origin yr-runall-research`. The final
plan (`revise.md`) is copied into this file. Before implementing, ask Prof. Rosenthal for the decisions in section 9.
Originally, if the plan had been missing, the instructions were to redo only the missing parts: map every question on the six pages and every tool that
would change, build a prototype of the chapter 5 conversion in a scratch folder (convert the page,
run it top to bottom with nbclient `allow_errors=False`, build the website from it), then write the
final plan here and ask Prof. Rosenthal for the decisions above before changing the live pages.
