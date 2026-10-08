# plan:2

## Review pages: question code in the text, live Answers in collapsed sections, one source for every question's code

# Plan: questions as text, live Answers in collapsed sections, one source for each question's code

Priority: maintainability and DRY. The professor and future Claude sessions should write each question's code once. Tools should generate everything that can be derived from it. One check should fail whenever derived content is out of date. Special cases should be as few as possible.

## 0. The decision in brief

1. **Question code is text.** It goes in the question as a markdown block fenced ```` ```python run ````, one block per part. The editor never sees it, so Colab cannot underline anything. The trailing word `run` is the single explicit marker meaning "the Answer runs this".
2. **Each Answer is a collapsed heading section.** It starts with a markdown cell `#### Answer`, saved collapsed for Colab (`metadata.colab.collapsed_sections`, with the heading id mirrored into `metadata.id`) and for JupyterLab (`jp-MarkdownHeadingCollapsed`). It holds the expected output and explanation as before, then one generated code cell per run block.
3. **Answer code cells use a cell magic.** Each starts with the line `%%run_question` followed by the question's code, verbatim. The magic runs the body with `get_ipython().run_cell(...)`. Errors look exactly like a normal cell's, but the cell's reply status stays "ok", so Run all continues. This replaces `run_code("""...""")` (reasons in section 5).
4. **Derived content is owned by one command.** `review_cells.py normalize NB` writes the Answer code cells, the collapse metadata, the shared `run_question` setup cell and output stripping. It is idempotent. Both checks fail unless normalize would change nothing ("check = normalize is a no-op").
5. **One format module.** A new `yr/tools/review_format.py` (stdlib only) defines the format once and is imported by `review_cells.py`, `check_review.py`, `turtle_images.py`, `jb/prep_notebooks.py` and `check_notebooks.py`.
6. **The website keeps working.** `prep_notebooks.py` folds each Answer section into the same collapsed MyST dropdown as today and drops the Answer code cells. The site is not executed.

## 1. What I verified for this plan (beyond the research findings)

Experiments are in `/tmp/claude-0/-home-user-yrThinkPython/6571a165-f8cc-5e43-8b74-c00357a4a6f6/scratchpad/ultra/plan-maint/`. Nothing under the repo was changed.

- **Uniform string wrapping is fragile (VERIFIED).** Converting all six pages with every Answer cell as `run_code(r'''...''')` (via nested `run_cell`) ran cleanly, except one question. On IPython 9.17 (the local checker), ch07 Q14's doctest printed nothing. IPython 9's new doctest-aware `PromptStripper` (`IPython/core/inputtransformer2.py`) strips the indented `>>> ` lines of the *outer* cell, even inside the string literal. IPython 7.34 (Colab) leaves them alone (`dbg6.py`).
- **Quoting is a real problem for string forms (VERIFIED).** ch07 Q? cell 25 contains `'\n'` inside the question code, so a non-raw string would corrupt it. ch04 Q4 contains `"""`, so the generator would need to switch quote styles.
- **The `%%run_question` cell magic works on both stacks (VERIFIED).** Tested on IPython 9.17 / Python 3.13 and on IPython 7.34 / ipykernel 6.17.1 / Python 3.12 (Colab's pinned versions). Results (`mtest.py`, `m9.txt`, `m7.txt`):
  - every cell returns status "ok";
  - tracebacks are normal, with correct line numbers;
  - a last expression is displayed (`price * 3` shows `12`);
  - doctest prompts are intact, and backslashes and `"""` pass through verbatim.
- **Run-all simulation on all six pages, both stacks (VERIFIED).** Pages converted to this layout (`conv3.py` → `new3/`), compared with the originals (`exp.py`; `exp3_py313.txt`, `exp3_ipy7.txt`):
  - 0 cells with reply status "error" (what Colab's kernel queue stops on);
  - 0 outputs outside an Answer, setup excluded;
  - 0 of 103 questions with any difference in stdout, error lines, last-expression values or turtle displays compared with today's pages.
- **Queued Run all and Stop (VERIFIED, `intr.py`, both stacks).**
  - Three requests sent at once, the way Run all sends them, with two `%%run_question` errors: all three return "ok".
  - Interrupting a running `%%run_question` cell returns "error", so Stop still halts Run all. The KeyboardInterrupt traceback prints twice (cosmetic).
- **Cell ids (VERIFIED).** Converting in place kept the old ids on 187 cells (37/29/34/30/28/29): question code cells became run-block cells, and `<details>` cells became explanation cells. New ids are needed only for the Answer headings and the Answer code cells.
- **Website (VERIFIED).** A mini Jupyter Book with the repo's `_config.yml` and the prototype's `answer_sections` prep, building ch04 and ch07:
  - "build succeeded" with no warnings;
  - 19 and 17 collapsed Answer dropdowns;
  - 0 h4 headings and 0 "Answer" entries in the page contents;
  - ```` ```python run ```` blocks render as `highlight-python`, and the word "run" is not shown. myst-parser's `render_fence` uses only the first word of the info string.
- **A new last-expression check finds one real gap (VERIFIED, `combined.py`).** The check compares stdout plus last-expression value with the ```text blocks. It flags exactly one question: ch02 Q4's Answer gives `12` as inline code, not in a ```text block as the README requires.
- **Turtle pictures.** The only Answer pictures without a ```python block of their own (ch04 Q2, Q6, Q7; ch05 Q17) belong to questions with exactly one run block. "Draw the question's run block" is therefore unambiguous today.
- **Rejected check idea (VERIFIED).** "Every ```text block in an Answer equals some real output" fails legitimately on ch02 Q15 (find the error), whose Answer shows the corrected output `80.0`. The narrower rule "every error *named* in an Answer is actually raised" holds on all six pages and is adopted (B5 below).

## 2. The page format

### 2.1 Page skeleton (in order)

1. Title cell `# NNb. Prof. Rosenthal's Review` (unchanged, wording tweak: "click **Answer** (in Colab or Jupyter, the arrow next to it)").
2. `## Concepts covered` with the two `<details open>` lists (unchanged).
3. `## Questions` intro. It includes the standard paragraph below, written to be true on both the site and Colab:
   > Each question is followed by a collapsed **Answer**: click it (in Colab or Jupyter, the arrow next to **Answer** or the "cells hidden" line under it) to open it. Try the question first. In Colab you can use **Runtime > Run all**: each Answer ends with a `%%run_question` cell that runs the question's code, so an opened Answer also shows the code's real output. Errors are shown there without stopping Run all.
4. The page's own setup code cell, tagged `setup` (imports, downloads), as written by the author.
5. **Managed cell** tagged `["setup", "remove-cell"]`. Its source is exactly `review_format.RUN_QUESTION_CELL` (section 5). normalize owns it. The website drops it (myst-nb's standard `remove-cell`); Colab shows it.
6. Questions, easy to hard.
7. `## Credits` heading and the credit line. A collapsed heading hides everything up to the next heading of the same or higher level, so without this heading the last Answer would swallow the credits.

### 2.2 The three building blocks

**Run block** (in the question text, any markdown cell before the Answer heading). The migration puts each in its own cell, keeping the old code cell's id:

~~~
```python run
x = 5
if x = 5:
    print('five')
```
~~~

**Answer heading** (exact source `#### Answer`; metadata written by normalize):

```json
{"cell_type": "markdown", "id": "2fe08d87",
 "metadata": {"id": "2fe08d87", "jp-MarkdownHeadingCollapsed": true},
 "source": ["#### Answer"]}
```

Notebook metadata (written by normalize; ids in page order):

```json
"metadata": {"colab": {"collapsed_sections": ["e37c4922", "61b70332", "..."]},
             "kernelspec": {"display_name": "Python 3 (ipykernel)", "language": "python", "name": "python3"},
             "language_info": {"name": "python"}}
```

**Answer code cell.** It is generated: one per run block, in order, at the end of the Answer. When there are 2+ run blocks, the magic line carries a label that the magic ignores:

```json
{"cell_type": "code", "execution_count": null, "id": "a60c5a59", "metadata": {}, "outputs": [],
 "source": ["%%run_question part a\n", "x = 5\n", "if x = 5:\n", "    print('five')"]}
```

### 2.3 Layout per question kind

Cells are listed top to bottom; "md" means markdown.

**What is displayed, single part** (e.g. ch05 Q1)
- md `### Question 1 (easy): what is displayed?` + "What does this code display?"
- md run block
- md `#### Answer` (collapsed)
- md ```` ```text ```` exact output, then the explanation
- code `%%run_question` + the same code (generated)

**Last-expression display** (ch02 Q4, ch03 Q9): same as above. The run cell shows `Out: 12`, and the new check B3 requires a ```text block `12` (ch02 Q4 needs this one-line fix).

**Errors / find the error, multi-part** (ch05 Q8, ch02 Q9/Q10/Q14)
- md heading + task
- md `**Part a**`, md run block, md `**Part b**`, md run block, ...
- md `#### Answer`
- md "**Part a:** ... ```text SyntaxError: ...```" and so on for each part
- code `%%run_question part a`, code `%%run_question part b`, ...

Parts with no error (ch02 Q9 a, e; ch04 Q14 c) look the same, so nothing hints which parts fail. No cell is tagged `raises-exception` any more.

**Wrong calls** (ch03 Q10, ch04 Q14/Q15, ch05 Q14, ch06 Q15)
- md heading + task
- code **definition cell** ("Run this cell to define `add_and_show`"). It stays a visible code cell and must display nothing (check B2).
- md "Two correct ways to call it:" with ```python + ```text examples
- md Part labels + run blocks
- md `#### Answer`, md explanation, code run cells

**Doctest** (ch07 Q14): one run block holding the defs and the `run_doctests(...)` call. The run cell prints the same 8-line report, with `File "__main__", line 9` unchanged (verified on both stacks).

**Turtle, what is drawn** (ch04 Q2, Q6, Q7; ch05 Q17)
- md run block with `make_turtle()`
- md `#### Answer`
- md explanation with `<img data-turtle src="data:...">`, which `review.sh images` draws from the question's single run block
- code run cell (the live drawing, visible only when the Answer is open)

**Write code** (34 questions): unchanged question text: header block, examples (```python + ```text or a picture), and the `# Your code here` cell. Then `#### Answer` and markdown with the ```python solutions. There are no run blocks, so no run cells; the same Answer form is used for all questions.

**Refactor / generalize / simplify** (ch03 Q12; ch04 Q11, 17, 18, 19; ch06 Q12): the given code stays a plain ```` ```python ```` block, because it is not marked `run`. No heuristic is needed, which removes the prototype's "write-code questions run nothing" special case.

### 2.4 Format rules (README-ready; enforced by `review_format.lint`)

- **F1.** A question runs from `### Question N (level): kind` to the next heading of level 1-3.
- **F2.** Each question has exactly one cell whose source is exactly `#### Answer`, after the question text.
- **F3. Headings.** A heading may only be the first line of a markdown cell. Allowed: `#`, `##`, `###`, and `####` only as the Answer heading. No `#####`/`######` and no setext (`===`/`---` underline) headings anywhere. The scan is fence-aware, so `# comment` lines inside code blocks are ignored. Why: Colab and JupyterLab end a collapsed section at the next heading of the same or higher level. Any other heading inside an Answer would end it early and show the rest. This fixes the verified gap M3.
- **F4.** The code the Answer runs is written only as ```` ```python run ```` blocks before the Answer heading. Answers never contain run blocks.
- **F5.** Code cells before the Answer heading: setup cells, definition cells (display nothing), and `# Your code here`. Code cells inside an Answer: only generated `%%run_question` cells, last in the Answer.
- **F6.** An Answer picture with no ```python block above it in its cell shows what the question's run block draws. This is allowed only when the question has exactly one run block; otherwise put a ```python block above the picture.
- **F7.** The page ends with a `## Credits` section.
- **F8.** Allowed tags: `setup`, `no-signature`, and `remove-cell` (only on the managed cell). `raises-exception` is no longer used on yr pages.
- **F9.** Never edit `%%run_question` cells. Edit the run block and run normalize, which prints a diff of every Answer cell it rewrites, so a hand edit is never lost silently.

## 3. How Answers collapse

| Where | Mechanism | Evidence |
|---|---|---|
| Colab | `metadata.colab.collapsed_sections` lists the Answer heading ids; each heading also has `metadata.id` equal to its top-level `id` | Format VERIFIED from real Colab-saved files: dm_control, eng-edu, gromacs, lambdamai Pandas_1 (nbformat 4.5, id == metadata.id == '36396f4c' in collapsed_sections). That opening from `/github/` honors it is strongly supported but NOT tested live. That Run all runs the hidden cells and keeps their outputs hidden is strongly supported but NOT tested live. |
| JupyterLab 4 / Notebook 7 | `jp-MarkdownHeadingCollapsed: true` on the heading cell | VERIFIED in headless JupyterLab 4.6.4: opens collapsed; Run All runs the hidden cells and they stay hidden. Shift+Enter walking into an Answer expands it (VERIFIED; a known cost). |
| Website | `prep_notebooks.answer_sections` folds heading + Answer markdown into one `:::{admonition} Answer` / `:class: dropdown` cell and drops run cells | VERIFIED in a mini build (section 1). |
| VS Code (and "Colab in VS Code/Cursor") | none: VS Code ignores both markers | Source-read; Answers and their outputs are visible there after Run all. Accepted limitation. |

## 4. The DRY mechanism

- **Single source.** Each question's code exists once, as a run block. Option A from the research, made explicit: the `run` marker replaces the prototype's guessing.
- **Derived content.** Four things are derived; authors never write them. All are produced by one function, `review_format.normalize(nb)`, exposed as `review_cells.py normalize NB...`:
  1. the Answer code cells: `render_run_cell(code, label)` gives `'%%run_question' + (f' part {label}' if label else '') + '\n' + code`, with label letters a, b, c... when there are 2+ blocks;
  2. the collapse metadata: Answer heading `metadata.id` and `jp-MarkdownHeadingCollapsed`, notebook `colab.collapsed_sections`, and removal of `metadata.id` / `jp-...` from every other cell (Colab adds `metadata.id` to all cells when it saves);
  3. the managed setup cell;
  4. clean state: no outputs, `execution_count: null`, a metadata whitelist (cells: `tags`, plus `id`/`jp-...` on Answer headings; notebook: `kernelspec`, `language_info`, `colab.collapsed_sections`).
- **Enforcement.** `review_format.lint(nb)` runs `normalize(deepcopy(nb))`. If anything would change, it reports "derived content out of date: run `python3 yr/tools/review_cells.py normalize NB`". This is the strongest possible DRY check, with no parsing of run cells anywhere: the tools compare against what the generator would write.
- **No escaping.** The cell magic takes the code verbatim, so there are no quoting rules or edge cases (backslashes, triple quotes, doctests all verified).
- **Pictures are derived too.** The new `turtle_images.py --check` re-renders every picture and fails if a stored PNG differs. Redraws are byte-identical (verified by earlier workers), so this is reliable. `review.sh check` runs it.
- **Switching mechanisms later.** `render_run_cell` and `RUN_QUESTION_CELL` are the only places that know how Answer cells run. Changing the mechanism (e.g. a fallback after the Colab test) means editing one function, then running normalize on all pages.

## 5. Running the question code: `%%run_question` instead of `run_code`

### Managed cell source (`review_format.RUN_QUESTION_CELL`)

```python
def run_question(line, cell):
    """The %%run_question cell magic: run the code under it like a normal cell, show its output.

    Each Answer ends with a %%run_question cell that runs the question's code, so you can see
    its real output. Unlike a normal cell, an error is shown without stopping Runtime > Run all.
    """
    result = get_ipython().run_cell(cell)
    if isinstance(result.error_in_exec, KeyboardInterrupt):
        raise KeyboardInterrupt  # the Stop button still stops Run all

try:
    get_ipython().register_magic_function(run_question, 'cell')
except NameError:  # plain Python (e.g. the review tools): no cell magics
    pass
```

### Why not `run_code("""...""")` with catch + `showtraceback()`

The catch + `showtraceback()` form does keep the reply status "ok" (verified by three workers). Its problems:

- **Messy tracebacks.** On IPython 8+ it shows a `run_code` frame and "Could not get source"; `tb_offset` does not remove them. On 7.34 it shows no source lines.
- **Shifted line numbers.** The newline after the opening quotes shifts every line number by +1.
- **No last-expression display.** ch02 Q4 and ch03 Q9 lose their output.
- **Generated code inside a string literal** needs raw strings and a quote-style switch, and still breaks doctests on IPython 9.

Nested `run_cell` inside a function fixes the traceback look, but still embeds the code in a string. The cell magic gets the raw body, so it has none of these problems.

### How errors look (VERIFIED)

On Colab's IPython 7.34:

```
  File "/tmp/ipykernel_20425/2636000202.py", line 2
    if x = 5:
       ^
SyntaxError: invalid syntax. Maybe you meant '==' or ':=' instead of '='?
```

```
ZeroDivisionError                         Traceback (most recent call last)
/tmp/ipykernel_20425/1862101479.py in <cell line: 0>()
      1 print('start')
----> 2 print(1/0)

ZeroDivisionError: division by zero
```

On IPython 9 it is the usual `Cell In[N], line 2` form. N is one higher than the cell's prompt, because the nested run increments the counter (cosmetic). Answers keep comparing only `Ename: message` lines, never headers.

### Behaviour details

- **Reply status (VERIFIED).** Every `%%run_question` cell returns status "ok", including queued requests. This is what ipykernel 6.17.1's queue abort keys on.
- **Unknown: Colab's frontend.** Whether Colab's *frontend* also stops Run all on an error-type output is unknown (Colab test C2).
- **Stop button (VERIFIED).** It still halts Run all; the KeyboardInterrupt traceback shows twice.
- **Running too early (VERIFIED).** A run cell executed before the setup cells gives `UsageError: Cell magic %%run_question not found` (status error), just as `run_code` gives a NameError today.

### Fallbacks, if the Colab test says so

- **(a) Colab stops on error outputs.** Inside the magic, temporarily set `shell._showtraceback = lambda et, ev, stb: print(shell.InteractiveTB.stb2text(stb), file=sys.stderr)` around `run_cell`. The skeptic verified this gives normal-looking tracebacks with status ok on both stacks. At the same time `check_review.errors_shown(cell)` must parse the last `Ename: message` line of the ANSI-stripped stderr of run cells. Otherwise every error check goes blind; mutation M15 showed exactly that.
- **(b) Colab blocks or warns on custom magics.** Switch `render_run_cell` to a function call with the opening quote on its own line, `run_question(\nr'''\n...\n''')`. Unverified: on IPython 9 this relies on the prompt stripper's heuristic. Then re-run the full check on both stacks.

## 6. Tool changes

### 6.1 New `yr/tools/review_format.py` (stdlib only; works on plain JSON dicts and nbformat nodes)

- **Constants:** `ANSWER_HEADING = '#### Answer'`, `RUN_FENCE = re.compile(r'```python run\n(.*?)```', re.S)`, `RUN_MAGIC = '%%run_question'`, `RUN_QUESTION_CELL`, `PLACEHOLDER = '# Your code here'`. Also `TEXT_BLOCK`, `PY_BLOCK` (```` ```python\n ```` exactly, so run blocks never count as answer code), `SIGNATURE`, `IMG`, `HAZARD`, and `EXAMPLE`, tightened to `r'```python\n(?:(?!```).)*?```\s*(```text\n|<img\b[^>]*\bdata-turtle)'` so it cannot stretch across blocks (fixes F23).
- **Helpers:**
  - `source(cell)`;
  - `headings(md)`: fence-aware list of (line_no, level, kind ATX/setext);
  - `heading_level(cell)`: first-line heading;
  - `run_blocks(md)`;
  - `render_run_cell(code, label)`.
- **`parse_page(cells)`** returns `Page(setup_cells, managed_cell, questions, credits_index)`. Each `Question` has: `title`, `cells`, `question_cells`, `answer_heading`, `answer_md`, `run_cells`, `run_blocks`, `definition_cells`, `placeholders`.
- **`normalize(nb)`** applies section 4 and returns a list of human-readable changes, including a unified diff for any run cell whose body changed. It reuses existing run-cell ids by position and inserts the managed cell right after the last author setup cell.
- **`lint(nb)`** returns the static problems F1-F9 plus "normalize would change ...".

### 6.2 `yr/tools/review_cells.py`

- **Spec kinds:**
  - `%%% markdown`;
  - `%%% run` (new): the body is plain code and becomes a markdown cell with a ```` ```python run ```` block;
  - `%%% code [tags]`: definition cells only, which must display nothing;
  - `%%% placeholder`;
  - `%%% answer`: now emits the `#### Answer` heading cell plus one markdown cell with the body.
- **`add` and `renumber`** call `normalize` at the end, so new questions get their run cells and collapse metadata automatically.
- **New `normalize NB...`**: idempotent; writes only when something changed; prints the change list.
- **`new` skeleton:** standard intro paragraph, page setup cell, managed cell, `## Credits` + credit line, `metadata.colab.collapsed_sections: []`. `fresh_id` is unchanged (8 hex); normalize mirrors ids into `metadata.id` on Answer headings only.
- **Docstring** updated with a full spec example (section 7).

### 6.3 `yr/tools/check_review.py` (runtime checks; static ones come from `review_format.lint`)

Execution changes:

- Run once with `allow_errors=True`, recording each cell's `execute_reply['content']['status']` through nbclient's `on_cell_executed` hook (available in nbclient 0.11.0, verified). This gives complete outputs for every check plus an exact model of Colab's kernel queue.
- Drop the tag logic.
- Add a `--python`/env override in `review.sh` (`REVIEW_PYTHON=...`) so the check can also run under the Colab-like IPython 7.34 venv.

Mapping old checks to new ones (nothing is weakened):

| Today | New |
|---|---|
| a cell may raise only if tagged `raises-exception` | **B1** no cell has reply status "error" (Run all reaches the end, Colab semantics). **B6** error outputs only in run cells. |
| "tagged but raised nothing" | **B5** every error-looking last line (`^[A-Z]\w*(Error\|Exception\|Interrupt\|Exit)\b`) in an Answer's ```text blocks names an exception that some run cell of that question raised. Fixes M1; holds on all six pages (verified). |
| stdout must equal one ```text block | **B3** a run cell's shown text (stdout + `execute_result` text/plain, in output order) must equal one ```text block. Closes the execute_result gap F7/M2; needs the ch02 Q4 fix. |
| error line must appear in the Answer | **B4** unchanged (substring of a ```text block; `error_line` unchanged). |
| syntax error must be inside `run_code` | Obsolete by construction: question code is never in a visible cell. **B2** plus F5 keep visible cells harmless. |
| answer ```python blocks run as standalone .py | **B8** unchanged (only ```` ```python\n ```` blocks in Answer markdown). |
| write-code: header + 2 examples | lint F-rules plus the tightened `EXAMPLE`; same semantics. |
| wrong calls: 2 correct calls | **B9**: any run cell raised AND the question defines a function (in a definition cell or run block) gives at least 2 examples. |
| empty pictures, (c)/(r) symbols | lint, unchanged |
| "no Answer cell" | lint F2 |
| new | **A1** normalize is a no-op (DRY, collapse metadata, managed cell). **B2** no output in any cell outside an Answer, except stdout of setup cells ("Downloaded ..."). **B7** a run cell that draws (display_data with an svg) needs a data-turtle picture in its Answer, and `turtle_images --check` reports the pictures up to date. lint F3/F7. |

### 6.4 `yr/tools/turtle_images.py`

- Use `parse_page`. The namespace per question is:
  1. setup cells (the managed cell is harmless thanks to its NameError guard);
  2. the Answer's ```python blocks;
  3. then, in page order, definition cells *and run blocks* as they are reached (mirrors today, when these were code cells; errors are swallowed as today).
- Picture code: the nearest ```python block above the img in the same cell. Otherwise the question's single run block (F6); if there are 0 or 2+ run blocks, report an error instead of guessing.
- Never execute `%%run_question` cells.
- **New `--check` mode:** render, compare with the stored data URIs, write nothing, exit 1 on any difference. `review.sh check` runs it.

### 6.5 `jb/prep_notebooks.py`

- `process_review`:
  - drop `# Your code here` cells;
  - `raw_pictures`;
  - `details_to_dropdown` (now only the concept lists);
  - new `answer_sections`, importing `review_format` via `sys.path` from `../yr/tools`. It folds the heading plus Answer markdown into one dropdown cell, keeps the heading's id, and drops run cells;
  - `process_cell`.
- Leave ```` ```python run ```` as is (renders fine; verified).
- **Guard:** after processing a yr page, `sys.exit` if any cell is still `#### Answer` or a code cell starts with `%%run_question`. A format drift then fails the deploy instead of publishing open answers.

### 6.6 `.claude/skills/check-notebooks/check_notebooks.py`

- Add `%%run_question` to `KNOWN_MAGICS`.
- For `yr/*.ipynb`, call `review_format.lint(nb)` (static, fast, stdlib). This puts the DRY, collapse, heading and tag invariants into the general lint.
- Today it passes: `OK: 48 notebook(s)`, verified.

### 6.7 Other files

- **`run_notebooks.sh`:** treat a cell whose first line starts with `%%run_question` like a `%%expect`d cell (its error outputs are expected). Update the header comment, which mentions `raises-exception` for yr pages.
- **`review.sh`** (and optionally `build_book.sh`, `run_notebooks.sh`): fall back when `git rev-parse` fails, so the tools work in a copy without `.git`. This trap broke earlier workers:
  `ROOT="$(git -C "$(dirname "$0")" rev-parse --show-toplevel 2>/dev/null || (cd "$(dirname "$0")/../.." && pwd))"`.
- **`.github/workflows/deploy-book.yml`:** add a step `python3 .claude/skills/check-notebooks/check_notebooks.py` before prep (decision D10).

## 7. Docs

**`yr/README.md`.** Rewrite:
- "Layout of a page" items 3-4 (setup + managed cell, Answer sections, `## Credits`);
- "Answers";
- "Cell conventions": replace the `<details>` Answer, `raises-exception` and `run_code` sections with F1-F9, the three building blocks, why (Run all, nothing visible after it, Colab squiggles) and the metadata JSON;
- "Turtle pictures" (F6);
- "Tools": add `normalize`, `images --check` through `check`;
- the `review.sh check` list (the B/lint list);
- "How the build handles yr/" (`answer_sections`, the guard).

Add a short section "Editing a page in Colab or Jupyter": saving there adds outputs, `metadata.id` on every cell, and possibly a changed collapse layout. Download the file and run `normalize`. Colab has an explicit View > "Save collapsed section layout" command, so a Colab save may change the layout. Also add one line on VS Code (Answers not collapsed there).

**`.claude/skills/yr-review-questions/SKILL.md`.**
- Rules: question code as `%%% run` blocks; never edit `%%run_question` cells; no `raises-exception`; definition cells display nothing.
- New spec example: a multi-part error question with `%%% run`.
- Steps: add (normalize runs automatically) → images → `review.sh check`. To revise, edit the run block, then `normalize` → images → check.

**`.claude/skills/yr-review-page/SKILL.md`.** Skeleton description (managed cell, Credits, intro paragraph); verify steps include `check_notebooks.py`.

**`.claude/skills/notebook-conventions/SKILL.md` L86:** replace "`<details>` answer format ... `raises-exception`" with a pointer to the README's Answer sections.

## 8. Converting the six pages

**One-time script.** It stays in the scratchpad, not the repo (decision D12). It is based on `plan-maint/conv3.py`, which already produced this layout and passed the comparison on both stacks. Per page it:

1. turns each question code cell that is not definition-only (`ast`: only def/class/import/assign) and not `# Your code here` into a markdown run-block cell **with the same id**, unwrapping `run_code("""...""")` and dropping `raises-exception`;
2. turns the `<details>` Answer into a new `#### Answer` heading cell plus an explanation cell **with the old id**;
3. deletes `def run_code` from setup cells (ch02-ch05, ch07);
4. prefixes the credit cell with `## Credits`;
5. calls `review_format.normalize`, which adds the run cells, metadata and managed cell.

**Hand edits (Claude, reviewed in the diff).** Stale wording found by the verifier:
- ch02 Q9 "For each cell...", ch02 Q14 "Each cell has an error...";
- ch03 Q10 and ch04 Q14 "For each of the next three cells";
- ch04 Q7 "...and this cell"; ch02 Q4 and ch03 Q9 "this cell" → "this code";
- ch07 Q15 "then run it"; "then run it to check" → "then open the Answer to check";
- each page's `run_code` intro → the standard paragraph (section 2.1);
- ch02 Q4: add ```` ```text\n12\n``` ```` to its Answer (B3).

Also grep the question text for `\bcells?\b|run (it|this)` and review each hit.

**Then:** `normalize` (no-op the second time), `review.sh images --check` (expect identical pictures), `review.sh check` on all six.

## 9. Verification here, before asking the professor

1. `review.sh check yr/chap0{2..7}_review.ipynb`: OK on all six (IPython 9.17 / Python 3.13). Also run `check_review.py` with the Colab-like venv (`scratchpad/ultra/proto/venv-colablike`, IPython 7.34 / ipykernel 6.17.1 / Python 3.12): OK.
2. Equivalence: `plan-maint/exp.py` with the original and converted page, on both stacks. Expect 0 output differences on all 103 questions, 0 error statuses, 0 visible outputs.
3. Idempotency: `normalize` twice gives no diff. `turtle_images --check` reports 0 differences on ch04 (22) and ch05 (1).
4. `python3 .claude/skills/check-notebooks/check_notebooks.py`: OK.
5. Mutation self-test, committed as `yr/tools/selftest_review.py` and run via `review.sh selftest`. It applies each mutation to a copy of chap05/chap04, asserts that check fails with the expected message, and asserts that the unmutated copy passes. The mutations:
   - M1 run block edited so it no longer raises, Answer still says SyntaxError (B5);
   - M2 code changed in both places, Answer not (B3);
   - M3 `#### Note` inside an Answer (F3);
   - M4 run block edited, run cell not regenerated (A1);
   - M5 collapse metadata removed (A1);
   - M6 run cell deleted (A1);
   - M7 definition cell prints (B2);
   - M8 answer block not standalone (B8);
   - M9 wrong expected stdout (B3);
   - M10 error text missing (B4);
   - M11 `## Credits` removed (F7);
   - M12 wrong-call question with one correct call (B9);
   - M13 write-code question with one example (lint);
   - M14 run block draws something else, picture not redrawn (B7 via `--check`);
   - M15 old-style raising code cell before the Answer (B1/B6/B2);
   - M16 setext heading in an Answer (F3);
   - M17 managed cell edited (A1);
   - M18 `raises-exception` tag present (F8);
   - M19 Answer picture without a block in a two-run-block question (F6).
   
   Future sessions must run it whenever `check_review.py` or `review_format.py` changes ("never weaken checks", made testable).
6. Website: `build_book.sh`, no new warnings versus `known_warnings.txt`. A script over `jb/_build/html/yr/chap0*_review.html` asserts:
   - Answer dropdowns 17/16/19/17/17/17, none open;
   - 0 h4; 0 contents entries named "Answer";
   - no `run_question` text (the managed cell is removed);
   - dropdown text identical to today's site except ch02 Q4.
   
   Look at screenshots of ch04 Q2, ch05 Q8, ch07 Q14. For headless Chromium, pass `executable_path=/opt/pw-browsers/chromium-1194/chrome-linux/chrome`.
7. Optional: headless JupyterLab 4.6.4 run of the converted chap05 (prototype scripts `lab_test.py`), checking it opens collapsed and Run All keeps outputs hidden.
8. Pyright (`scratchpad/pr/node_modules/.bin/pyright`) on every visible code cell together with the cells above it: no new diagnostics except the known jupyturtle import note.
9. `git diff --stat`, and a script counting preserved cell ids (expect about 187 converted cells keeping their ids, plus all untouched cells).

## 10. Colab test checklist for the professor

Push the topic branch, not v3. Open
`https://colab.research.google.com/github/y-rosenthal/yrThinkPython/blob/yr-answer-sections/yr/chap05_review.ipynb`.
Use a fresh session (Runtime > Disconnect and delete runtime first). Note yes/no for each step.

1. **C1 Collapsed on open.** Every "Answer" is collapsed and shows a "N cells hidden" row; questions and setup cells are visible.
2. **C2 Run all reaches the end.** Runtime > Run all; wait until no cell is running. Open Question 17's Answer: its drawing and an execution count are there. Did Run all stop anywhere (a cell left with a pending/aborted marker)?
3. **C3 Nothing given away.** Scroll the whole page without clicking anything. Only question text and the setup output ("Downloaded jupyturtle.py") are visible. No Answer expanded by itself, the page did not jump into an Answer, and no red error marks on Answer headings or "cells hidden" rows reveal which Answers contain errors.
4. **C4 Live answers look right.** Open Question 8: three normal-looking SyntaxError / SyntaxError / IndentationError tracebacks under three `%%run_question` cells. Open Question 14 (RecursionError, short on Colab). Any warning or notice about the `%%run_question` magic?
5. **C5** Runtime > Restart session and run all: same results as C2-C3.
6. **C6 Keyboard stepping.** Restart. Click the setup cell and press Shift+Enter repeatedly through Questions 1-3: does an Answer expand when you reach it? Then select Question 1's heading and press the Down arrow repeatedly: same question.
7. **C7 Stop.** Run all, and press the Stop button while Question 17's drawing is running: does Run all stop?
8. **C8 Rendering.** The question code blocks look like normal highlighted Python, and the word "run" is not shown.
9. **C9 Squiggles.** With Tools > Settings > Editor > Code diagnostics at its default, and again with "Syntax and type checking": no underlines in the visible code cells (setup cells, the definition cell in Question 14).
10. **C10 What Colab saves.** File > Save a copy in Drive, open one Answer, save, then File > Download .ipynb and send us the file. This shows which metadata Colab writes; normalize must cope with it.
11. **C11** Is the list of "Answer" entries in Colab's table-of-contents sidebar acceptable?
12. **C12, only if C2 failed.** Open `scratch/colab_probe.ipynb` on the same branch (never merged). Cells:
    1. magic setup;
    2. `%%run_question\n1/0`;
    3. `print('REACHED 3')`;
    4. a stderr-variant magic cell `%%run_question_stderr\n1/0`;
    5. `print('REACHED 5')`;
    6. a plain `1/0` (control, expected to stop);
    7. `print('REACHED 7')`, which should not run.
    
    Report which REACHED lines appear.

## 11. Rollout order

1. **Approve.** The professor reads this plan and answers the decisions in section 12 (defaults are the recommendations).
2. **Branch.** Create `yr-answer-sections` from `v3` (which already contains b389c80).
3. **Format module.** Implement `review_format.py` first, then `review_cells.py` (spec kinds, normalize, skeleton).
4. **Convert.** Run the migration on all six pages, normalize, and make the hand edits (section 8).
5. **Tools.** Update `check_review.py`, `turtle_images.py` (`--check`), `prep_notebooks.py` (`answer_sections` + guard), `check_notebooks.py`, `run_notebooks.sh`, `review.sh` (ROOT fallback, `selftest`, `REVIEW_PYTHON`), `selftest_review.py`.
6. **Verify.** Run all of section 9.
7. **Commit atomically.** One commit holds tools + six pages: old prep with new pages would publish every answer openly, and old turtle_images would silently rewrite 19 ch04 pictures (both verified). A second commit holds the README and skills. Add the `scratch/colab_probe.ipynb` only on a throwaway branch.
8. **Colab test.** Push the topic branch and have the professor run section 10.
9. **Decide.**
   - C1-C4 pass: merge to v3 and publish (yrpublish skill), then check the live site and one Colab link on v3.
   - C2 fails because of error outputs: fallback (a) (section 5, magic + check change, re-verify), then re-test C2.
   - The magic is blocked or warned about: fallback (b).
   - C1 fails (Answers not collapsed on open): stop and rethink, because goal 2 is then unmet in Colab. Try metadata variants first (ids only in `metadata.id`; Colab-style 12-character ids).
   - C6 shows expansion: decision D11.
10. **Later.** Optionally add the `check_notebooks.py` step to `deploy-book.yml` (D10) in the same PR or right after.

## 12. Open decisions for the professor

| # | Decision | Recommendation |
|---|---|---|
| D1 | How Answer cells run the code: `%%run_question` cell magic vs `run_code("""...""")` string | Magic: verbatim code, normal tracebacks, last expression shown, doctests intact on IPython 9; one place to change if Colab objects |
| D2 | Marker for "the Answer runs this": ```` ```python run ```` fence vs a cell tag vs guessing | Fence: visible in the text, survives any editor, renders normally (verified on the site; Colab check C8) |
| D3 | Run cells after the explanation or before it | After: the explanation is the answer; the live output confirms it |
| D4 | Part labels on run cells (`%%run_question part a`) | Yes, generated automatically |
| D5 | Same Answer form for write-code questions (heading section) or keep `<details>` there | Same form: one format, one set of tools (costs the Shift+Enter reveal for those too, if Colab behaves like JupyterLab) |
| D6 | Credits: `## Credits` heading at the end, or move the credit line into the title cell | `## Credits` (one extra page-contents entry) |
| D7 | `run_question` definition: separate managed setup cell hidden on the site (`remove-cell`) or inside the page's setup cell | Separate cell: fully tool-owned and not shown on the website; students run two setup cells (or Run all) |
| D8 | Website: drop Answer run cells, or show them as code blocks | Drop: the question code is shown just above; showing it again is a duplicate |
| D9 | Add the ```text `12` block to ch02 Q4 so the new last-expression check passes | Yes (it is what the README already requires) |
| D10 | Run `check_notebooks.py` (including the static review lint) in `deploy-book.yml` | Yes: catches out-of-date derived content before publishing; it passes today |
| D11 | If Shift+Enter or Down arrow expands Answers in Colab | Accept and add one sentence to the intro ("step with Ctrl+Enter or use Run all"); no layout fits Colab's section model better |
| D12 | Commit the migration script? | No, unless other branches still hold old-format review pages |
| D13 | VS Code users (incl. "Colab in VS Code") see Answers expanded | Accept; document in the README |

## 13. About the errors in research workers 3 and 4

I cannot see those workers' transcripts, so the exact cause is unconfirmed. Several verified traps in this container would make a worker fail:
- `rsync` is not installed (use `tar` or `cp -a`);
- `review.sh`, `build_book.sh` and `run_notebooks.sh` find the repo root with `git rev-parse`, which fails in a copied tree without `.git` (fixed by the ROOT fallback in 6.7, or `git init` the copy);
- the Playwright 1.63 in `jupyter-facts/venv-lab` looks for browser build 1243, while only 1194 exists (pass `executable_path=/opt/pw-browsers/chromium-1194/chrome-linux/chrome`);
- `jupyter lab` as root needs `--allow-root`, and `window.jupyterapp` needs `--LabApp.expose_app_in_browser=True`;
- `pkill -f` or `pgrep -f | kill` with a pattern that also appears in the Bash command kills the calling shell (exit 144);
- `gh`/curl GitHub API calls for repositories not attached to the session return 403, while WebFetch to github.com works.

Continuing does not require re-running them: the four research reports plus three skeptic passes cover their questions, and this plan's experiments filled the remaining gaps.


## assumptions_needing_colab_test

- C1: Colab opens a notebook from colab.research.google.com/github/... with the headings listed in metadata.colab.collapsed_sections collapsed. Here the ids are nbformat 4.5 top-level ids copied into each heading's metadata.id. The format is verified from Colab-saved files; that Colab honors it on open is not tested live.
- C2a: Runtime > Run all executes the cells inside collapsed sections and does not expand them or scroll into them.
- C2b: Colab's frontend does not stop Run all on a cell that sends an iopub 'error' output while its execute_reply status is 'ok'. The kernel side is verified on Colab's pinned ipykernel 6.17.1 and IPython 7.34, queued requests included; the frontend is unknown. Colab has server_execution_queue and execution_status_propagation flags.
- C3: A collapsed section hides its cells' outputs. No error badge or status mark on an Answer heading or its 'N cells hidden' row reveals which Answers contain errors.
- C4: Colab runs a cell magic registered with get_ipython().register_magic_function, here %%run_question, without an 'unsupported magic' warning or block. Its nested run_cell shows errors like a normal cell, including Colab's ModuleNotFoundError note.
- C6: Stepping with Shift+Enter or the Down arrow into a collapsed '#### Answer' section does not expand it. JupyterLab does expand it (verified), and Colab issue #171 (2018) reports that Down-arrow expands sections.
- C7: Pressing Stop during a %%run_question cell halts Run all. The magic re-raises KeyboardInterrupt, so the reply status is 'error' (verified on the kernel side).
- C8: A markdown block fenced ```python run renders in Colab as ordinary highlighted Python, without showing the word 'run'.
- C9: The visible code cells left on the page (setup cells and definition cells) show no editor underlines that give an answer away, both with the default Code diagnostics setting and with 'Syntax and type checking'.
- C10: After a professor edits and saves in Colab, normalize can repair what Colab wrote: outputs, metadata.id on every cell, and a collapsed_sections list that may come from the current UI layout or the 'Save collapsed section layout' command. Whether Colab also keeps cell tags and the jp-MarkdownHeadingCollapsed metadata is unknown.
- The 2026-01-20 Colab UI redesign may have changed the labels the checklist refers to: the 'N cells hidden' row, menu names, and the location of the settings.

## dry_choice

Option A, made explicit. Each question's code is written once, as a ```python run block in the question's markdown. `review_cells.py normalize` generates every derived part:
- the Answer's `%%run_question` code cells, which contain the question's code verbatim;
- the collapse metadata;
- the shared `run_question` setup cell.

`review.sh check` and `check_notebooks.py` fail unless normalize would change nothing. Tested on all six pages under IPython 9.17 and 7.34: 0 output differences across the 103 questions. Options B and C were rejected. Under IPython 9 a string literal corrupts doctests, and string forms need escaping. The %%question magic gets squiggles from Pyright.

