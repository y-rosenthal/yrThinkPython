# plan:1

## Run-all-safe review pages with live Answers in collapsed sections: implementation plan, student experience first

# Run-all-safe review pages with live Answers: implementation plan (student experience first)

Evidence labels used below: **VERIFIED** means tested here or seen in primary sources. **BELIEVED** means strong but indirect evidence. **UNKNOWN** means it must be tested in live Colab (section 10).

---

## 0. Why the 3rd and 4th research workers errored (the question you asked)

**VERIFIED**, from the workflow journal (`/root/.claude/projects/-home-user-yrThinkPython/6571a165-.../subagents/workflows/wf_f52e2176-172/journal.jsonl`) and the two workers' transcripts:

- **What was cut off.** Worker 3 was `research:repo` (agent `af37ec9aba7ebfba4`) and worker 4 was `research:prototype` (agent `a1fdadaddebba8544`). Both transcripts end at the same instant, **2026-10-08 17:20:58 UTC**, with `[Request interrupted by user]`.
  - The session was interrupted while they were running. Workers 1 and 2 had already finished (at 17:09 and 17:15), so only 3 and 4 were cut off.
  - The cause was not the task, the scripts or the container.
- **It has already been fixed and the work continued.** The workflow relaunched at 17:24:01.
  - Workers 1 and 2 were reused from the cache.
  - Workers 3 and 4 re-ran from scratch (agents `a20fcc3ef3b159eda`, finished 17:36, and `a24699395a4a294b3`, finished 17:55).
  - Their results are the "repo" and "prototype" findings this plan is built on. The verification and design phases ran after them. **Nothing needs fixing.**
- **The traps the workers guessed at were not the cause.** Those environment traps are real: no `rsync`; `git rev-parse` fails in copies; Playwright wants a browser build that isn't installed; `pkill -f` kills its own shell. They are listed in section 9 so the implementation avoids them.
- **To avoid a repeat:** pressing Esc/Stop while a workflow runs kills the workers in progress. Finished workers are kept, and a relaunch re-runs only the unfinished ones.

---

## 1. The design in one paragraph

Each question shows its code as **highlighted markdown**. Nothing in the question can be run, so nothing in it can give away an answer, and Colab's editor never sees it, so there are no squiggles.

Under each question is a **`#### Answer` heading saved collapsed**, for both Colab and JupyterLab. Under that heading are:
- the explanation, with the expected output as text or a stored picture, as today;
- **one code cell per question code block**, holding exactly the question's code, which shows the **real output** when run.

Code that raises goes through `run_code("""...""")`. It shows the error like a normal cell, but the cell still ends with status "ok", so **Run all reaches the end**.

**Single source.** The question's code is written once, in markdown cells tagged `question-code`. `review.sh sync` generates the Answer's code cells from them, and `review.sh check` fails if the two ever differ.

**Website.** The website folds each Answer section back into today's closed "Answer" dropdown and drops the run cells. The site looks as it does today.

---

## 2. What a student sees

### Colab, on opening the page from its "Run this page on Colab" link
- **Layout:** title, Concepts lists (open), Questions intro, then the setup cell (code, no output yet).
- **Each question shows:**
  - its heading;
  - the prompt ("Predict what this code displays, then open the Answer to check.");
  - the code as a markdown code block. Syntax colours are BELIEVED; test C2.
  - Multi-part questions also show **Part a / Part b** labels between the blocks.
- **Under the question:** a small bold **Answer** heading, collapsed, with a "↳ N cells hidden" row.
  - Colab honouring `collapsed_sections` when a notebook is opened from GitHub is BELIEVED (strong evidence: Google's own course notebooks rely on it). Test C1. The exact wording after Colab's 2026 redesign is UNKNOWN.
- **Questions that keep a code cell:**
  - questions with a definition ("Run this cell to define `countdown_by_two`") keep that runnable cell, which displays nothing;
  - write-code questions keep their `# Your code here` cell.
- **No squiggles anywhere visible.**
  - Question code is markdown, which is not sent to the checker (BELIEVED). Code inside strings is ignored by Pyright (VERIFIED).
  - Setup and definition cells are valid code.

### Colab, after Runtime > Run all
- **What runs:** Run all runs the setup cell, the definition cells, the student's own `# Your code here` cells, and every hidden Answer cell.
  - That it runs hidden cells is BELIEVED; one notebook on GitHub collapses its setup sections and still tells users to use Run all. Test C3.
  - If a student wrote broken code, Run all stops at *their* cell, as in any notebook.
- **Why it doesn't stop:** `run_code` turns errors into a displayed traceback while the cell's status stays "ok".
  - VERIFIED on Colab's pinned kernel stack (ipykernel 6.17.1, IPython 7.34.0) with queued requests, as Run all sends them. An uncaught error aborts the queued cells; a `run_code` error does not.
  - Whether Colab's *frontend* also stops on a displayed error is UNKNOWN. Test C3; the fallback is ready, see section 6.
- **What stays visible afterwards:** only the setup cell's one-time "Downloaded jupyturtle.py / words.txt" line (ch04, ch05, ch07). All other outputs sit inside collapsed Answers.
  - VERIFIED in the nbclient simulation on all six prototype pages and in JupyterLab 4.6.4.
  - Not auto-expanding in Colab is UNKNOWN. Test C3.
- **Possible weak hints:**
  - the "N cells hidden" count, which only reveals the number of parts, and the question already shows that;
  - any error badge Colab might show on a collapsed section (UNKNOWN, test C3).

### Opening an Answer
- **How:** click the arrow next to **Answer**, or the "N cells hidden" row.
- **What appears:**
  - the explanation with the expected output (text block or stored PNG);
  - directly below it, the code cell with **the same code as the question and its real output**: the printed lines, the red traceback, the turtle drawing, or the `Out:` value;
  - for multi-part questions, **interleaved**: "**Part a:** explanation", then Part a's live cell, then "**Part b:** ...", and so on.
- **If Run all wasn't used:** the cell has a ▶ button. The intro tells students to run the setup cell first.
- **Experimenting:** students can edit the Answer's cell to try variations.
- **How errors look:** like a normal cell's errors. There is no `run_code` frame, and line numbers count from the first line of the question's code (examples in section 6).

### Write-code questions
- The student types into `# Your code here` and runs it. The intro recommends **Ctrl+Enter** (run and stay); see the Shift+Enter note below.
- The Answer shows the suggested solution(s) as standalone ```python blocks, as today, with **no run cells**.

### JupyterLab 4 / Notebook 7 (VERIFIED with JupyterLab 4.6.4 in a browser)
- The page opens with every Answer collapsed. "Run All Cells" runs the hidden cells, and their outputs stay hidden. Expanding an Answer shows the real output.
- **Known issue (VERIFIED):** pressing **Shift+Enter** on a collapsed Answer heading moves into the section and **expands it**; Down-arrow skips it.
- **Mitigation:** question cells no longer need running (except definitions), and the instructions say "use Run all, then read; run your own code with Ctrl+Enter". Colab's behaviour here is UNKNOWN (test C6). A 2018 Colab issue reported that Down-arrow expanded collapsed sections.

### Website (Jupyter Book; it does not execute review pages)
- Unchanged look: the same closed **Answer** dropdown with the same text and pictures as today.
  - VERIFIED in the prototype build: dropdown text identical, 0 `h4`, 0 "Answer" entries in the page table of contents, no new warnings.
- Question code shows as code cells, as today, if decision D7 is adopted (prep converts them); otherwise it shows as highlighted code blocks.
- The prompt "then open the Answer to check" fits both the website and Colab.

### VS Code, and "Colab in VS Code/Cursor" (Colab launched this in January 2026)
- Both collapse markers are ignored (BELIEVED from VS Code source), so Answers and their outputs are visible.
- The title cell says so, in one sentence, and recommends Colab or JupyterLab.

---

## 3. Page layout

### 3.1 Page-level cells (all six pages)

**1. Title cell.** Replace "Each question has a suggested answer: click **Answer** to reveal it, but try the question yourself first." with the following. Finalize the wording after test C1/C3, using Colab's real labels.

> Each question has a suggested answer under a closed **Answer** heading. Try the question yourself first, then click the arrow next to **Answer** to open it (on the website, click **Answer**). On Colab you can start with **Runtime > Run all**: it runs every cell, including the hidden ones in the Answers, and the Answers stay closed until you open them. (Editors that do not support collapsed sections, such as VS Code, show the Answers open.)

**2. Questions intro.** Replace the current `run_code` paragraph with:

> In Colab or Jupyter, each Answer also has a code cell that runs the question's code, so you can see its real output: run it, or use Run all. When that output is an error, the cell runs the code with `run_code("""...""")`, defined in the next cell. It shows the error just as a normal cell would, but does not stop Run all. Run the next cell first: ...

ch06 gets this paragraph, and `run_code`, for the first time.

**3. Setup cell.**
- Tagged `setup`.
- Ends with the `run_code` definition from section 6. On ch02, ch03, ch04, ch05 and ch07 it replaces the `exec` version; on ch06 it is appended.

**4. Last cell.**
- It becomes `## Credits` followed by a blank line and the current credit text.
- The heading ends the last Answer section. Without it, the credits are hidden inside Question 17's Answer (VERIFIED).
- Decision D6: prep removes the `## Credits` line on the website.

### 3.2 The cell kinds (exact JSON)

**Question-code cell.** A markdown cell holding exactly one ```python block, with nothing else in the cell:
```json
{"cell_type": "markdown", "id": "5d1f0a2c", "metadata": {"tags": ["question-code"]},
 "source": ["```python\n", "x = 5\n", "if x = 5:\n", "    print('five')\n", "```"]}
```

**Answer heading.** Collapsed for both Colab and JupyterLab; `metadata.id` must equal `id`:
```json
{"cell_type": "markdown", "id": "9c41e7b2",
 "metadata": {"id": "9c41e7b2", "jp-MarkdownHeadingCollapsed": true},
 "source": ["#### Answer"]}
```

**Run cell.** A code cell under the Answer heading:
- generated by sync;
- plain code if it doesn't raise, otherwise wrapped in `run_code`;
- no tags;
- no added comment lines, because they shift traceback and doctest line numbers (VERIFIED: ch07 Q14 broke).
```json
{"cell_type": "code", "execution_count": null, "id": "<old question code cell id>", "metadata": {}, "outputs": [],
 "source": ["run_code(\"\"\"\n", "x = 5\n", "if x = 5:\n", "    print('five')\n", "\"\"\")"]}
```

**Notebook metadata.** `collapsed_sections` lists exactly the Answer heading ids, in page order:
```json
"metadata": {"colab": {"collapsed_sections": ["9c41e7b2", "..."]},
             "kernelspec": {"display_name": "Python 3 (ipykernel)", "language": "python", "name": "python3"},
             "language_info": {"name": "python"}}
```

**Other cell kinds:** definition cells (code cells that display nothing), `# Your code here` cells, and ordinary markdown.

### 3.3 Layout for each kind of question

In the table, Q is the question part, before `#### Answer`, and A is the Answer section.

| Kind (examples) | Q | A |
|---|---|---|
| **What is displayed** (ch05 Q1; most "wid" questions) | heading, prompt "Predict what this code displays, then open the Answer to check.", one question-code cell | markdown: ```text exact output + explanation; then a plain run cell |
| **Last-expression display** (ch02 Q4, ch03 Q9) | same; ch02 Q4's prompt becomes "What does this code display when it is run as a notebook cell?" | the ```text block must show the displayed value: ch02 Q4's Answer needs a new ```text `12` block (VERIFIED missing today); ch03 Q9 already has it. The plain run cell shows `Out: 12`, and the check now verifies it |
| **What is drawn** (ch04 Q2, Q6; ch05 Q17) | question-code cell starting with `make_turtle()` | markdown with the stored `<img data-turtle>` PNG + explanation; then a plain run cell (live drawing) |
| **What happens, one error** (ch07 Q8; ch04 Q7 draws and then hits a NameError) | question-code cell | markdown with ```text for any prints, ```text `NameError: ...` (and the PNG for ch04 Q7) + explanation; then a `run_code(...)` cell |
| **Multi-part errors** (ch02 Q9, Q10, Q14; ch03 Q10; ch04 Q14, Q15; ch05 Q8) | prompt, then "**Part a**" + question-code cell, "**Part b**" + question-code cell, ... | interleaved: "**Part a:** ..." markdown, then run cell a, "**Part b:** ..." markdown, then run cell b, ... Parts that run without error are plain cells (ch02 Q9 a and e, ch04 Q14 c) |
| **Wrong calls with a definition** (ch03 Q10, Q14; ch04 Q14, Q15; ch05 Q14; ch06 Q15) | "Run this cell to define f." plus the **definition code cell** (stays runnable, displays nothing); "Two correct ways to call it:" examples with output (markdown); question-code cell(s) with the wrong call(s) | explanation (and the fixed function as a standalone ```python block); then `run_code(...)` cell(s) |
| **Find the bug, no error** (ch02 Q15, ch06 Q8) | question-code cell; prose describes what the code should do | actual output in ```text, the fix as a standalone ```python block; a plain run cell shows the buggy output |
| **Doctest** (ch07 Q14) | question-code cell with the whole program, including `run_doctests` | ```text report + explanation; a plain run cell, byte-identical to the question so the report's `line 9` stays right |
| **Reading a file** (ch07 Q9, Q15) | as "what is displayed" (words.txt comes from setup) | as "what is displayed". ch07 Q15's "(...then run it...)" becomes "...then open the Answer, which runs it" |
| **Write code / refactor / docstring / generalize** (34 questions) | prose with the header block (`def f(...):` / `    ...`), at least 2 examples with ```text or a picture; refactor questions show the given code as **untagged** ```python blocks; a `# Your code here` cell | markdown only: suggested solution(s) as standalone ```python blocks; **no run cells** |

### 3.4 Structural rules (enforced by the checks)

- **What a question is:** a question runs from its `### Question N (level): kind` cell to the next `#`, `##` or `###` heading.
- **One Answer heading:** exactly one `#### Answer` cell per question, with exactly that text.
- **No other headings inside a question.** That means no ATX heading, no setext underline (`===` or a `---` line after text), and no HTML `<h1>`–`<h6>`.
  - A heading inside an Answer ends the collapsed section early and exposes the live outputs after it (VERIFIED, mutation M3).
  - JupyterLab treats a markdown cell as a heading if it contains a heading **anywhere** (source read).
- **Which code cells go where:**
  - before the Answer heading: only definition cells (no output) and `# Your code here`;
  - after it: only run cells.
- **Removed:** `raises-exception` tags (Colab ignores them) and `<details>` Answer cells.
- **End of page:** the last question's Answer is followed by `## Credits`.

---

## 4. How Answers collapse on each platform

| Platform | Mechanism | Status |
|---|---|---|
| Colab, opened from GitHub | `metadata.colab.collapsed_sections` lists the heading ids. We also copy `id` into the heading's `metadata.id`, which is what Colab itself writes for nbformat 4.5 files (seen in a Colab-saved file) | format VERIFIED from real Colab-saved files; honoured on open BELIEVED (C1); Run all runs hidden cells BELIEVED (C3); outputs stay hidden UNKNOWN (C3) |
| JupyterLab 4 / Notebook 7 | cell metadata `jp-MarkdownHeadingCollapsed: true` | VERIFIED: opens collapsed, Run All keeps hidden outputs hidden; Shift+Enter expands (VERIFIED) |
| Website | `prep_notebooks.answer_sections` merges the heading and the markdown under it into one `:::{admonition} Answer` + `:class: dropdown` cell and drops the run cells (each markdown cell is parsed separately, so a dropdown cannot span cells: VERIFIED) | VERIFIED in the prototype build |
| VS Code | none (folding is editor view state) | BELIEVED: nothing hidden |

**Fragility (BELIEVED):** if the professor edits a page in Colab and saves, the collapsed layout can change or be dropped. Colab has an explicit "View > Save collapsed section layout" command, and it adds outputs and `metadata.id` to cells. For that reason:
- `review_cells.py normalize` re-applies the layout;
- `check_notebooks.py` fails if it's wrong.

---

## 5. Don't Repeat Yourself: one source for the question's code (option A, made explicit)

- **Authors write the question's code once**, in `question-code` cells.
  - Tags are invisible to students: Colab has no tag UI (BELIEVED), JupyterLab shows tags only in its property inspector, and the website ignores them.
  - An explicit tag replaces the prototype's guessing rule, which misfired on six refactor questions (chap03 Q12; chap04 Q11, Q17, Q18, Q19; chap06 Q12) (VERIFIED).
- **`yr/tools/review.sh sync NB` generates the run cells:**
  1. For each question without `# Your code here`, pair its question-code cells with the code cells under its Answer, in order.
  2. Update each pair's source. Append missing run cells at the end of the Answer. Delete extras and report them. **Keep the ids** of existing run cells. Positions inside the Answer are kept, so interleaving survives.
  3. Run the page once (nbclient, `allow_errors=True`).
  4. Wrap every run cell that produced an error in `run_code(...)`, and unwrap any wrapped cell that produced none.
  5. Run `normalize` (collapse metadata, no outputs).
- **Quoting rules for the wrapper:**
  - default: `run_code("""\n<code>\n""")`;
  - if the code contains a backslash: `run_code(r"""...""")`. Without the `r`, a `\n` inside a string in the question's code would become a real newline and change the code;
  - if the code contains `"""`: use `'''`;
  - if it contains both: refuse and tell the author.
- **`review.sh check` recomputes the same mapping** and fails with "run `yr/tools/review.sh sync NB`" when anything differs. It unwraps with `ast.literal_eval`, not a regex.
- **For the student:** the question code is ordinary highlighted code. The only "duplicate" appears inside the opened Answer, where seeing the code next to its real output is the point.
- **Rejected options:**
  - B (`q8a = """..."""`): the question's code reads as a one-colour string, and the website shows `q8a = """`.
  - C (read the notebook file): doesn't work in Colab.
  - C' (a custom `%%question` magic): plain Pyright flags the magic line *and* the very syntax errors students must predict (VERIFIED). Colab has linted `%%writefile` bodies before and has an `unsupported_magics_check` flag.
  - Per-cell `# type: ignore`: Colab most likely joins cells into one document, so a cell's first line isn't the top of the file (BELIEVED).

---

## 6. run_code

The definition goes at the end of every setup cell:
```python
def run_code(code):
    """Run code (a string) as if it were a cell of its own: show its output, and its error if it
    raises, without stopping "Run all". The Answers use it for code whose result is an error.
    (Code in a string is also not underlined by Colab's editor.)"""
    try:
        ip = get_ipython()
    except NameError:              # plain Python (e.g. yr/tools/turtle_images.py): just run it
        exec(code, globals())
        return
    result = ip.run_cell(code, store_history=False)
    if isinstance(result.error_in_exec, KeyboardInterrupt):
        raise KeyboardInterrupt    # the Stop button still stops "Run all"
```

**Behaviour, all VERIFIED in this container on IPython 9.17.1 / Python 3.13 and on Colab's pinned stack (IPython 7.34.0, ipykernel 6.17.1, Python 3.12.3):**
- The reply status is "ok" for syntax errors, runtime errors and nested-function tracebacks, so queued cells keep running.
- A final expression is displayed (`price * 3` gives `Out: 12`).
- In plain Python, run_code runs the code with `exec`.
- **Stop:** when the student presses Stop during a slow `run_code` cell, the reply status is "error" and the queued cells are "aborted", so Run all stops. Cosmetic cost: the KeyboardInterrupt traceback prints twice.

**How errors look on Colab's stack** (the same as a normal Colab cell):
```text
  File "/tmp/ipykernel_20358/445721521.py", line 2
    if x = 5:
       ^
SyntaxError: invalid syntax. Maybe you meant '==' or ':=' instead of '='?
```
```text
NameError                                 Traceback (most recent call last)
/tmp/ipykernel_20358/1243571756.py in <cell line: 0>()
      1 print('start')
----> 2 print(total)

NameError: name 'total' is not defined
```
- **Other tracebacks:** a function traceback (ch03 Q14's subject) shows the module frame and then `in outer(s)`, in order.
- **IPython 9** (the local check venv) labels it `Cell In[N], line 2`, where N is one more than the cell's prompt number.
- **Rejected:** the `exec` + `showtraceback()` variant shows a `run_code` frame and "Could not get source" on IPython 9. The linecache variant drops frames on 7.34. Both were rejected (VERIFIED by the jupyter skeptic).

**Fallback, if C3 shows that Colab stops Run all on a displayed error** (built and VERIFIED locally on both stacks):
- It prints the identical traceback to **stderr** instead of creating an error output.
- It temporarily sets `ip._showtraceback = lambda et, ev, stb: print(ip.InteractiveTB.stb2text(stb), file=sys.stderr)` around `ip.run_cell(code)`, then deletes the override.
- `check_review` will parse the last line of a stderr traceback as the error line (section 7.4), so switching doesn't weaken the checks (the skeptics' mutation M15 showed it would otherwise).

**Colab-only detail:** Colab appends a NOTE to ModuleNotFoundError tracebacks (ch02 Q14a). It is harmless: answers are compared by substring.

---

## 7. Tool changes

### 7.1 New: `yr/tools/review_format.py`
Stdlib only, so the format is defined in one place. It is imported by `review_cells.py`, `sync_answers.py`, `check_review.py`, `turtle_images.py`, `check_notebooks.py`, and by `jb/prep_notebooks.py` through `sys.path` (`../yr/tools`).
- **Constants:** `ANSWER_HEADING='#### Answer'`, `QUESTION_CODE_TAG='question-code'`, `PLACEHOLDER='# Your code here'`, `CREDITS_HEADING='## Credits'`.
- `text(cell)`: works for list or str sources, so it handles both JSON-loaded dicts and nbformat nodes.
- `heading_level(md)` and `has_heading(md)`: ATX, setext and HTML headings, outside code fences.
- `questions(cells)`: one record per question, with `title`, `cells`, `heading` (the Answer heading cell), `qpart`, `answer`, `qcode` (question-code cells), `defs` (definition cells), `placeholders`, `runs`, `answer_md`.
- `question_code(cell)` and `unwrap(source)`:
  - `unwrap` returns `(code, wrapped)`;
  - for a wrapped cell, `ast` must see a single call to `run_code` with one string literal;
  - anything else starting with `run_code(` is a ValueError.
- `wrap(code)`: applies the quoting rules from section 5.
- `apply_collapse(nb)` and `collapse_problems(nb)`.

### 7.2 `yr/tools/review_cells.py` (stdlib)
- **SKELETON:**
  - new title and intro text (3.1);
  - setup cell with `run_code`;
  - credit cell starting with `## Credits`;
  - notebook metadata gains `"colab": {"collapsed_sections": []}`.
- **`parse_spec`** cell kinds:
  - `%%% markdown`;
  - `%%% code [tags]` (definition cells);
  - `%%% placeholder`;
  - **`%%% question`**: the body becomes a question-code cell;
  - **`%%% answer`**: a collapsed heading plus the markdown body;
  - **`%%% run`**: the next run cell, filled from the matching question block. Further `%%% markdown` cells after the answer continue it, so authors can interleave parts.
- **`cmd_add`:**
  - inserts before the `## Credits` cell;
  - fills or appends run cells from the question cells (plain);
  - runs `apply_collapse`;
  - prints "now run `review.sh sync`, `review.sh images`, `review.sh check`".
- **New `normalize NB`:**
  - clears outputs and execution counts;
  - drops the cell metadata Colab adds (`executionInfo`, `outputId`, `colab`, and `metadata.id` on any cell other than an Answer heading);
  - re-applies the collapse layout.
- `list` and `renumber` are unchanged. The usage docstring shows a full spec example.

### 7.3 New: `yr/tools/sync_answers.py`, run as `review.sh sync NB`
- Implements section 5 using nbformat, nbclient and review_format.
- Idempotent: a second run reports "0 questions changed".
- `review.sh` gets a `sync)` case that runs it, like `check`, using the venv and the cached `jupyturtle.py`.

### 7.4 `yr/tools/check_review.py`
It keeps every existing check, makes two of them stronger, and adds new ones.

**How it runs:**
- One execution with `allow_errors=True` plus nbclient's `on_cell_executed` hook, which records each cell's reply status. Hook available in nbclient 0.11.0 (VERIFIED).
- So it sees the full outputs **and** every place Run all would stop, ignoring tags, as Colab does.

**Error lines** come from `error` outputs, **plus** the last line of a stderr traceback in a `run_code` cell, so the fallback cannot blind the checks.

**Numbered checks:**
1. **Run all reaches the end:** every cell's reply status is "ok". The message names the cell and question and suggests `review.sh sync`.
2. **Nothing gives the answer away after Run all:** a visibility pass uses the collapse rules (section 3.4). Every code cell with output, except `setup` cells, must sit under a collapsed Answer heading. Definition cells must show nothing.
3. **Structure:**
   - exactly one `#### Answer` per question, and no other heading inside a question;
   - `## Credits` after the last Answer;
   - no `<details><summary>Answer`;
   - no `raises-exception` tags;
   - question-code cells hold exactly one ```python block.
4. **Saved collapsed:**
   - `metadata.id == id` and `jp-MarkdownHeadingCollapsed` on each Answer heading;
   - `colab.collapsed_sections` equals exactly the Answer heading ids.
5. **Single source:**
   - run cells match question-code cells one to one, in order, byte-identical after unwrapping;
   - write-code questions have neither;
   - every other question has at least one, which fails closed if an author forgets the tag.
6. **`run_code` exactly when the code raises.** This restores the old "tagged but raised nothing" guard and covers the old syntax-error rule.
7. **The Answer text matches the live output:**
   - stdout equals one ```text block exactly (existing);
   - each error line appears in a block (existing);
   - **new:** an `execute_result`'s `text/plain` equals a ```text block;
   - **new:** every `XxxError: ...` line in the Answer's text blocks is produced by one of that question's run cells. This closes the skeptics' mutation M1. It was run on all six converted pages: 0 violations (VERIFIED).
8. **Standalone answer blocks:** each ```python block in the Answer runs on its own as a `.py` file (existing).
9. **Write-code and wrong-call checks:**
   - write-code questions show headers and at least 2 examples (existing). Examples are counted only in prose cells, which excludes question-code cells and fixes the over-count risk in the example-matching regex;
   - wrong-call questions show at least 2 correct calls (existing). A wrong-call question is one where a run cell raises and a definition cell or the question code contains `def`.
10. **No empty turtle pictures** (existing).
11. **No `(c)`, `(r)`, `(tm)` or `+-` symbol hazards** (existing).

**Optional:** an environment variable to run the kernel from another venv, so the check can also be run on the Colab-like stack.

### 7.5 `yr/tools/turtle_images.py`
- Uses `review_format.questions`.
- **Per question:** run the setup code, then the Answer's ```python blocks, then walk the cells in order:
  - definition cells and question-code blocks run as they are reached (as code cells do today);
  - run cells are **skipped**, because they repeat question code and may call `run_code`.
- **Picture rule:**
  - a ```python block above the picture in the same cell (unchanged);
  - otherwise, for a picture in an Answer cell, the question-code block of the **next run cell below it** (index = number of run cells above it), else the last question-code block.
- This removes the false `make_turtle(` warning and the bug where the current tool rewrote 19 ch04 pictures with partial NameError drawings (VERIFIED by the repo skeptic).

### 7.6 `jb/prep_notebooks.py`, function `process_review`
1. Drop `# Your code here` cells (as now).
2. `raw_pictures` and `details_to_dropdown` (as now; they handle the open Concept lists).
3. **New `answer_sections`:**
   - merge each `#### Answer` heading and the markdown cells under it, up to the next heading of level 1 to 4, into one `:::{admonition} Answer` + `:class: dropdown` cell (keeping the heading's id);
   - drop the run cells (they duplicate the question code, and the site doesn't execute).
4. **New, decision D7:** turn `question-code` markdown cells into code cells (no outputs) so the site looks as it does today. To verify: this adds no new Pygments lexer warnings.
5. **New, decision D6:** remove the `## Credits` line after step 3.
6. `process_cell` (as now). Never tag Answer cells `solution`: prep blanks them.
7. **New guard:** `SystemExit` with a clear message if any `#### Answer` heading or any `run_code(` cell survives, or if the number of Answer dropdowns differs from the number of questions. A format mismatch then fails the CI build instead of publishing answers in the open.

### 7.7 `check_notebooks.py` and `run_notebooks.sh`
- **`check_notebooks.py`:** new `check_review_page()` for `yr/*.ipynb`, using review_format (fast and static).
  - It covers structure, saved-collapsed metadata, single-source text equality (with `ast`), no `raises-exception` tags and no `<details>` Answers.
  - Its hints point to `review_cells.py normalize` or `review.sh sync`.
  - This catches "edited in Colab and saved" before a commit.
  - `KNOWN_MAGICS` is unchanged (no cell magic is added).
- **`run_notebooks.sh`:** treat error outputs in cells whose source starts with `run_code(` as expected, replacing the `raises-exception` note.
- **Unchanged:** `deploy-book.yml`, `build_book.sh`, `execute_notebooks.py`.

### 7.8 Documentation and skills
- **`yr/README.md`:**
  - Layout items 3–4;
  - Answers;
  - Cell conventions: replace the "collapsible sections", "raises-exception" and run_code paragraphs with: question-code cells, the Answer heading section, run cells, definition cells, the no-headings rule, `## Credits`;
  - turtle picture rule;
  - Tools: `sync`, `normalize`;
  - the list of what `review.sh check` fails on;
  - "How the build handles yr/": `answer_sections` and the guard;
  - a "What students see" note: Run all, Ctrl+Enter, VS Code.
- **`.claude/skills/yr-review-questions/SKILL.md`:** new spec kinds and an example; workflow `add` → `sync` → `images` → `check`; never type run cells by hand; how to interleave multi-part answers.
- **`.claude/skills/yr-review-page/SKILL.md`:** the new skeleton and the steps.
- **`.claude/skills/notebook-conventions/SKILL.md`** line 86 (it mentions the `<details>` answer format).
- **`run_notebooks.sh`** comment.

---

## 8. Converting the six existing pages

The one-off script stays in scratch; it is not committed. It is based on the prototype's `convert.py`, with the fixes found by the skeptics. Input: each page plus an executed copy, which tells which cells print.

1. **Page-level changes:** title sentence, intro paragraph (ch06 gets one), `run_code` in setup, `## Credits`.
2. **For each question:**
   - **Classify code cells.**
     - `# Your code here`: keep.
     - Definition cell (no output in the executed copy, only def/class/import/assignment statements, not tagged `raises-exception`): keep, as a runnable code cell.
     - Anything else is question code. Replace it **in place** with a question-code markdown cell (fresh id; code = `unwrap(source)`), and remember (old id, code).
   - **Old `<details>` Answer:** becomes a `#### Answer` heading (fresh id, collapse metadata) plus the body, which **keeps the old details cell's id**.
   - **Multi-part:** if the question has 2 or more blocks and the body has "**Part x:**" paragraphs in the same order as the question's "**Part x**" labels, split the body before each one and put run cell k after chunk k.
     - A trailing summary stays in the last chunk. Print these 7 questions for a manual look: ch02 Q9, Q10, Q14; ch03 Q10; ch04 Q14, Q15; ch05 Q8.
   - **Run cells:** plain code, **keeping the old code cell's id** (same code, now inside the Answer), no tags.
3. **Text edits.** Each must match exactly once; print any that don't:

| Page / question | Old | New |
|---|---|---|
| all pages, Q1 etc. | "then run it to check" / "then run the cells to check" / "then run the cell to check" | "then open the Answer to check" |
| ch02 Q4 | "What does this cell display when you run it in a notebook?" | "What does this code display when it is run as a notebook cell?" (and add ```text `12` at the top of the Answer) |
| ch02 Q9 | "For each cell, predict whether it runs..." | "For each part, predict whether it runs..." |
| ch02 Q14 | "Each cell has an error on its second line." / "what each cell displays before the error" | "Each part has an error on its second line." / "what each part displays before the error" |
| ch03 Q9 | "What does this cell display in a notebook?" | "What does this code display when it is run as a notebook cell?" |
| ch03 Q10, ch04 Q14 | "For each of the next three cells" | "For each of the three parts" |
| ch04 Q2, ch05 Q17 | "then run it/the cell to check" | "then open the Answer to check" |
| ch04 Q7 | "...run only the setup cell (at the start of the Questions) and this cell" | "...run only the setup cell (at the start of the Questions), and then run this code" |
| ch05 Q8 | "Each cell has one mistake." | "Each part has one mistake." |
| ch07 Q15 | "(...predict what it means, then run it...)" | "(...predict what it means, then open the Answer, which runs it...)" |

   Afterwards, grep the question prose for leftover `cell`, `run it` and `run_code` wording. "Run this cell to define ..." stays: it is still true.
4. Run `apply_collapse`, `nbformat.validate`, then write.
5. **Then, on the branch:** `review.sh sync`, `review.sh images`, `review.sh check`, `check_notebooks.py`, then build.
   - Expected wrap changes from sync: today's 19 `run_code` cells stay wrapped, except ch02 Q9 parts a and e, which become plain. The 5 plain raising cells become wrapped: ch03 Q14, ch04 Q14 a and b, ch05 Q14, ch06 Q15.
   - `images` should leave all 23 PNGs byte-identical.

**Cell ids:** every unchanged cell keeps its id. Only Answer headings and question-code cells are new.

---

## 9. Verification in this container (before any Colab rollout)

- **V1. Checker on both stacks.** `review.sh check` passes on all six pages with the repo venv (Python 3.13, IPython 9). It also passes with the Colab-like venv (`scratchpad/ultra/proto/venv-colablike`: Python 3.12.3, IPython 7.34.0, ipykernel 6.17.1). Substring matching covers version-specific messages (ch04 Q15c "Did you mean 'sides'?").
- **V2. Mutation suite.** Each mutation below must make the check fail:
  - M1: a part edited consistently so it no longer raises;
  - M2: `price*3` changed to `price*4` in the question and the run cell;
  - M3: a `#### Note` heading inside an Answer;
  - M15: stderr `run_code` plus wrong error text;
  - a question edited without sync;
  - run cells swapped;
  - a wrapped cell with no error;
  - a plain run cell that raises;
  - the `jp-MarkdownHeadingCollapsed` key missing;
  - a stale id in `collapsed_sections`;
  - `## Credits` removed;
  - a `raises-exception` tag left;
  - prose inside a question-code cell;
  - a non-write-code question with no question-code cell;
  - a definition cell that prints;
  - an Answer block that isn't standalone;
  - an old `<details>` Answer left;
  - backslash code without the `r` prefix;
  - plus the prototype's 10 mutations.
  
  Reuse `scratchpad/ultra/verify-repo/mut/` and the prototype's `scripts/mutate.py`.
- **V3. Run all simulation** (`verify-repo/runvis.py`) on both stacks: reaches the end, and no visible output except the setup lines.
- **V4. Sync is idempotent:** a second `sync` changes 0 questions, and run-cell ids are preserved.
- **V5. Pictures:** `images` leaves all 23 data URIs byte-identical.
- **V6. Website:**
  - `build_book.sh` reports no new warnings compared with `known_warnings.txt`;
  - per page: Answer dropdowns = number of questions, 0 `h4`, 0 "Answer" (and no "Credits") entries in the page table of contents, dropdown text equal to the current site's after whitespace normalization;
  - question code renders as code cells (D7);
  - screenshots of ch04 Q2 and Q14, ch05 Q8 and Q17.
- **V7. JupyterLab 4.6.4, headless:** opens collapsed; Run All runs everything with outputs hidden; expanding shows the real output.
- **V8. Pyright** on the visible code cells (setup and definitions) together with the cells above them: only the jupyturtle import message.
- **V9.** `check_notebooks.py` passes, `git diff` touches only the intended files, and no outputs are stored.

**Environment traps the workers hit:**
- no `rsync`: use `cp -a` or `tar`;
- `review.sh` and `build_book.sh` need `git rev-parse`: work on a branch in the real repo, or `git init` a copy;
- Playwright: pass `executable_path=/opt/pw-browsers/chromium-1194/chrome-linux/chrome`;
- JupyterLab: start with `jupyter lab --allow-root --LabApp.expose_app_in_browser=True`;
- never `pkill -f PATTERN` where the pattern appears in the same command line: it kills the calling shell;
- an occasional kernel "Address already in use" error goes away on retry (seen here once).

---

## 10. Colab test checklist for the professor (about 25 minutes)

**Links:**
- **L3, available now:** https://colab.research.google.com/github/y-rosenthal/yrThinkPython/blob/yr-runall-research/yr/plans/research/prototype/out/all/chap05_review.ipynb
  - This is the prototype chap05. Local remote-tracking ref `origin/yr-runall-research` at e68aa02; the file is identical to the prototype and has 17 collapsed Answers.
  - Its `run_code` lacks the Stop fix and its multi-part Answers are not interleaved; otherwise it is the proposed layout.
- **L1 and L2: two test notebooks**, already built and simulated here, in `scratchpad/ultra/plan-student/colab_test/`.
  - With your OK, push them to `yr/plans/colab_test/` on the same research branch (not v3).
  - L1: `.../blob/yr-runall-research/yr/plans/colab_test/colab_runall_test.ipynb`. The B tests (stderr tracebacks) come first, then a plain print, `price * 3`, a turtle square, then the A tests (normal error outputs), then an uncollapsed `## End` cell that prints END.
  - L2: `.../colab_stop_test.ipynb`, a 60-second `run_code` cell, then END.
  - Simulated here on both stacks: every status "ok", END reached, the only visible output is the setup line.

**Steps.** Use Chrome, signed in. Take a screenshot at each [shot].
- **C1. Collapsed on open** (L1, L3; also once in a private window) [shot]
  - Before running anything: is every **Answer** collapsed, with an "N cells hidden" row? Write down the exact wording and where the arrow is.
  - Fail → stop and use Plan B (section 13).
- **C2. Readability** (L3) [shot]
  - Is the markdown question code syntax-coloured?
  - Is anything underlined (setup cell, "Run this cell to define" cells)?
- **C3. Run all** (L1) [shot]: Runtime > Run all.
  - (a) Does `END` print under "## End"?
  - (b) Did any Answer open by itself, or did the page jump into one?
  - (c) Is any red mark, error icon, toast or "Explain error" chip visible **outside** the Answers?
  - (d) If it stopped: at which Test?
  - Decision: END printed and nothing opened → design confirmed. Passed Tests 1–2 (B) but stopped at Test 6 (A) → use the stderr `run_code`. Answers opened → Plan B.
- **C4. Live answers** (L1) [shot]: open each Answer.
  - Each error appears once.
  - Test 6 shows the code line and a caret; Test 7 shows both frames; Test 4 shows `12`; Test 5 shows a square.
  - Compare the look of the B tests (1–2) with the A tests (6–7).
- **C5. The real page** (L3): Run all, then open:
  - Q8 (three SyntaxErrors);
  - Q14 (RecursionError; about 20 lines expected on IPython 7.34);
  - Q17 (live tree drawing plus the stored picture).
  - Note how long Run all takes.
- **C6. Keyboard** (L3; reload first)
  - Click Question 1's text and press **Shift+Enter** repeatedly up to Question 3. Does any Answer open?
  - Repeat with **Down-arrow**, and with **Ctrl+Enter** then Down.
  - Click ▶ on an "N cells hidden" row: does it run the cells without opening them?
- **C7. Stop** (L2): Run all, then press Stop during Test 1.
  - Pass = "END: Run all was NOT stopped" never appears.
  - Note whether the KeyboardInterrupt traceback shows twice (expected).
- **C8. Editor settings:** Tools > Settings > Editor > **Code diagnostics**.
  - Write down every option and which one is the default.
  - Select "Syntax and type checking" and reload L3: is anything underlined? Open Q8's Answer: are the `run_code` strings underlined (expected: no)?
  - Restore the default.
- **C9. Versions:** note the Python, IPython and ipykernel versions printed by L1's first cell.
- **C10. Saving**
  - File > Save a copy in Drive. In the copy, open one Answer, press Ctrl+S, reload: is that Answer still open and the rest closed?
  - Then File > Download > .ipynb and send the file (it shows what Colab writes).
- **C11. Contents sidebar:** how are the Answers listed? (cosmetic)
- **C12. Optional:** does View > Expand sections (Ctrl+[) open every Answer? (Decides whether to warn students.)

---

## 11. Rollout order

1. **R0, now.** The professor runs C1–C12 on L3; L1 and L2 after the push. Then the professor decides D1–D13.
2. **R1.** Topic branch from the current review-pages branch (HEAD b389c80). Implement `review_format.py`, `sync_answers.py` plus `review.sh sync`, `check_review.py`, `turtle_images.py`, `prep_notebooks.py`, `review_cells.py` (`normalize`, spec kinds, skeleton), `check_notebooks.py` and `run_notebooks.sh`. If C3 calls for it, switch `run_code` to the stderr variant.
3. **R2.** Convert **chap05 only** and run V1–V9 for it. Push the branch, and the professor checks chap05 from the branch link in Colab (C1, C3, C4, C6). This catches interleaving and Stop-fix issues on a real page.
4. **R3.** Convert ch02, ch03, ch04, ch06 and ch07, with the text edits, and run V1–V9 on all of them.
5. **R4.** README and the three skills.
6. **R5.** Merge tools, pages and docs to v3 **together**: notebooks and `prep_notebooks.py` must never be out of step. Then use `yrpublish` and check the live site plus one Colab link on v3.
7. **R6.** Later, retire the `yr-runall-research` branch.

---

## 12. Open decisions for the professor (recommendation first)

- **D1. One collapsed section per Answer** (explanation plus live cells). *Recommended.* The alternative is two sections ("Run it", then "Explanation"), which doubles the clutter and headings.
- **D2. Order inside the Answer:** explanation first, then the run cell; multi-part answers interleaved per part. *Recommended.* It matches the website's dropdown text and reads well when the cell hasn't run yet. The alternative, all run cells at the end, is the prototype's layout.
- **D3. Single source:** option A with `question-code` tags plus `review.sh sync`. *Recommended* over the prototype's guessing rule, B and C'.
- **D4. Wrap only the cells that raise**, decided by sync running the page. *Recommended.* Wrapping everything uniformly isn't needed once cells are hidden, and it costs syntax colours.
- **D5. `run_code` = nested `run_cell`** with the Stop fix. *Recommended.* Switch to the stderr variant only if C3 fails.
- **D6. `## Credits` heading** in notebooks, stripped on the website. *Recommended.* It keeps the site's table of contents unchanged.
- **D7. Question code shown as code cells on the website** (prep converts the tagged cells). *Recommended*, so the site looks exactly as today; check for no new warnings.
- **D8. Student instructions:** "Start with Run all; run your own code with Ctrl+Enter; VS Code shows Answers open." *Recommended.* Final wording after C1, C3 and C6.
- **D9. Accept the "N cells hidden" count** as a hint: it reveals only the number of parts. *Recommended.*
- **D10. Remove all `raises-exception` tags**, and have the checks forbid them. *Recommended.* Colab ignores them, and in JupyterLab they would hide a cell that really fails.
- **D11. Drop run cells on the website** (the code is just above). *Recommended* over showing a duplicate block.
- **D12. Write-code Answers stay markdown-only.** *Recommended.* A runnable solution cell would redefine the student's function under Run all.
- **D13. If Colab's Shift+Enter opens Answers (C6):** accept it and rely on the instructions. *Recommended*, because question cells no longer need running. Plan B is for the worse case where Run all itself opens them.

---

## 13. Risks and fallback

- **Colab frontend unknowns:** C1 (collapsed on open), C3 (Run all continues; nothing opens; no error badges), C6 (keyboard stepping). The kernel side is VERIFIED on Colab's exact versions; the frontend is not.
- **Plan B, if C1 fails or C3 shows Answers opening:**
  - Keep today's static `<details>` Answers. Put a visible run cell after each one, with every run cell using a `run_code` that captures all output and displays it inside a **closed HTML `<details>` "Real output"** element.
  - This works in any frontend that renders HTML (Colab, JupyterLab, VS Code).
  - Costs: the code shows as a one-colour string; turtle animation is lost; last-expression capture needs a displayhook swap; `check_review` must parse the captured HTML. It needs its own prototype; it has not been built.
  - Colab's 2026 per-cell output-collapse chevron is a possible simpler alternative. Whether it is saved in the file or survives a re-run is UNKNOWN.
- **Version drift:** Colab runs IPython 7.34 (BELIEVED to be on Python 3.12, perhaps moving to 3.13), while the checks run IPython 9 on 3.13. Mitigation: error lines are compared by substring, and V1 runs the check on both stacks.
- **Editing in Colab** can change or drop the collapsed layout: `normalize` re-applies it and `check_notebooks` fails if it's wrong.
- **Version skew:** new notebooks published with an old `prep_notebooks.py` would show every answer openly. Mitigation: one merge, plus the prep guard.
- **Cosmetic:** Colab's and JupyterLab's contents sidebars list 17 "Answer" entries per page.

**Scratch artifacts from this plan:** all under `/tmp/claude-0/-home-user-yrThinkPython/6571a165-f8cc-5e43-8b74-c00357a4a6f6/scratchpad/ultra/plan-student/`:
- `colab_test/colab_runall_test.ipynb`, `colab_test/colab_stop_test.ipynb`, and their generator `make_colab_test.py`;
- `rc_test.py` (run_code variants on both stacks), `intr_test.py` (Stop button), `sim.py` (Run all plus visibility), `probe.py` (new check rules on the converted pages).

Nothing under /home/user/yrThinkPython was modified.

## assumptions_needing_colab_test

- C1: A notebook opened via colab.research.google.com/github/... opens with the '#### Answer' sections collapsed when metadata.colab.collapsed_sections lists the heading ids and each heading has metadata.id == id (format verified from Colab-saved files; honoring it on open is believed, not observed).
- C3a: Runtime > Run all runs the code cells inside collapsed sections (believed from notebooks on GitHub that tell users to use Run all).
- C3b: Run all does not expand or scroll into collapsed Answer sections, and their outputs (prints, tracebacks, turtle drawings) stay hidden until the student opens them (unknown).
- C3c: Colab's frontend continues Run all past a cell that shows an 'error' output while its execute_reply status is 'ok' (run_code via nested run_cell). The kernel side is verified on Colab's pinned ipykernel 6.17.1 / IPython 7.34.0; if Colab stops anyway, switch to the stderr-traceback run_code, which is verified locally and which check_review will parse.
- C3d: No error badge, red icon, toast or 'Explain error' chip shows on a collapsed section, so students cannot tell from outside which Answers contain errors (unknown).
- C6: Shift+Enter, Down-arrow or Ctrl+Enter stepping does not expand collapsed Answers in Colab (JupyterLab's Shift+Enter does expand them, verified; a 2018 Colab issue reports that Down-arrow expanded sections).
- C7: The Stop button halts Run all during a run_code cell (re-raising KeyboardInterrupt is verified locally on both stacks: queued cells abort; the traceback prints twice).
- C2: Colab syntax-colors ```python code blocks in markdown cells, so question code is as readable as a code cell (believed).
- C2/C8: Nothing visible is underlined by Colab's editor (question code is markdown; setup and definition cells are valid code), under both the default and the 'Syntax and type checking' setting; run_code strings are not underlined. The option names and default of Tools > Settings > Editor > Code diagnostics are unknown.
- C4: Errors from run_code look like a normal cell's (code line plus caret for syntax errors, all frames for runtime errors) and appear once, with no duplication from Colab's post-run hooks; Colab adds its NOTE to ModuleNotFoundError (ch02 Q14a).
- C9: Colab's runtime is IPython 7.34 / ipykernel 6.17.1 on Python 3.12 (pinned in colabtools setup.py; a newer image may use Python 3.13), which determines the traceback format and version-specific messages.
- C10: What Colab writes on save (collapsed_sections, metadata.id on every cell, outputs) and whether the collapsed state is kept in a Drive copy; this matters if the professor edits pages in Colab.
- C1/C11: The exact Colab 2026 UI wording ('N cells hidden', where the arrow is) to use in the student instructions, and how Answers appear in Colab's contents sidebar.
- C5: The live turtle drawing in a hidden Answer cell renders correctly when the section is opened after Run all, and Run all on chap05 finishes in reasonable time.

## dry_choice

Option A, made explicit. The question's code is written once, in markdown cells tagged "question-code", each holding exactly one ```python block (students see normal syntax-coloured code, and Colab's editor never checks it). `yr/tools/review.sh sync NB` (new yr/tools/sync_answers.py) generates the code cells under each collapsed '#### Answer' heading from those cells: one per block, in order, keeping existing cell ids and positions. It runs the page once and wraps exactly the cells that raise in run_code("""..."""), using r"""...""" when the code has a backslash. `review.sh check` and the fast `check_notebooks.py` lint fail if any Answer code cell differs from its question-code cell after unwrapping with ast. Write-code questions have neither kind of cell. Rejected: B (string variables read as one-colour text and show `q8a = """` on the website); C (reading the notebook file fails in Colab); the %%question cell magic (plain Pyright flags the magic line and the hidden syntax errors, and Colab has linted magic bodies before); the prototype's guessing rule (it misfired on six refactor questions).

