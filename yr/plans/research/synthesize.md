# synthesize

## Final plan: review pages that survive Colab's Run all, with live answers hidden until clicked (and why workers 3-4 stopped)

# Final plan: review pages that survive Colab's "Run all", with live answers hidden until clicked

**How this plan was made.** Three candidate plans were written and scored by three judges. This one starts from the highest-scoring plan, the risk-first staged rollout, and adds the best ideas from the other two:
- from the maintainability plan: one command owns everything that can be derived, a committed self-test of the checks, an explicit marker for the question's code, and a hidden helper cell;
- from the student-experience plan: interleaved multi-part Answers, exact wording edits, and a test link you can open today.

Where the plans disagreed, the choice and the reason are stated.

**Status.** Nothing under `/home/user/yrThinkPython` has been changed and nothing has been pushed. The current local branch is `yr-review-colab` at b389c80; `origin/v3` is three plan-only commits ahead.

**Evidence labels.** **VERIFIED** = tested in this container or seen in primary sources. **BELIEVED** = strong but indirect evidence. **UNKNOWN** = only a live Colab session can tell (section 7).

---

## 0. Why research workers 3 and 4 failed

**Short answer.** Their own work didn't fail. Workers 3 and 4 were stopped by an interrupt in the main session. The workflow was then resumed, both workers re-ran from scratch and finished, and their results are in this plan. Nothing needs fixing.

**Evidence.** I re-checked this for this plan in the session log (`~/.claude/projects/-home-user-yrThinkPython/6571a165-….jsonl`) and in the workflow folder (`…/subagents/workflows/wf_f52e2176-172/`). All times are UTC on 2026-10-08:
- **17:19:56** Claude started a helper agent (claude-code-guide) to answer your question about `/workflows`.
- **17:20:53** your next message ("Is Claude Code running on my laptop faster…") was queued.
- **17:20:58.405** that helper call was rejected ("The user doesn't want to proceed with this tool use") and the session logged `[Request interrupted by user for tool use]`.
- **17:20:58.398** both worker transcripts end with `[Request interrupted by user]`: worker 3 (`research:repo`, agent `af37ec9a…`) and worker 4 (`research:prototype`, agent `a1fdadad…`).
  - Workers 1 and 2 had already finished, at 17:09 and 17:15, so only 3 and 4 were cut off.
  - Neither had hit an error: one was comparing error texts between Python 3.12 and 3.13, the other was reading JupyterLab source.
  - The log can't tell whether Stop was pressed or whether sending a message mid-step interrupts the current step.
- **17:24:00** the same workflow run was resumed. Workers 1 and 2 came back from cache. Workers 3 and 4 re-ran from scratch (agents `a20fcc3e…` and `a24699395…`) and finished at 17:36 and 17:55.

**Not the cause.** The workers guessed at several environment traps: no `rsync`, `git rev-parse` failing in copies, a Playwright browser-version mismatch, and `pkill -f` killing its own shell. All are real, and section 6 avoids them, but none caused this failure.

**To avoid a repeat.** While a workflow is running, don't press Stop or reject a pending step. To ask something else meanwhile, wait for Claude's current step to finish, or use a separate session.

---

## The design in one paragraph

- **Question.** Each question shows its code as **highlighted text**: a markdown block fenced with ```` ```python run ````. Text can't be run, so it can't reveal an answer after Run all. Colab's editor never checks text, so nothing is underlined.
- **Answer.** Under the question, a small **`#### Answer` heading is saved collapsed**, for both Colab and JupyterLab. It holds two things:
  - the explanation with the expected output, as today;
  - a **code cell that runs exactly the question's code**. It shows the real output when the student opens the Answer.
- **Errors.** Code whose result is an error is wrapped in `run_code(r"""…""")`. The error looks like a normal cell's, but it doesn't stop **Run all**.
- **One copy of the code.** The question's code is typed once. One command, `review.sh sync`, generates everything derived from it, and `review.sh check` fails if anything is out of date.
- **Website.** Each Answer is folded back into today's closed "Answer" dropdown.

---

## 1. What students will see

### Colab: opening a page from its "Run this page on Colab" link
- The title, the "Concepts covered" lists (still open) and the "Questions" intro look as they do today.
- **A short "Using this page in Colab or Jupyter" note.** It is hidden on the website. It says:
  - Run all is safe;
  - click the arrow next to **Answer** to open it;
  - run your own code with **Ctrl+Enter**;
  - Answers are not closed in VS Code.
- **Two setup cells.** The page's own setup cell, then a small cell defining `run_code`.
- **Each question shows:**
  - its heading;
  - the prompt ("Predict what this code displays, then open the Answer to check.");
  - the code as a highlighted block. Multi-part questions show **Part a**, **Part b**, … above each block.
- **A closed Answer** under each question: a bold **Answer** heading with a "↳ N cells hidden" row.
  - The file format is VERIFIED from real Colab-saved notebooks.
  - That Colab honours it when a page is opened from GitHub is BELIEVED (Google's own course notebooks rely on it). Test A1/B1.
  - The exact wording after Colab's January 2026 redesign is UNKNOWN.
- **The only code cells outside the Answers:**
  - the setup cells;
  - "Run this cell to define `countdown_by_two`" cells, which display nothing;
  - the `# Your code here` cells of write-code questions.
- **No red underlines** before anything runs.
  - Question code is text. Markdown is not sent to Colab's checker (BELIEVED), and code inside strings is ignored by Pyright (VERIFIED).
  - Every visible code cell is valid code, and `review.sh check` enforces that.
  - This fixes the underlining problem you reported.

### Colab: after Runtime → Run all
- **What runs:** every cell, including the hidden ones inside closed Answers.
  - Running hidden cells is BELIEVED: a published notebook collapses its setup sections and still tells users to use Run all. Test A2/B3.
- **Run all reaches the end.** `run_code` shows an error while the cell still counts as having succeeded.
  - VERIFIED on Colab's exact kernel versions (ipykernel 6.17.1, IPython 7.34.0) with cells queued the way Run all queues them.
  - An unwrapped error aborts the remaining cells. A `run_code` error does not.
  - Whether Colab's **browser side** also stops on a red error output is UNKNOWN (test B4). A tested fallback is ready (section 10).
- **What stays visible:** only the setup cell's one-time "Downloaded jupyturtle.py" / "Downloaded words.txt" line (ch04, ch05, ch07). Every other output is inside a closed Answer.
  - VERIFIED in a Run-all simulation of all six prototype pages and in a real JupyterLab 4.6.4.
  - In Colab this is UNKNOWN until B3–B6.
- **Students' own code:** if a student's `# Your code here` code has an error, Run all stops there, as in any notebook.

### Opening an Answer
- **How:** click the arrow next to **Answer**, or the "N cells hidden" row.
- **What appears:**
  - the explanation with the expected output (a text block or the stored turtle picture);
  - then the code cell with the same code as the question and its real output: printed lines, a red traceback, the live turtle drawing, or a value like `12`.
- **Multi-part questions are interleaved:** "**Part a:** explanation", then Part a's live cell, then "**Part b:** …", and so on.
- **How errors look:** like a normal cell's error. There is no `run_code` frame, the line numbers match the question's code, and syntax errors show the code line and a caret (VERIFIED on IPython 7.34 and 9.17).
- **If Run all wasn't used:** each cell has a ▶ button. Students can also edit the cell to experiment.

### Write-code questions
- **No change on the question side:** header, at least 2 examples, and the `# Your code here` cell.
- **The Answer:** the same closed heading, containing the suggested solution(s) as text blocks, as today. It has no run cell; a run cell would overwrite the student's own function during Run all.

### JupyterLab 4 / Notebook 7 (VERIFIED in JupyterLab 4.6.4)
- The page opens with every Answer closed. "Run All Cells" runs the hidden cells, and their outputs stay hidden.
- **Known side effect (VERIFIED):** pressing **Shift+Enter** onto a closed Answer heading opens it.
  - Questions are text now, so students don't need to step through cells.
  - The help note says to use Run all, or Ctrl+Enter for their own code.
  - Colab's behaviour here is UNKNOWN (test A4/B9).

### The website (Jupyter Book; review pages are not executed there)
- **It looks as it does today:**
  - one closed **Answer** dropdown per question, with the same text and pictures;
  - no "Answer" entries in the right-hand contents list;
  - no new build warnings.
  - VERIFIED with the prototype build.
- **Hidden on the site:** the Colab help note and the `run_code` cell.
- **One visible change:** question code shows as highlighted code blocks, like the examples already on the page, instead of a code-cell box. Decision D7 can keep the old look.

### VS Code, and "Colab in VS Code/Cursor" (launched January 2026)
- These editors ignore both collapse markers (BELIEVED from source), so the Answers show open. The help note says so.

---

## 2. Page layout, per kind of question

### 2.1 Page skeleton, in order
1. **Title cell.** Same text, with one sentence that works everywhere: "Each question has a suggested answer under **Answer**. Try the question first, then open the Answer."
2. **`## Concepts covered`**: unchanged.
3. **`## Questions` intro**: no mention of `run_code` any more.
4. **The help note.** A *managed* markdown cell tagged `remove-cell`. The website drops it. `sync` writes its text, so it is identical on all six pages.
5. **The page's own setup cell**, tagged `setup`: imports, downloads.
   - The old `run_code` definition is removed from it.
   - ch03's setup cell held only `run_code`, so it becomes empty and is deleted.
6. **The managed `run_code` cell**, tagged `["setup", "remove-cell"]`. `sync` writes its text, it is hidden on the website, and it now exists on every page, ch06 included.
7. **The questions.**
8. **`## Credits`** heading added to the existing credit cell.
   - Without it, the last Answer would swallow the credits, because a closed heading hides everything up to the next heading.
   - The website build removes the heading line, so the site's contents list is unchanged.

### 2.2 The building blocks (exact format, for Claude)

**Run block.** The question's code, written once. It is a markdown cell before the Answer, holding one fenced block. It may start with a part label.

~~~
**Part a**

```python run
x = 5
if x = 5:
    print('five')
```
~~~

The word `run` is the marker that says "the Answer runs this". Other ```` ```python ```` blocks are never run by the Answer: examples, headers, refactor questions' given code, solutions. Markdown renderers use only the first word after the fence, so the site shows plain Python highlighting (VERIFIED in a Jupyter Book build). Colab is BELIEVED to do the same (test B2).

**Answer heading.** Collapsed for Colab and JupyterLab. `metadata.id` must equal `id`, which is what Colab itself writes for nbformat 4.5 files.
```json
{"cell_type": "markdown", "id": "9c41e7b2",
 "metadata": {"id": "9c41e7b2", "jp-MarkdownHeadingCollapsed": true},
 "source": ["#### Answer"]}
```

**Run cell.** A code cell inside the Answer, generated by `sync`.
- Plain code if the code runs without error; otherwise wrapped in `run_code`.
- No tags and no comment lines: an added line shifts traceback and doctest line numbers (VERIFIED, ch07 Q14).
```json
{"cell_type": "code", "id": "3f0a77c1", "execution_count": null, "metadata": {}, "outputs": [],
 "source": ["run_code(r\"\"\"\n", "x = 5\n", "if x = 5:\n", "    print('five')\n", "\"\"\")"]}
```

**Managed `run_code` cell.** `review_format.RUN_CODE_CELL`, byte-identical on every page:
```python
def run_code(code):
    """Run code (a string) as if it were a cell of its own.

    Some Answers use it for code whose result is an error: the error is shown as
    usual, but it does not stop Runtime > Run all.
    """
    try:
        ip = get_ipython()
    except NameError:                 # plain Python (the review tools): just run it
        exec(code, globals())
        return
    result = ip.run_cell(code, store_history=False)
    if isinstance(result.error_in_exec, KeyboardInterrupt):
        raise KeyboardInterrupt       # the Stop button still stops Run all
```

**Notebook metadata.** `collapsed_sections` lists exactly the Answer heading ids, in page order. Both are written by `sync`.
```json
"metadata": {"colab": {"collapsed_sections": ["9c41e7b2", "…one per Answer…"]},
             "kernelspec": {"display_name": "Python 3 (ipykernel)", "language": "python", "name": "python3"},
             "language_info": {"name": "python"}}
```

### 2.3 Tiny examples

Cells are listed top to bottom; `[md]` is markdown, `[code]` is code.

**What is displayed** (most of the 69 predict questions):
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
~~~

The rule that places run cells: in a question with 2 or more run blocks, every run block starts with `**Part a**`, `**Part b**`, …. The Answer has one markdown cell starting with `**Part a:**` and so on for each part, and run cell *x* goes right after that cell. Any summary text after the last part stays after the last run cell.

Parts that run without error (ch02 Q9 a and e, ch04 Q14 c) are plain cells, so nothing outside hints which parts fail. That hint would only be visible once the Answer is open anyway.

**Last value shown** (ch02 Q4 `price * 3`, ch03 Q9 `greet`):
- Same layout as "what is displayed". The plain run cell shows `12`, and the check now verifies it.
- ch02 Q4's Answer gets a missing ```` ```text 12 ``` ```` block.
- The prompt becomes "What does this code display when it is run as a notebook cell?".

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
[code] run_code(r"""
       countdown_by_two(5)
       """)
~~~

**What is drawn** (ch04 Q2, Q6, Q7; ch05 Q17):
- **Question:** a run block starting with `make_turtle()`.
- **Answer:** the explanation with `<img data-turtle src="data:…">`. `review.sh sync` draws that picture from the question's run block; the website shows it.
- **Run cell:** draws live, and the drawing is visible only when the Answer is open.

**Doctest** (ch07 Q14):
- **Question:** one run block holding the whole program.
- **Answer:** the run cell is plain (the code doesn't raise), byte-identical to the block, so the report's `line 9` stays right.
- **Rule:** `run_code` strings may never contain `>>>` lines. IPython 8 and later strips them even inside strings (VERIFIED on 9.17).

**Write code** (34 questions):
~~~
[md]   ### Question 4 (easy): write a function
       Write sign(n) ... header block ```python def sign(n): ... ```, 2+ examples (```python + ```text or a picture)
[code] # Your code here
[md]   #### Answer
[md]   ```python  def sign(n): ...  ``` + explanation          <- no run cell
~~~

**Refactor / generalize / simplify** (ch03 Q12; ch04 Q11, Q17, Q18, Q19; ch06 Q12):
- The given code is a plain ```` ```python ```` block, without `run`, so nothing is run and no guessing is needed. The prototype's guessing rule misfired on exactly these six questions (VERIFIED).

**Reading a file** (ch07 Q9, Q15): same as "what is displayed". words.txt comes from the setup cell.

### 2.4 Format rules (go in the README; enforced by `review.sh check` and `check_notebooks.py`)
1. **Extent of a question.** It runs from `### Question N (level): kind` to the next heading of level 1–3.
2. **One Answer heading.** Exactly one cell whose whole source is `#### Answer`.
3. **No other headings inside a question.** That means no `#`–`######`, no setext `===`/`---` underlines, and no HTML `<h1>`–`<h6>`, checked outside code fences.
   - A heading inside an Answer would end the closed section early and show the rest after Run all (VERIFIED, mutation M3).
4. **Run blocks.** They appear only before the Answer heading, one per markdown cell, and must hold valid fenced code.
5. **Code cells before the Answer heading:** only setup cells, definition cells (must parse, display nothing, raise nothing), and `# Your code here`.
6. **Code cells inside an Answer:** only generated run cells.
7. **Answer pictures.** A picture with no ```` ```python ```` block above it in its cell shows what the question's run block draws. That is allowed only when the question has exactly one run block.
8. **End of page.** The page ends with `## Credits`.
9. **Tags.** Only `setup`, `no-signature` and `remove-cell` (managed cells only). `raises-exception` is no longer used: Colab ignores it.
10. **Never edit run cells or managed cells by hand.** Edit the run block and run `review.sh sync`.

---

## 3. Don't Repeat Yourself: how the code stays in one place

- **Single source.** The question's code is written **once**, as a ```` ```python run ```` block. This is option A from the research, with an explicit marker.
  - **Chosen over an invisible cell tag:** the fence is part of the text, so it survives any editor, including a Colab save that might drop tags. It is also visible to authors.
  - **Fallback:** if test B2 shows Colab renders it badly, switching to a tag is one constant in `review_format.py`.
- **One command derives everything else: `yr/tools/review.sh sync NB`.**
  1. **normalize** (static, stdlib-only, in `review_format.py`) regenerates:
     - the run cells from the run blocks, in order, placed by the Part rule, keeping existing run-cell ids and their wrapped/plain state;
     - the two managed cells;
     - the Answer heading metadata and `colab.collapsed_sections`;
     - it strips outputs and execution counts;
     - it drops metadata Colab adds when it saves: `executionInfo`, `outputId`, `colab` on cells, and `metadata.id` except on Answer headings.
  2. **Run the page once** (nbclient). Wrap each run cell that produced an error in `run_code(…)`, and unwrap any wrapped cell that didn't.
  3. **Quoting.**
     - Use `r"""…"""`, or `r'''…'''` when the code contains `"""` (docstrings).
     - Check that `ast.literal_eval` of the literal gives back exactly the code.
     - **Refuse with a clear message** if the code contains both quote styles, ends with a backslash, or contains `>>>` lines.
  4. **Redraw the turtle pictures** (`turtle_images.py`), deterministically.
  5. **Second run.** Running `sync` again changes nothing.
- **`review.sh check NB` fails if `sync` would change anything.**
  - **Static part:** "normalize is a no-op". Run cells are compared with the run blocks after unwrapping with `ast`, not regexes. It also runs in `check_notebooks.py` and CI, without executing anything.
  - **Runtime part:** "wrapped exactly when it raises".
  - **Pictures:** `turtle_images --check` reports any picture that differs from a fresh drawing.
- **Rejected options:**
  - **B**, code in a string variable `q8a = """…"""`: the question reads as one-colour text, the site would show `q8a = """`, and the Answer depends on the question cell having run first.
  - **C**, reading the notebook file at run time: doesn't work in Colab.
  - **A custom `%%run_question` magic for the Answer cells**: verified to work in IPython, and it would avoid quoting rules. But it adds Colab unknowns: Colab has an "unsupported magics" check, it linted `%%writefile` bodies in 2022, and unknown magics may show uncoloured.
    - Smoke test E6 records how Colab treats a custom magic. If it is clean, the professor may switch later; `render_run_cell` is the only function that would change.
  - **`# type: ignore` at the top of question cells**: not needed (question code is text), and probably ineffective in Colab, which most likely joins cells into one document.

---

## 4. Tool, README and skill changes

### 4.1 New `yr/tools/review_format.py` (stdlib only)
The format is defined in one place. It is imported by `review_cells.py`, `sync_review.py`, `check_review.py`, `turtle_images.py`, `check_notebooks.py`, and by `jb/prep_notebooks.py` via `sys.path`.
- **Constants:** `ANSWER_HEADING`, `RUN_FENCE` (```` ```python run ````), `PLACEHOLDER`, `CREDITS_HEADING`, `HELP_CELL`, `RUN_CODE_CELL`, and a tightened `EXAMPLE` regex that never stretches across blocks and never counts run blocks.
- **Helpers:** `source(cell)`; fence-aware `headings(md)`; `run_blocks(md)`; `render_run_cell(code, wrapped)`; `unwrap(src)` (ast-based); `parse_page(cells)` returning setup cells, managed cells, questions (with question cells, run blocks, definition cells, placeholders, Answer heading, Answer markdown, run cells) and the credits cell.
- **`normalize(nb)`:** returns a list of changes, including a diff for any run cell it rewrites, so a hand edit is never lost silently.
- **`lint(nb)`:** static rules 2.4 plus "normalize would change …".
- **`page_format(nb)`:** returns `new`, `old` or `mixed` (`mixed` is an error). Used during the rollout (section 8).

### 4.2 `yr/tools/review_cells.py` (stays stdlib)
- **Spec kinds:**
  - `%%% markdown`;
  - **`%%% run`** (new): the body is plain code and becomes a run-block cell;
  - `%%% code [tags]` (definition cells only);
  - `%%% placeholder`;
  - **`%%% answer`**: the `#### Answer` heading plus a markdown body. Further `%%% markdown` cells continue the Answer, e.g. one per `**Part x:**`. Headings in the body are rejected.
- **`add` / `renumber`** call `normalize` automatically and then print "run `review.sh sync NB`, then `review.sh check NB`".
- **New `normalize NB…`:** the static repair, for example after a page was edited and saved in Colab.
- **`new` skeleton:** title sentence, help cell, setup cell, `run_code` cell, `## Credits`, and `"colab": {"collapsed_sections": []}`.
- **The docstring** gets a full spec example, including a multi-part error question.

### 4.3 New `yr/tools/sync_review.py`, run as `review.sh sync NB…`
Implements section 3. It needs the venv (nbclient), like `check`.

### 4.4 `yr/tools/check_review.py` (new-format path)
**How it runs.** One execution with `allow_errors=True`. nbclient's `on_cell_executed` hook (present in nbclient 0.11.0, VERIFIED) records every cell's reply status. That gives full outputs *and* an exact model of where Run all would stop, ignoring tags as Colab does.

**What counts as an error line.** Error lines come from `error` outputs **and** from the last `Ename: message` line of an ANSI-stripped stderr traceback in a run cell. So switching to the stderr fallback can't silently disable the checks (mutation M15).

**Rules** (none of today's checks is weakened; three gaps are closed):
1. **Run all reaches the end:** no cell has reply status "error".
2. **Nothing visible after Run all:** every code cell with output, except the stdout of `setup` cells, sits inside a collapsed Answer. This uses the real section rule.
3. **Visible cells are harmless:**
   - definition cells parse, display nothing and raise nothing;
   - placeholders are exactly `# Your code here`;
   - no visible code cell has a syntax error. This is what stops editor underlines.
4. **Wrapped exactly when it raises** (restores today's "tagged but raised nothing" guard).
5. **Live output matches the Answer text:**
   - a run cell's stdout plus any `execute_result` text, in output order, equals one ```` ```text ```` block exactly. **New:** closes the unchecked `12` in ch02 Q4 and ch03 Q9.
   - every error line appears in a text block (existing; substring, so wording differences between Python 3.12 and 3.13 are tolerated);
   - **new, reverse rule:** every line in the Answer's text blocks that looks like an exception (`^[A-Z]\w*(Error|Exception|Interrupt|Exit)\b`) matches an error that one of that question's run cells produced, by substring in either direction. This closes mutation M1;
   - **new:** a run cell that draws must have a data-turtle picture in its Answer;
   - **new:** stderr that isn't a traceback and isn't in the Answer is reported.
6. **Standalone Answer blocks:** each ```` ```python ```` block in an Answer runs as a standalone `.py` file (existing).
7. **Write-code questions:** a header plus at least 2 examples (existing). Examples are counted in prose only, never in run blocks. These questions have no run blocks and no run cells.
8. **Wrong-call questions** (a run cell raises and the question defines a function): at least 2 correct calls (existing).
9. **Pictures:** up to date (`turtle_images --check`) and not empty (existing plus new).
10. **No hazard symbols:** no `(c)`, `(r)`, `(tm)`, `+-` (existing).
11. **Static rules** from `review_format.lint`.

**Option:** `REVIEW_PYTHON=/path/to/venv` runs the kernel from a Colab-like venv: Python 3.12, `ipython==7.34.0`, `ipykernel==6.17.1`, `jupyter_client==7.4.9`. Used at each page conversion; the README shows how to create that venv.

### 4.5 `yr/tools/turtle_images.py`
- **Uses `parse_page`.** Per question it runs the setup code, then the Answer's ```` ```python ```` blocks, then the definition cells and run blocks in page order. It **never runs run cells or managed cells**.
- **Picture rule:** use the nearest ```` ```python ```` block above the picture in the same cell. Otherwise use the question's single run block (rule 7). With 0 or 2+ run blocks it reports an error instead of guessing.
- **New `--check`:** draws everything, writes nothing, and exits 1 if any stored picture differs.
- **Hardening:** if an *example* picture's code raises, it exits 1 without writing anything. Today's tool silently rewrote 19 ch04 pictures with partial drawings when run on the new layout (VERIFIED).

### 4.6 `jb/prep_notebooks.py` (`process_review`)
1. Drop `# Your code here` cells (as now).
2. `raw_pictures` and `details_to_dropdown` (as now; the concept lists and old-format pages still use them).
3. **New `answer_sections`:** merge each `#### Answer` heading and its markdown into one `:::{admonition} Answer` / `:class: dropdown` cell, keeping the heading's id, and drop the run cells. Each markdown cell is parsed separately, so a dropdown can't span cells (VERIFIED).
4. **New:** remove the `## Credits` line from the credit cell.
5. `process_cell` (as now). Never tag run cells `solution`: prep would blank them.
6. **New guard:** stop the build with a clear message if any of these happens:
   - a `#### Answer` heading survives;
   - a code cell sits inside an Answer dropdown's question;
   - the number of dropdowns differs from the number of questions.

   A tools-vs-pages mismatch then fails the deploy instead of publishing answers in the open (VERIFIED risk: the old prep plus new pages shows every answer, with zero warnings).

The managed cells are removed by myst-nb's standard `remove-cell` tag; check this in the build (V7).

### 4.7 Other files
- **`.claude/skills/check-notebooks/check_notebooks.py`:** for `yr/*.ipynb`, call `review_format.lint(nb)` (static and fast). `KNOWN_MAGICS` is unchanged.
- **`.claude/skills/check-notebooks/run_notebooks.sh`:** skip `yr/` pages and point to `review.sh check`. Its tag logic would report the caught errors as failures.
- **`yr/tools/review.sh`:**
  - new `sync` and `selftest` cases;
  - `images` stays as an alias for the picture step;
  - **ROOT fallback** for copies without `.git`: `ROOT="$(git -C "$(dirname "$0")" rev-parse --show-toplevel 2>/dev/null || (cd "$(dirname "$0")/../.." && pwd))"`. The same fallback goes in `build_book.sh` and `run_notebooks.sh`.
- **`.github/workflows/deploy-book.yml`:** add `python3 .claude/skills/check-notebooks/check_notebooks.py` before the build. It is static and fast, and blocks publishing malformed pages. It passes on today's notebooks (48 checked, VERIFIED).
- **New `yr/tools/selftest_review.py`, run as `review.sh selftest`:**
  - **The fixture:** `yr/tools/selftest/fixture_review.ipynb`, about 9 questions covering every kind. It is outside `yr/*.ipynb`, so it never reaches the site or the table-of-contents check.
  - **The test:** each mutation is applied to a copy and must make `check` fail with the expected message; the unmutated fixture must pass.
  - **Mutations:**
    - M1: a part edited so it no longer raises, while the Answer still claims an error;
    - M2: `price*3` changed to `price*4` in both the run block and the run cell, with the Answer unchanged;
    - M3: `#### Note` inside an Answer;
    - a setext heading in an Answer;
    - an HTML `<h4>` in an Answer;
    - M15: the stderr `run_code` combined with wrong error text;
    - a run block edited without running sync;
    - run cells swapped;
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
    - a wrong-call question with only one correct call;
    - a write-code question with one example;
    - a picture not redrawn;
    - a managed cell edited;
    - a leftover `<details>` Answer.

  The README tells future sessions to run it whenever `check_review.py` or `review_format.py` changes. This makes "never weaken checks" testable.

### 4.8 README, guide for people, skills (goals 7 and 8 in your plan file)
- **`yr/README.md`:**
  - **New section near the top, "Adding a question: a guide for people" (goal 8).** One short recipe per kind: what is displayed, what is drawn, an error answer, several parts, wrong calls, write code, refactor, doctest. Each recipe gives:
    - the exact text to type (the ```` ```python run ```` block, the `#### Answer` cell, the `**Part a:**` cells);
    - the three commands: `review.sh sync`, `review.sh check`, `check_notebooks.py`;
    - "or ask Claude: *add a question to chapter N's review page* (it uses the yr-review-questions skill)".

    It also covers "If you edit a page in Colab or Jupyter": download it and run `review_cells.py normalize` or `review.sh sync`.
  - **Rewrite:**
    - "Layout of a page", "Answers" and "Cell conventions": replace the `<details>`, `raises-exception` and "Errors an editor can see" sections with rules 2.4, the building blocks, and why (Run all, nothing visible, no underlines);
    - "Turtle pictures";
    - "Tools" (`sync`, `normalize`, `selftest`, `--check`, `REVIEW_PYTHON`);
    - the `review.sh check` list;
    - "How the build handles yr/" (`answer_sections`, the guard).
- **`.claude/skills/yr-review-questions/SKILL.md` (goal 7):**
  - **Rules:** question code goes in `%%% run` blocks; one way per kind (table); never write run cells or `run_code` by hand; no headings in Answers; no `raises-exception`.
  - **Spec examples** for an error question and a multi-part question.
  - **Workflow:** add → `review.sh sync` → `review.sh check` → `check_notebooks.py` → `build_book.sh`.
- **`.claude/skills/yr-review-page/SKILL.md`:** the new skeleton and verification steps.
- **`.claude/skills/notebook-conventions/SKILL.md`, line ~86:** point to the README's Answer sections.
- **No new skill.** The two yr-review skills cover it (decision D12).
- **At the end of the rollout:**
  - replace the "Draft plan" in `yr/plans/runall-collapsible-answers.md` with this plan and tick its to-do list;
  - delete the "Pending work" section of `CLAUDE.md`.

---

## 5. Converting the six pages

**The script.** A one-off script, based on the prototype's `convert.py` and the maintainability plan's `conv3.py`. It stays in the scratchpad (decision D13). For each page:
1. **Question code cells.** Every question code cell that isn't `# Your code here` and isn't definition-only becomes a run-block markdown cell **with the same id**.
   - "Definition-only" means: by `ast`, only def/class/import/assignment, no output in an executed copy, not tagged `raises-exception`.
   - The `run_code("""…""")` wrapper is removed with `ast` (the result is checked).
   - A trailing `**Part x**` line in the cell above, or a `**Part x**` cell, is folded into the run-block cell.
2. **The old `<details>` Answer** becomes a new `#### Answer` heading plus explanation cell(s); the first keeps the old id.
   - For multi-part questions, the body is split before each `**Part x:**` paragraph.
   - All 7 multi-part questions are printed for a manual look: ch02 Q9, Q10, Q14; ch03 Q10; ch04 Q14, Q15; ch05 Q8.
3. **Page-level changes:**
   - remove the old `run_code` definitions (ch02–ch05, ch07), deleting a setup cell that becomes empty (ch03);
   - remove all `raises-exception` tags;
   - add `## Credits`.
4. **`review.sh sync`** adds the run cells, wrapping, managed cells, metadata and pictures.
   - **Expected wrapping changes:** the 19 existing `run_code` cells stay wrapped, except ch02 Q9 parts a and e, which become plain. The 5 plain raising cells become wrapped: ch03 Q14, ch04 Q14 a and b, ch05 Q14, ch06 Q15.
   - **Pictures:** all 23 stored PNGs (22 in ch04, 1 in ch05) must come out byte-identical.

**Wording edits.** Each must match exactly once; any that don't are printed. Afterwards, grep the question text for `\bcells?\b`, `run (it|this)` and `run_code` and review each hit. "Run this cell to define …" stays: it is still true.

| Page / question | Old | New |
|---|---|---|
| all pages | "then run it to check" / "then run the cell(s) to check" | "then open the Answer to check" |
| ch02 Q4 | "What does this cell display when you run it in a notebook?" | "What does this code display when it is run as a notebook cell?" (+ add ```` ```text 12 ``` ```` to the Answer) |
| ch02 Q9 | "For each cell, predict …" | "For each part, predict …" |
| ch02 Q14 | "Each cell has an error …" / "what each cell displays before the error" | "Each part has …" / "what each part displays …" |
| ch03 Q9 | "What does this cell display in a notebook?" | "What does this code display when it is run as a notebook cell?" |
| ch03 Q10, ch04 Q14 | "For each of the next three cells" | "For each of the three parts" |
| ch04 Q7 | "… run only the setup cell … and this cell" | "… run only the setup cells (at the start of the Questions), and then this code" |
| ch05 Q8 | "Each cell has one mistake." | "Each part has one mistake." |
| ch07 Q15 | "(… then run it …)" | "(… then open the Answer, which runs it …)" |

Optionally, ch02 Q14a's Answer can mention that Colab adds a NOTE to ModuleNotFoundError.

**Order.** ch05 first, as the pilot: it has syntax errors, a RecursionError, a turtle tree and write-code questions. Then ch02, ch03, ch06, ch07, and ch04 last. ch04 has 22 pictures, the "assume restarted" premise in Q7, Q14's canvases, Q15's version-dependent message and Q18's `jump`.

**Cell ids.** Every cell that stays in place keeps its id. Only Answer headings, run cells and managed cells are new.

---

## 6. Verification here, before anything reaches you

- **V1. Checks on both stacks.** `review.sh check` passes on every converted page on Python 3.13 / IPython 9.17, and with `REVIEW_PYTHON` on the Colab-like stack (Python 3.12 / IPython 7.34 / ipykernel 6.17.1).
- **V2. Nothing changed.** For all 103 questions, compare stdout, error lines, displayed values and turtle displays between the old and new page, on both stacks (`plan-maint/exp.py`). Expect 0 differences except intended ones. The maintainability plan got 0 differences for its variant of this layout.
- **V3. Run-all simulation.** nbclient with `allow_errors=False` and `force_raise_errors=True`, which ignores tags as Colab does, on both stacks. It must reach the end with no visible output except the setup lines. Visibility uses the real section rule (`verify-repo/runvis.py`).
- **V4. Idempotent.** A second `sync` changes nothing; `turtle_images --check` reports 0 differences; ids are preserved.
- **V5. Self-test.** `review.sh selftest` catches every mutation.
- **V6. Lint.** `check_notebooks.py` passes, including the new static lint.
- **V7. Website.** `build_book.sh` gives no warnings beyond `known_warnings.txt`. A script over the built `yr/chap0*_review.html` asserts:
  - dropdowns equal the number of questions (17/16/19/17/17/17), none open;
  - 0 `h4` headings and 0 "Answer" or "Credits" entries in the contents list;
  - no help text and no `def run_code`;
  - dropdown text identical to today's site, except ch02 Q4.

  Pages still in the old format must build byte-identical HTML. Screenshots: ch04 Q2 and Q14, ch05 Q8 and Q17, ch07 Q14, with the D7 alternative shown side by side.
- **V8 (pilot only).** Headless JupyterLab 4.6.4: the page opens collapsed, and Run All keeps outputs hidden.
- **V9. Pyright.** Run it on every visible code cell together with the cells above it. Expect nothing beyond the known jupyturtle import note.
- **V10. Diff.** `git diff` touches only the intended files, no outputs are stored, and ids are preserved.

**Environment traps to avoid:**
- there is no `rsync`: use `cp -a` or `tar`;
- work on a real branch, or `git init` a copy;
- Playwright needs `executable_path=/opt/pw-browsers/chromium-1194/chrome-linux/chrome`;
- start JupyterLab with `--allow-root --LabApp.expose_app_in_browser=True`;
- never run `pkill -f PATTERN` when the pattern appears in the same command line;
- don't press Stop during workflows (section 0).

---

## 7. Colab test checklist for you

Use Chrome, signed in, with default settings. Take a screenshot wherever it says [shot]. Between notebooks, use Runtime → Disconnect and delete runtime. Each answer below decides something (see the table at the end).

### Part A: today, nothing needs pushing (about 10 minutes)
Open the prototype chapter 5 page, already on the research branch:
`https://colab.research.google.com/github/y-rosenthal/yrThinkPython/blob/yr-runall-research/yr/plans/research/prototype/out/all/chap05_review.ipynb`

It differs from the final design in three small ways: its run cells sit at the end of each Answer, its `run_code` lacks the Stop fix, and its code blocks lack the word `run`.

1. **A1. Closed on open.** Before running anything: is every Answer closed, with an "N cells hidden" row? Write down the exact wording. [shot]
2. **A2. Run all.** Choose Runtime → Run all and wait until nothing is running.
   - Did it stop anywhere, or show an error popup?
   - Did any Answer open by itself, or did the page jump into one?
   - Is anything visible outside the Answers besides "Downloaded jupyturtle.py"?
   - How long did it take? [shot]
3. **A3. Live answers.** Open Q8: three errors (SyntaxError, SyntaxError, IndentationError), each shown once? Open Q14 (RecursionError, expected to be short) and Q17 (a stored picture plus a live drawing). [shot]
4. **A4. Keyboard.** Reload the page.
   - Click Question 1's text and press **Shift+Enter** repeatedly through Question 3: does an Answer open?
   - Repeat with the **Down arrow**, then with **Ctrl+Enter** followed by Down.

### Part B: smoke-test notebooks (about 20 minutes; needs your OK to push branch `colab-smoke-test`, which never deploys)
These are already built and simulated here (`scratchpad/ultra/plan-risk/make_smoke.py`). Before pushing, they will be updated to use ```` ```python run ```` and the final `run_code`, and the generator is committed with them, because the scratchpad is temporary.

**Notebook 1** (`colab_tests/colab_test_runall.ipynb`):
5. **B1.** Before running: which of Tests 1–10 are closed?
   - Test 1 has the full markers.
   - Test 2 has only Colab's list with the top-level id.
   - Test 3 has only the JupyterLab key.
   - Is any "SECRET n" text visible without clicking?
6. **B2.** Do the question code blocks look like normal highlighted Python, without the word "run"?
7. **B3.** Run all. Which "MARKER n" lines appear, and is "END" printed?
8. **B4.** Did Run all get past Tests 6–8 (red error outputs, variant A) as well as Tests 4–5 (stderr, variant B)?
9. **B5.** Without clicking anything: is there any red icon or mark on an Answer heading, its "cells hidden" row, or the contents sidebar? Compare the rows of the A tests with the B tests. [shot]
10. **B6.** Is any "LIVE n", traceback or drawing visible outside an Answer?
11. **B7.** Open Tests 6, 7, 8, then 4, 5, then 9, 10. Expected:
    - 7 lists `outer` before `inner`;
    - 8 may show a Colab NOTE;
    - 4 and 5 show the same text in stderr style;
    - 9 shows `12`;
    - 10 shows a square. [shot]
12. **B8.** Test 11 (fallback C): do both "Show the output" boxes open and show their contents?
13. **B9.** Reload. Step through Test 9 with Shift+Enter, then with the Down arrow, then with Ctrl+Enter. Which ones open the Answer?
14. **B10.** Copy the setup cell's version line (for example `Python 3.12.x | IPython 7.34.0 | ipykernel 6.17.1`).
15. **B11.** File → Save a copy in Drive. Open one Answer in the copy, save, then File → Download .ipynb and send the file. This shows what Colab writes when it saves.

**Notebook 2** (`colab_test_editor.ipynb`; don't run it, just press Connect):
16. **E1–E7.** Click into each cell and wait 5 seconds. Is it underlined? Is it coloured?
    - E6 is a custom `%%magic`: is there an "unsupported magic" warning?
    - Repeat with Tools → Settings → Editor → Code diagnostics set to "Syntax and type checking". Write down every option in that list and which one is the default, then restore the default.

**Notebook 3** (`colab_test_stop.ipynb`):
17. **S1.** Run all, then press Stop (Runtime → Interrupt) after about 10 seconds. Pass = "END" never appears. A doubled KeyboardInterrupt message is expected.

### Part C: the real chapter 5 pilot (about 15 minutes, from branch `yr-review-runall`)
`https://colab.research.google.com/github/y-rosenthal/yrThinkPython/blob/yr-review-runall/yr/chap05_review.ipynb`

18. **P1.** On opening: all 17 Answers closed; question code shown as text; the help note visible; no underlines anywhere.
19. **P2.** Run all reaches the end. Afterwards nothing is visible except "Downloaded jupyturtle.py".
20. **P3.** Q8 shows three live errors interleaved with their "Part a/b/c" explanations.
21. **P4.** Q14 shows the RecursionError. Q17 shows the stored and the live tree.
22. **P5.** Q9 (write code): your own code in `# Your code here` runs with Ctrl+Enter; the Answer shows the solution text.
23. **P6.** Close an Answer again: it hides again.
24. **P7.** Does the help note's wording match what you saw (arrow, "cells hidden")? Suggest changes.

### What the results decide
| Result | Action |
|---|---|
| A1/B1 Test 1 closed; A2/B3 END reached; B5/B6 clean | Main design, variant A (normal red tracebacks) |
| B3 stops at Test 6 (variant A blocks Run all) | Switch `run_code` to variant B (stderr). One function changes; the checks already read stderr |
| B5 shows red marks only on the A rows | Switch to variant B, so nothing hints which Answers are errors |
| B1: Test 2 also closed | No change; keep writing `metadata.id` (harmless) |
| A1/B1: Test 1 **not** closed, or A2/B3 open Answers by themselves | Fallback C (section 10) |
| A4/B9: Shift+Enter or Down opens Answers | Keep the design; help note: "use Run all; run your own code with Ctrl+Enter" (decision D10) |
| B2: the word "run" shows or there is no colour | Switch the marker to a cell tag (one constant) |
| E6 clean and you dislike the `run_code(r"""…""")` look inside Answers | Optional later switch to the `%%run_question` magic (one function) |
| S1: END printed | Investigate; minor, documented |
| B10 shows IPython 8 or later | Nothing changes (nested `run_cell` also looks normal on 9.17); re-run the Colab-like check with that version |

---

## 8. Rollout: one page first

Your plan file's to-do list says "convert chapter 5 first and publish it". That means the tools must handle both formats for a while.

**How the transition works:**
- each tool checks the page format (`review_format.page_format`);
- old-format pages go through today's code, kept unchanged in a `legacy` module;
- a page mixing both formats is an error;
- `prep_notebooks.py` handles both naturally (`answer_sections` does nothing on old pages);
- the legacy code is deleted once all six pages are converted.

**Steps:**
1. **Step 1, today.** You run Part A. You decide D1–D13 (defaults = recommendations).
2. **Step 2.** With your OK, push `colab-smoke-test`; you run Part B. If the results call for variant B or fallback C, the plan is adjusted before any page is touched.
3. **Step 3.** Branch `yr-review-runall` from `origin/v3`.
   - Build `review_format.py`, `sync_review.py`, the new `check_review.py` and `turtle_images.py` with their legacy paths, `prep_notebooks.py` with its guard, `review_cells.py`, `check_notebooks.py`, `run_notebooks.sh`, `review.sh`, the self-test and fixture, the README (with the guide for people) and the skills.
   - Gate: old pages pass the old checks unchanged, their HTML is identical, the self-test is green, and `check_notebooks` passes.
4. **Step 4.** Convert **chapter 5 only** and run V1–V10. Push the branch, and you run Part C from the branch link. This is the same experience as the live page, but students never see a broken page (decision D9).
5. **Step 5.** Publish chapter 5 with the yrpublish skill: tools and ch05 go to v3 in one merge. Then a 2-minute check: open the live "Run this page on Colab" link, Run all, open one Answer.
6. **Step 6.** Convert ch02, ch03, ch06, ch07, then ch04, one commit each. Each must pass V1–V7 plus a Colab spot-check from you (one error question and one turtle question). Publish them together or one by one.
7. **Step 7. Cleanup:**
   - remove the legacy paths; `check` then rejects `<details>` Answers;
   - add the CI lint step;
   - confirm on the live pages that your three reported problems are gone: underlines, Run all stopping, answers visible;
   - update the plan file and remove the `CLAUDE.md` note;
   - with your OK, delete the `colab-smoke-test` and `yr-runall-research` branches.

**Rollback.** `git revert` of a page commit on v3 brings back the old page. The tools still read both formats until Step 7, the site redeploys on push, and Colab links follow v3 immediately. A bad tools commit is reverted the same way.

---

## 9. Decisions needed from you (recommendation first)

- **D1. The overall design.** Question code as text; a closed Answer heading with the explanation plus live code cells. *Recommended.*
- **D2. Permission to push** `colab-smoke-test` (never deploys) and later `yr-review-runall`. *Recommended.* Nothing has been pushed.
- **D3. Write-code questions get no runnable solution cell.** *Recommended.* A solution cell would replace the student's own function during Run all. Their Answers use the same closed heading, with text only.
- **D4. Multi-part Answers interleaved** (Part a explanation, its live cell, Part b …). *Recommended* over putting all live cells at the end.
- **D5. Marker for the question's code:** a ```` ```python run ```` block. *Recommended* (visible, survives any editor). The alternative is an invisible cell tag.
- **D6. Wrap only the code that raises** in `run_code(r"""…""")`; everything else stays a plain cell with syntax colours. *Recommended.* The `%%run_question` magic is kept as an option to try only if test E6 is clean.
- **D7. On the website, question code shows as highlighted code blocks** (like the examples). *Recommended* for simplicity. The alternative, a small extra build step, keeps today's code-cell look; decide from the V7 screenshots.
- **D8. A `## Credits` heading** in the notebooks, removed on the website. *Recommended.*
- **D9. Test chapter 5 from the branch link before publishing it.** *Recommended.* Your to-do list's order, publish first and then test, also works, but students could see a broken page.
- **D10. If Colab's Shift+Enter or Down arrow opens Answers,** accept it, and the help note says "use Run all; run your own code with Ctrl+Enter". *Recommended.* Questions no longer need stepping through.
- **D11. Accept the cosmetic side effects:**
  - Colab's and JupyterLab's contents sidebars list an "Answer" per question;
  - "N cells hidden" reveals the number of parts (which the question shows anyway);
  - VS Code shows Answers open.

  *Recommended.*
- **D12. No new skill.** Update `yr-review-questions` and `yr-review-page`, and put the guide for people near the top of `yr/README.md`. *Recommended.* The alternative is a separate `yr/GUIDE.md` linked from the README.
- **D13. Don't commit the one-off conversion script.** *Recommended.* Commit `make_smoke.py` on the smoke branch only.

---

## 10. Known uncertainties and fallbacks

**The kernel side is VERIFIED on Colab's exact versions. These are not verified:**
1. **Does Colab's browser stop Run all on a red error output?** (B4) The cell's reply status is "ok", so the kernel doesn't stop it.
   - **Fallback B:** inside `run_code`, temporarily replace `ip._showtraceback` with a function that prints `ip.InteractiveTB.stb2text(stb)` to stderr, then call `ip.run_cell(code)`.
   - The traceback text is identical, but there is no error output at all (VERIFIED on IPython 7.34 and 9.17). The checks already read stderr, so this is a one-function change.
2. **Are Answers closed on open from GitHub?** (A1/B1) The format matches real Colab-saved files exactly, but Colab honouring it hasn't been observed. Tests 2 and 3 show which markers Colab really needs.
   - **Fallback C:** if closed sections don't work, or Run all opens them:
     - run cells sit outside any closed section and call `run_hidden(r"""…""")`;
     - `run_hidden` captures stdout, the traceback text, the last drawing and the last value into one closed HTML "Show the output" box, and attaches the exact values as metadata for `check_review`;
     - the explanation stays a `<details>` block, as today.
     - VERIFIED locally on both stacks; B8 tests that Colab renders it.
     - **Costs:** no live animation, and tracebacks lose colour.
3. **Error badges** (B5). A red mark on a closed section would hint which Answers are errors → variant B.
4. **Keyboard stepping** (A4/B9). JupyterLab's Shift+Enter opens closed Answers (VERIFIED). A 2018 Colab issue says Down-arrow did too. Mitigation: D10.
5. **The `python run` marker in Colab** (B2). Verified on the website; in Colab it is BELIEVED (renderers use the first word). Fallback: a cell tag.
6. **Editing a page in Colab and saving** (B11). Colab may add outputs and `metadata.id` to every cell, and may change the closed layout: it has a separate "Save collapsed section layout" command. `normalize` repairs all of this, and `check_notebooks` (also in CI) fails until it's repaired.
7. **Version drift.**
   - Colab pins IPython 7.34 / ipykernel 6.17.1 on Python 3.12, possibly moving to 3.13; the checks run IPython 9.17 on 3.13.
   - Error lines are compared by substring, and V1 runs the checks on both stacks.
   - Traceback headers differ by stack: `/tmp/ipykernel_…` on Colab, `Cell In[N]` locally, where N is one more than the prompt number. Answers never quote headers.
   - Colab appends a NOTE to ModuleNotFoundError (ch02 Q14a); this is harmless.
8. **Stop button.** Re-raising KeyboardInterrupt makes Stop halt Run all (VERIFIED, kernel side; S1 tests Colab). Cost: the interrupt message prints twice.
9. **Running a cell inside a cell.** `run_code` runs IPython's hooks twice per cell. This is untested in Colab; watch B7 for duplicated output.
10. **VS Code / "Colab in VS Code".** Answers show open (BELIEVED from source). Accepted and documented.
11. **The January 2026 Colab redesign.** Labels like "↳ N cells hidden" and the Settings path may differ. The help note's final wording waits for A1/P7.
12. **Run all on ch04** animates several turtle drawings in hidden cells, so it may take a minute or two (A2 records the time for ch05).

**Scratch artifacts** used by this plan (temporary): `/tmp/claude-0/-home-user-yrThinkPython/6571a165-f8cc-5e43-8b74-c00357a4a6f6/scratchpad/ultra/`:
- `plan-risk/` (smoke notebook generator and logs);
- `plan-maint/` (equivalence script `exp.py`, conversion `conv3.py`);
- `plan-student/` (run_code and Stop tests);
- `proto/` (prototype converter, adapted tools, mutations);
- `verify-repo/` (`runvis.py`, mutations);
- `verify-jupyter/` (traceback and interrupt tests).

The prototype is also saved on branch `yr-runall-research` under `yr/plans/research/prototype/`.

## assumptions_needing_colab_test

- A1/B1: A notebook opened via colab.research.google.com/github/... opens with the '#### Answer' sections closed when metadata.colab.collapsed_sections lists the heading ids and each heading has metadata.id == id. The format is verified from real Colab-saved files; that Colab honours it on open is believed, not observed. Smoke Tests 2 and 3 show whether the top-level id alone or only jp-MarkdownHeadingCollapsed is enough.
- A2/B3: Runtime > Run all executes the code cells inside closed sections without opening them or scrolling to them, and their outputs (prints, tracebacks, turtle drawings) stay hidden until the student opens the Answer.
- B4: Colab's browser side continues Run all past a cell that shows a red 'error' output while its execute_reply status is 'ok' (run_code via nested get_ipython().run_cell). The kernel side is verified on Colab's pinned ipykernel 6.17.1 / IPython 7.34.0 with queued requests. If Colab stops anyway, the stderr variant (fallback B) is verified locally and the checks already parse stderr tracebacks.
- B5: No red badge, error icon, toast or 'Explain error' chip appears on a closed Answer heading, its 'N cells hidden' row or the contents sidebar that would reveal which Answers contain errors (compare the variant A and variant B rows).
- A4/B9: Stepping with Shift+Enter, the Down arrow or Ctrl+Enter into a closed '#### Answer' section does not open it. JupyterLab's Shift+Enter does open it (verified); a 2018 Colab issue reported that Down-arrow opened sections.
- B2: Colab renders a markdown block fenced ```python run as ordinary highlighted Python without showing the word 'run' (verified on the Jupyter Book site; believed for Colab because renderers use the first word of the info string).
- P1/E1-E7: Nothing visible is underlined by Colab's editor (question code is markdown; setup and definition cells are valid code; run_code strings are never checked), under both the default Code diagnostics setting and 'Syntax and type checking'. The option names and the default of that setting are unknown.
- A3/B7: Errors from run_code look like a normal Colab cell's errors (code line and caret for syntax errors, frames listed outer then inner for ch03 Q14) and appear once, with no duplication from Colab's post-run hooks firing twice; Colab's ModuleNotFoundError NOTE is the only extra text.
- S1: Pressing Stop (Runtime > Interrupt) during a run_code cell halts Run all. The KeyboardInterrupt re-raise is verified on the kernel side on IPython 7.34 and 9.17; the message prints twice.
- B10: Colab's live runtime is IPython 7.34 / ipykernel 6.17.1 on Python 3.12 (pinned in colabtools setup.py; a newer image may use Python 3.13). This affects traceback headers, the IPython>=8 stripping of '>>>' lines inside strings, and version-specific error messages.
- B8: An HTML <details> 'Show the output' box inside a cell output renders and opens in Colab (needed only for fallback C).
- E6: How Colab displays and lints a custom %%magic cell, and whether it warns about an unsupported magic (decides whether the %%run_question alternative is ever worth switching to).
- B11: What Colab writes when it saves (outputs, metadata.id on every cell, collapsed_sections from the current layout or only via 'Save collapsed section layout', whether it keeps cell tags such as remove-cell and the jp-MarkdownHeadingCollapsed key), so that normalize can repair a page the professor edited in Colab.
- A1/P7: The exact wording and placement in the 2026 Colab UI ('N cells hidden', the collapse arrow, the Settings path), used for the help note shown to students.
- A2/P4: The live turtle drawing in a hidden Answer cell renders correctly when the Answer is opened after Run all, and Run all on a turtle-heavy page finishes in a reasonable time.

## dry_choice

Option A with an explicit, visible marker. Each question's code is typed once, as a markdown block fenced ```python run. Students see normal highlighted code, Colab's editor never checks it, and the website renders it as Python.

One command, `review.sh sync NB`, derives everything else:
- It generates the Answer's code cells from those blocks, one per block in order. Multi-part questions are interleaved after each '**Part x:**' explanation, and existing ids are kept.
- It runs the page once and wraps exactly the cells that raise in run_code(r"""...""") (r''' when the code has """). It refuses code it can't quote exactly, and code with '>>>' lines, because IPython 8+ strips those even inside strings.
- It writes the managed help and run_code cells, the collapse metadata (colab.collapsed_sections, metadata.id, jp-MarkdownHeadingCollapsed) and the turtle pictures, and strips outputs.

`review.sh check` fails if sync would change anything: run-cell code vs. block compared via ast unwrapping (also run statically by check_notebooks.py and in CI), 'wrapped exactly when it raises' at run time, and turtle_images --check.

Rejected:
- B (string variables: one-colour code, `q8a = """` on the site, an order dependency).
- C (reading the .ipynb fails in Colab).
- An invisible cell tag as the marker (may not survive Colab saves; it is the fallback if Colab renders 'python run' badly).
- A %%run_question magic for the Answer cells (verified in IPython, but it adds Colab unknowns: the unsupported-magics check and linting of magic bodies). It is kept as an optional later switch in one function if smoke test E6 is clean.

