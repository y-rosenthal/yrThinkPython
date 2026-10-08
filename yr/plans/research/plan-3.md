# plan:3

## Review pages that survive Colab's Run all: question code as text, live Answers in collapsed sections, tested in a risk-first, staged rollout

# Plan: Run-all-safe review pages, answers hidden until clicked (risk-first)

## 0. Why the 3rd and 4th research workers failed, and the fix

I found the answer in the session's own logs: `~/.claude/projects/-home-user-yrThinkPython/6571a165-…/subagents/workflows/wf_f52e2176-172/journal.jsonl` plus the agent transcripts.

**What happened**
- Only two agents run at a time, because the container has 4 CPUs. At 17:20 workers 1 and 2 (colab, jupyter) had already finished. Workers 3 and 4 were still running:
  - `research:repo`, agent `af37ec9a…`
  - `research:prototype`, agent `a1fdadad…`
- At **17:20:58.398Z** both transcripts end with `[Request interrupted by user]`. Neither had crashed: the repo worker was comparing error texts between Python 3.12 and 3.13, and the prototype worker was reading JupyterLab source.
- In the same second the main session logged `[Request interrupted by user for tool use]`. The tool call in progress was rejected ("The user doesn't want to proceed with this tool use"). That call was a helper Claude had started at 17:19:56 to answer your `/workflows` question.
- This came 5 seconds after your message "Is Claude Code running on my laptop faster…" was queued, at 17:20:53.
- The interrupt reached every workflow agent running at that moment, which were exactly workers 3 and 4.
- The log records it only as a user interrupt. It can't tell whether you clicked Stop or whether the web app interrupts the current step when you send a message mid-step.

**What did not cause it**
- The workers' own guesses were missing `rsync`, `git rev-parse` failing in copies, and the Playwright browser version. Those are real traps in this container, but none of them caused this failure.

**The fix, already done**
- At 17:24:00 the orchestrator resumed the same run (`resumeFromRunId: wf_f52e2176-172`).
- Workers 1 and 2 came back from cache. Workers 3 and 4 re-ran from scratch as `a20fcc3e…` and `a24699395…` and both finished.
- Their results (the repo map and the prototype) are part of this plan, and the run is now in its Design phase.

**Avoiding it next time:** while a workflow runs, don't click Stop or reject a pending step. If the web app interrupts on send, wait until Claude finishes the current step before typing.

---

## 1. Decision in one paragraph

- **The question:** a markdown cell (prompt) plus one markdown cell per piece of code, tagged `question-code`, holding a ```python block. Markdown is never underlined by Colab's editor.
- **The Answer:** a `#### Answer` heading saved as collapsed. Under it come the explanation (expected output in ```text blocks, turtle PNGs) and, last, one generated **run cell** per question-code cell. A run cell is either:
  - the code itself, or
  - `run_code(r"""…""")` when the code raises.
- **`run_code`:** it calls `get_ipython().run_cell(code)`. The error is shown like a normal cell's error, but the cell's own status is "ok", so Run all goes on.
- **Collapsing:** Colab collapses the Answers through `metadata.colab.collapsed_sections`, and JupyterLab through `jp-MarkdownHeadingCollapsed`. The website folds each Answer section into the same dropdown it uses today.
- **One copy of the code:** `review.sh sync` generates the run cells from the question-code cells, and `review.sh check` fails if they differ by a single byte.
- **Order of work:** nothing is rolled out until a 20-minute Colab smoke test (section 10) settles the unknowns. That test also exercises both fallbacks, so one Colab session decides between the main design and the fallbacks.

## 2. What is verified here vs. what only Colab can answer

| Claim | Status | Evidence |
|---|---|---|
| Colab stores collapsed headings as `metadata.colab.collapsed_sections` (list of heading cell ids) | VERIFIED (file format) | Real Colab-saved files: dm_control, eng-edu, gromacs, lambdamai Pandas_1 (nbformat 4.5, `id == metadata.id == "36396f4c"`) |
| Colab opens a GitHub notebook with those sections collapsed | BELIEVED (strong) | gromacs README /github/ links + "click ↳ cells hidden"; issue #438; 'Save collapsed section layout' menu. Not observed live |
| Colab's Run all runs cells in collapsed sections and keeps them hidden | BELIEVED | gromacs "Runtime → Run all" with collapsed code sections; #2990 |
| Colab's Run all stops at an uncaught error | VERIFIED (kernel side) + your own observation | Colab pins ipykernel 6.17.1; queued-request abort reproduced on that stack |
| A cell whose error is caught (reply "ok", error output shown) lets Run all continue | VERIFIED in kernel, nbclient, JupyterLab 4.6.4, Notebook 7. **UNKNOWN in Colab's frontend** | Colab flags `server_execution_queue`, `execution_status_propagation` |
| Traceback printed on stderr (no error output at all) lets Run all continue | VERIFIED in kernel/nbclient. Colab: BELIEVED | This plan's smoke run, both stacks |
| Shift+Enter into a collapsed heading expands it | VERIFIED in JupyterLab. Colab UNKNOWN (Down-arrow did in 2018, #171) | Two independent browser tests |
| Code in markdown or inside a string literal is never underlined | VERIFIED (Pyright 1.1.414) | Colab's checker is Pyright (VM `ps` dumps) |
| Website: merging each Answer section into one dropdown leaves no 'Answer' TOC entries and no new warnings | VERIFIED | Prototype build plus an independent skeptic build |
| **New (this plan):** the smoke notebooks run to END under a Colab-like Run all (stop at first error, tags ignored), with variants A and B and fallback C, on IPython 9.17/ipykernel 7.4 and on 7.34/6.17.1 | VERIFIED | `scratchpad/ultra/plan-risk/logs_runall_ipy{7,9}.txt` |
| **New:** Stop during a `run_code` cell, with cells queued like Run all: that cell → "error", next cell → "aborted" (so Stop still halts Run all) | VERIFIED (kernel side, both stacks) | `logs_stop_ipy{7,9}.txt` |
| **New:** fallback C (`run_hidden`) produces exactly one `display_data` holding stdout, the final turtle SVG, the traceback text and the last-expression value | VERIFIED (both stacks) | `showhidden.py` output |
| **New:** on IPython 9.17, wrapping ch07 Q14 in `run_code(r'''…''')` silently drops the doctest report. IPython 9 strips `>>> ` prompt lines from a cell's source even inside a string literal opened on line 1. IPython 7.34 is unaffected | VERIFIED | `logs_uniform_ipy9.txt` ("ch07q14 DIFFERENT"), `logs_doctest_strip_ipy{7,9}.txt` |
| **New:** a docstring inside `run_code("""…""")` is a SyntaxError, so the generator must choose the quote style | VERIFIED | `uniform.py` first run |
| **New:** plain cell vs `run_code` gives identical output for last-expression `12`, the function repr and turtle drawings, on both stacks | VERIFIED | `logs_uniform_*` |

## 3. Final page layout

**Page skeleton**
- Title cell (unchanged).
- `## Concepts covered` (unchanged).
- `## Questions`, with its intro.
- A **Colab-only help cell tagged `remove-cell`**. myst-nb drops markdown cells with that tag, so the website never shows Colab instructions. Verified by the jupyter worker; re-check in the Stage 2 build.
- The setup code cell (`setup` tag), which defines `run_code` **on every page, including ch06**.
- The questions.
- `## Credits` heading on the existing credit cell (same id). Without it, the last Answer would hide the credits.

**Cells of a question, in order**
```
[md]               ### Question N (level): <kind>      prompt, "By the way" remarks, example pairs (python+text / python+img)
[code, optional]   definition cell ("Run this cell to define X"); must print nothing
[md, question-code] one per part: optional "**Part a**" line, then exactly one ```python block
[md]               #### Answer                          (the cell holds nothing else)
[md]               explanation: ```text expected output, <img data-turtle>, approaches   (no headings of any level)
[code, answer-run] one per question-code cell, same order, generated by sync
```

**Metadata**

Notebook:
```json
"metadata": {"colab": {"collapsed_sections": ["e37c4922", "61b70332", "…one per Answer heading…"]},
             "kernelspec": {"display_name": "Python 3 (ipykernel)", "language": "python", "name": "python3"},
             "language_info": {"name": "python"}}
```

Answer heading:
```json
{"cell_type": "markdown", "id": "e37c4922",
 "metadata": {"id": "e37c4922", "jp-MarkdownHeadingCollapsed": true}, "source": ["#### Answer"]}
```

Question-code cell:
```json
{"cell_type": "markdown", "id": "5a1c09e2", "metadata": {"tags": ["question-code"]},
 "source": ["**Part a**\n", "\n", "```python\n", "x = 5\n", "if x = 5:\n", "    print('five')\n", "```"]}
```

Run cell:
```json
{"cell_type": "code", "id": "<old question code cell id>", "execution_count": null, "outputs": [],
 "metadata": {"tags": ["answer-run"]},
 "source": ["# Part a\n", "run_code(r\"\"\"\n", "x = 5\n", "if x = 5:\n", "    print('five')\n", "\"\"\")"]}
```

**Per question kind**

| Kind | Question side | Answer section |
|---|---|---|
| What is displayed (one block) | 1 question-code cell | text block + explanation; plain run cell |
| Last expression shown (ch02 Q4 `12`, ch03 Q9 function repr) | same | plain run cell; the check now verifies `execute_result` |
| Answer is an error (syntax, NameError, runtime, RecursionError, ModuleNotFoundError) | 1 question-code cell | text block with `Ename: message`; run cell `run_code(r"""…""")` |
| Multi-part (7 questions: ch02 Q9/Q10/Q14, ch03 Q10, ch04 Q14/Q15, ch05 Q8) | one question-code cell per part, each starting `**Part x**` | explanation with `**Part x:**` paragraphs; one run cell per part whose first line is the comment `# Part x` (outside the `run_code` string, so line numbers inside are unchanged); the check strips exactly that line |
| Wrong calls (ch02 Q10, ch03 Q10/Q14, ch04 Q14/Q15) | definition cell + "Two correct ways to call it" examples (≥2 python+output pairs) + parts | `run_code` run cells |
| Definition cells (ch03 Q10/Q14, ch04 Q14/Q15, ch05 Q14, ch06 Q15) | visible code cell, must produce no output (checked) | n/a |
| Write code (34 questions) | unchanged: prompt, header block, ≥2 examples, `# Your code here`. **No question-code cells** | heading + markdown solution(s) only; no run cell |
| Refactor / generalize (ch03 Q12; ch04 Q11/17/18/19; ch06 Q12) | the given code is an ordinary python block in the prompt, **not** tagged question-code | as write-code |
| Doctest (ch07 Q14) | 1 question-code cell | plain run cell. It never needs `run_code` (it doesn't raise), and the check forbids `>>>` lines inside `run_code` strings |
| Turtle "what is drawn" (ch04 Q2/Q6/Q7, ch05 Q17) | 1 question-code cell | `<img data-turtle>` in the explanation, drawn by `turtle_images` from the question-code block; the run cell draws live (hidden until opened) |
| Turtle canvases that reveal (ch04 Q14 a–c) | parts | `run_code` run cells; empty canvases appear only inside the Answer |
| Files (ch07 Q9/Q15) | question-code | plain run cells (words.txt comes from setup) |
| ch04 Q7 ("assume restarted") | reword "and this cell" → "and only the setup cell" | `run_code` (NameError for `jupyturtle`) |

## 4. How answers collapse in each environment

- **Colab** (BELIEVED until test R1):
  - The Answer heading's id is listed in `metadata.colab.collapsed_sections`, and `metadata.id` equals the top-level `id`, which is exactly what Colab itself writes for nbformat 4.5 files.
  - A collapsed section hides its cells and their outputs behind "↳ N cells hidden". Run all runs them (BELIEVED, test R4–R6).
  - Colab's TOC sidebar lists 17 "Answer" headings per page (cosmetic).
- **JupyterLab 4 / Notebook 7** (VERIFIED):
  - The pages open collapsed through `jp-MarkdownHeadingCollapsed`, and Run All keeps the outputs hidden.
  - Shift+Enter walks into an Answer and expands it. This is mitigated by the help text; the questions are markdown, so students no longer need Shift+Enter.
- **VS Code, and "Colab in VS Code/Cursor"** (source-read): neither marker is honoured, so everything shows. Accepted; documented in the help cell.
- **Website** (VERIFIED in the prototype):
  - `prep_notebooks.answer_sections` turns each `#### Answer` section into one `:::{admonition} Answer` / `:class: dropdown` cell. That cell holds the explanation markdown; run cells are dropped because the question code is just above.
  - Result: no h4 headings, no Answer TOC entries, and dropdown text identical to today's site. The only visible change is a "Credits" TOC entry.

## 5. One copy of each question's code (option A with an explicit marker)

- **The single source:** the `question-code` markdown cells. The tag is invisible in Colab, JupyterLab and on the site, and it removes the guessing that failed on refactor questions (prototype F12) and the EXAMPLE over-count (F23).
- **`review.sh sync NB`** (new `yr/tools/sync_answers.py`, run in the venv):
  1. For each question, rebuild its run cells from its question-code blocks, keeping existing run-cell ids by position. Add `# Part x` labels when the question has parts.
  2. Execute the page (nbclient, run cells plain, `allow_errors=True`). Wrap each run cell that produced an error output as `run_code(r"""\n<code>\n""")`, and unwrap any that no longer raise.
  3. Choose quotes: `r"""` normally, `r'''` when the code contains `"""`. Refuse, and tell the author, when:
     - the code contains both quote styles or ends with a backslash;
     - `ast.literal_eval` of the generated literal ≠ the code;
     - the code to be wrapped contains a line matching `^\s*>>> ` (IPython ≥ 8 strips such lines; verified).
  4. Set `answer-run` tags, the heading metadata and `collapsed_sections`; strip outputs.
- **The check** (byte equality):
  - Parse each run cell with `ast`: either a plain cell (source == block) or a single `run_code(<str literal>)` call (literal == block).
  - Leading/trailing newlines are ignored, plus the `# Part x` line in multi-part questions.
  - Any other difference means "run: `review.sh sync`".
- **Why not B or C′:**
  - B (`q8a = """…"""`) shows one-colour code, needs `q8a = """` stripped on the site, and adds an order dependency.
  - C′ (`%%question` magic): Pyright flags the magic line and the hidden syntax error. Colab linted `%%writefile` bodies in 2022. A misspelled or unregistered magic raises a UsageError that stops Run all.
  - The editor smoke test (E6) records how Colab treats a custom magic, in case you want to revisit C′.

## 6. `run_code`

```python
def run_code(code):
    """Run code (a string) exactly as if it were a cell of its own.

    The Answers use it for code whose result is an error: the error is shown as usual,
    but it does not stop "Runtime > Run all", so the rest of the page still runs.
    """
    try:
        ip = get_ipython()
    except NameError:                  # plain Python (e.g. yr/tools/turtle_images.py)
        exec(code, globals())
        return
    result = ip.run_cell(code, store_history=False)
    if isinstance(result.error_in_exec, KeyboardInterrupt):
        raise KeyboardInterrupt        # the Stop button still stops "Run all" (verified, kernel side)
```

**Why nested `run_cell` rather than catch + `showtraceback()`.** `run_cell` does the catching and calls `showtraceback` itself, so the reply status is "ok" (verified). It is the only variant that looks like a normal cell on both IPython 7.34 (Colab's pin) and 9.17 (the local checks). The alternatives fall short:
- exec + `showtraceback()`: on 9.17 it shows a `run_code` frame and "Could not get source"; on 7.34 it shows no source lines.
- The linecache + `tb.tb_next` variant drops frames on 7.34 (refuted for ch03 Q14).
- Both exec forms lose the last-expression display.

**How errors look** (verified output of the smoke notebook):
- **Colab-like stack (IPython 7.34):**
  - Syntax error: `File "/tmp/ipykernel_N/510256474.py", line 2` / `if x > 0` / caret / `SyntaxError: expected ':'`.
  - Runtime error: the usual red `TypeError … Traceback (most recent call last)` with `/tmp/ipykernel_N/<hash>.py in <cell line: 0>()`, then `in outer(s)`, then `in inner(s)`, with source lines. That is identical to a plain cell, so ch03 Q14's frame-order answer holds.
- **Local IPython 9.17:** `Cell In[N], line 2 …`, same frames.
- Line numbers match the question block, because leading blank lines are stripped.
- Answers compare only the `Ename: message` line, never file or line headers.
- Colab adds a NOTE to ModuleNotFoundError (ch02 Q14a); the Answer text can mention it.

**Fallback B** (only if Colab's Run all stops on red error outputs; test R4): the same function with `ip._showtraceback` temporarily replaced by `lambda et, ev, stb: print(ip.InteractiveTB.stb2text(stb), file=sys.stderr)`. The traceback text is identical, but it is sent as a stderr stream (verified, both stacks). The check already parses stderr tracebacks (section 7), so switching variants is a one-function change in six setup cells plus the skeleton.

## 7. Tool changes

During Stages 2–4, every tool detects the format **per page**:
- any `#### Answer` heading → new rules;
- `<details><summary>Answer` → today's code path, unchanged;
- both on one page → error.

Old-format support is removed in Stage 5.

### `yr/tools/check_review.py` (new-format path)
1. **Execution.** Run once with `allow_errors=True` and an `on_cell_executed` hook recording reply status. Any status "error" = "Run all stops here" (ignores tags, like Colab). `raises-exception` tags on new pages are reported as obsolete.
2. **Visibility pass** using the real section rules:
   - every code cell with outputs, except `setup`, must sit under a collapsed `#### Answer`;
   - Answer markdown must contain no heading at all (ATX, setext or `<h1>`–`<h6>`, outside code fences), since JupyterLab ends a section at any heading in a cell (fixes skeptic mutation M3);
   - the last cell must not be inside an Answer.
3. **Collapse markers.** Each Answer heading has `metadata.id == id` and `jp-MarkdownHeadingCollapsed: true`. `collapsed_sections` equals the set of Answer heading ids, with no stale ids.
4. **Same code.** ast-based question-code ↔ run-cell equality (section 5). Write-code and refactor questions have no question-code cells and no run cells. Every code cell inside an Answer is tagged `answer-run`, and only those are.
5. **Outputs of run cells**
   - stdout appears exactly in a ```text block (existing rule).
   - Every error line appears in a text block (existing rule). Error lines come from `error` outputs **and** from the last line of an ANSI-stripped stderr traceback, so fallback B can't blind the check (fixes M15).
   - **NEW:** `execute_result` text/plain appears exactly in a text block (closes M2: ch02 Q4, ch03 Q9).
   - **NEW:** a turtle `display_data` (HTML containing `<svg`) requires a filled data-turtle picture in the Answer.
   - **NEW, reverse rule:** every text-block line that looks like an exception (`^[A-Z]\w*(Error|Exception|Interrupt)\b`) must match a produced error (substring either way, to tolerate 3.12 vs 3.13 wording) (fixes M1).
   - **NEW:** stderr that isn't a traceback and isn't shown in the Answer is reported.
   - **NEW:** `run_code` strings must not contain `^\s*>>> ` lines.
6. **Existing checks, kept**
   - Answer ```python blocks run standalone as .py files (Answer = positional cells after the heading).
   - Write-code: header plus ≥2 examples, counted in question markdown **excluding** question-code cells.
   - Wrong calls (definition cell + an error in its run cells) need ≥2 correct calls.
   - No empty pictures; no `(c)`-style symbols.
   - Question-side code cells print nothing.
7. **Optional second pass.** `review.sh check --colab-like` uses a pinned venv (Python 3.12, `ipython==7.34.0`, `ipykernel==6.17.1`, `jupyter_client==7.4.9`) and compares error last lines only.

### `yr/tools/sync_answers.py` (new) and `review.sh`
- Add `review.sh sync NB` (section 5).
- `review.sh` keeps `git rev-parse`, which is fine in the real repo.

### `yr/tools/turtle_images.py`
- New-format split by position: Answer python blocks = blocks in the markdown after the heading.
- Run definition code cells in order. **Do not** run `answer-run` cells.
- An Answer picture with no python block above it in its cell is drawn from the question's **last question-code block**. This replaces the "last code cell above" rule.
- Hardening: if an **example** picture's code raises, exit 1 without writing. Answer pictures may raise (ch04 Q7). This stops the silent rewriting of 19 ch04 PNGs with partial drawings that the skeptic saw under version skew.

### `jb/prep_notebooks.py`
- Add `answer_sections(cells)` from the prototype: heading + markdown → one dropdown; drop code cells; keep the heading's id. Call it in `process_review` before `details_to_dropdown`.
- **Guard:** after processing, `sys.exit` if any `#### Answer` cell survives, or any code cell sits between an Answer dropdown and the next `###`/`##` heading. The build then fails loudly instead of publishing answers in the open.
- `remove-cell` on the help cell is handled by myst-nb.
- Never tag run cells `solution`, which would blank them.

### `yr/tools/review_cells.py` (stays stdlib-only)
- Spec kinds:
  - **new** `%%% question-code` → tagged markdown cell; validate exactly one ```python block;
  - `%%% answer` → heading cell (collapse markers, id copied into `metadata.id`) + explanation cell; reject headings in the body;
  - `%%% code` stays for definition cells.
- `add` then reminds the author to run `review.sh sync`.
- `SKELETON` gains:
  - the new `run_code` in the setup cell;
  - the `remove-cell` Colab help cell;
  - `## Credits` on the credit cell;
  - `"colab": {"collapsed_sections": []}`.
- **New `normalize NB`**: strip outputs and execution counts; drop `metadata.id` from non-heading cells; re-assert collapse markers; rebuild `collapsed_sections`; drop other `colab` keys. Run it after anyone saves a page from Colab.
- `fresh_id` is unchanged; `renumber`/`list` need no change.

### `.claude/skills/check-notebooks/check_notebooks.py`
Static lint for new-format yr pages:
- the markers of check item 3;
- `metadata.id` only on Answer headings;
- every Answer heading has ≥1 explanation cell;
- `question-code` cells hold exactly one python block.

`KNOWN_MAGICS` is unchanged (no custom magic).

### `.claude/skills/check-notebooks/run_notebooks.sh`
Skip `yr/` pages and point to `review.sh check`. Its tag logic would report caught `run_code` errors as failures (skeptic simulation: 4 cells on ch05).

### `.github/workflows/deploy-book.yml`
Add a step `python3 .claude/skills/check-notebooks/check_notebooks.py` before the build. It's fast and static, and blocks publishing malformed pages. First verify that it passes on today's v3.

### Mutation self-test (new: `yr/tools/selftest_review.py`, run by `review.sh selftest`)
- A small fixture page covering every kind (~8 questions).
- Each mutation is applied to a copy and must be caught:
  - the prototype's 10;
  - M1 (code no longer raises, Answer still claims an error);
  - M2 (`price * 4`);
  - M3 (`#### Note` inside an Answer);
  - M15 (stderr variant + wrong error text);
  - a run cell edited but not its question-code cell;
  - a stale `collapsed_sections` id;
  - a `>>>` line inside `run_code`;
  - a missing `answer-run` tag.
- This keeps the checks from silently weakening later.

## 8. README and skills
- **`yr/README.md`:**
  - rewrite "Layout of a page" (sections 3–4 here), "Answers", "Cell conventions" (question-code cells, `#### Answer` sections, no headings inside Answers, run cells generated by sync, `run_code` and what errors look like, the `>>>` rule);
  - add a short "How students use the page" (Run all, open Answers, avoid Shift+Enter);
  - update the Tools list (`sync`, `normalize`, `selftest`) and the `review.sh check` list.
- **`yr-review-questions` SKILL.md:** new spec example (`%%% question-code`, `%%% answer`). Workflow: add → `review.sh sync` → `review.sh images` → `review.sh check` → `check_notebooks` → `build_book.sh`. Rules: no headings in Answers; parts get a `**Part x**` line; the question code must be self-contained (NameError answers rely on page order).
- **`yr-review-page` SKILL.md:** the new skeleton (help cell, Credits heading, `run_code` everywhere).
- **`notebook-conventions` SKILL.md** (around L86): the Answer format sentence.

## 9. Converting the six pages
- **Script:** `yr/tools/convert_answers.py`, based on `scratchpad/ultra/proto/scripts/convert.py`. Commit it with the tools and delete it in Stage 5; git history keeps it. Per page:
  1. Every question code cell that is not a definition cell (by the prototype's `is_definition_only` rule) becomes one `question-code` markdown cell. A `**Part x**` markdown cell just above it is folded into that cell.
  2. The old `<details>` cell becomes the `#### Answer` heading, **keeping its id**, plus an explanation cell (new id) holding the details body.
  3. Each old question code cell's **id moves to its run cell**.
  4. Remove `raises-exception` tags; replace the old `run_code` definition (add it to ch06); turn the `run_code` intro paragraph into the `remove-cell` help cell.
  5. Add `## Credits`, then run `review.sh sync`, which wraps raising code, sets quotes, labels and metadata.
  6. Print a list of cells containing stale wording for hand editing: "then run it", "Run this cell", "For each of the next … cells", "this cell", "and this cell" (ch02 Q4/Q9/Q14, ch03 Q9/Q10, ch04 Q7/Q14, ch07 Q15).
- **Order:** ch05 (pilot; it has syntax errors, a RecursionError, a turtle tree and write-code), then ch02, ch03, ch06, ch07, and ch04 last (22 pictures, the Q7 premise, Q14 canvases, Q15's version-dependent message, Q18's `jump`).
- **After each page:** `review.sh images` must leave the PNGs byte-identical (`cmp`; the prototype achieved this for ch04 and ch05), then `review.sh check`.

## 10. Verification

### Here, before anything reaches you (all scriptable)
1. `review.sh check` on all six pages on the default stack, and on the Colab-like stack after each conversion.
2. `review.sh selftest`: every mutation caught.
3. `check_notebooks.py`, then `build_book.sh` with no new warnings (`comm -23` against `known_warnings.txt`).
4. Site diff with BeautifulSoup: per page, the number of Answer dropdowns equals the number of questions, none open, 0 h4, 0 "Answer" TOC entries, 0 leftover `<details>`. The dropdown text must equal the old page's (the skeptic got this result with the prototype).
5. For the tools commit, the built HTML of the still-old pages must be identical to before.
6. Simulated Colab Run all (nbclient `allow_errors=False`, `force_raise_errors=True`) on both stacks: reaches the end, and every output is hidden except setup.
7. Optional, for the pilot only: headless JupyterLab 4.6.4. Opens collapsed; Run All keeps outputs hidden.
   - Traps: `--allow-root`, `--LabApp.expose_app_in_browser=True`, and Playwright `executable_path=/opt/pw-browsers/chromium-1194/chrome-linux/chrome`.
   - Never run `pkill -f` with a pattern that appears in the command itself; it kills the calling shell.

### In Colab: what you check (about 25 minutes, one session)

With your OK, Claude pushes a throwaway branch `colab-smoke-test` (it never deploys; only v3 deploys). It contains `colab_tests/` built by `scratchpad/ultra/plan-risk/make_smoke.py`; commit that generator too, since the scratchpad is temporary. Open each notebook from its GitHub link, e.g. `https://colab.research.google.com/github/y-rosenthal/yrThinkPython/blob/colab-smoke-test/colab_tests/colab_test_runall.ipynb`. Use default settings; Runtime → Disconnect and delete runtime between notebooks.

**Notebook 1: `colab_test_runall.ipynb`**

| # | Do | Expected | Report |
|---|---|---|---|
| R1 | Before running: look at Tests 1–10 | Test 1 collapsed (full metadata). Test 2 (Colab list, top-level id only) and Test 3 (JupyterLab key only) show what Colab really needs. Tests 4–10 collapsed | collapsed yes/no per test |
| R2 | Is any "SECRET n" text visible without clicking? | only in tests that R1 found expanded | which |
| R3 | Runtime → Run all; wait for it to finish | — | duration, any popup |
| R4 | Which "MARKER n" cells show output; is "END" printed? | MARKER 1–11 and END | last MARKER shown |
| R5 | Without clicking: did any Answer open by itself, or the page scroll into one? Any red error icon on a heading, a "cells hidden" row or the TOC? Compare the rows of Tests 4–5 (stderr) and 6–8 (red error output) | nothing opened, no icons | screenshot |
| R6 | Is any "LIVE n", traceback or drawing visible outside an Answer? | only the setup version line, MARKERs, END, Test 11's closed boxes | yes/no |
| R7 | Open Tests 6, 7, 8, then 4, 5, then 9, 10 | red tracebacks (7 lists outer then inner); 8 may have a Colab NOTE; 4–5 the same text in stderr style; 9 shows `12`; 10 a square | screenshots |
| R8 | Test 11: open both "Show the output" boxes | box 1: `start`, a line drawing, ZeroDivisionError text; box 2: `12` | works yes/no |
| R9 | Reload from the GitHub link. Click Test 9's question-code cell, press Shift+Enter repeatedly; then Esc + Down arrow; then Ctrl+Enter | — | does each one open Test 9's Answer? |
| R10 | Open the TOC sidebar | Answer entries listed | cosmetic note |
| R11 | Copy the setup cell's first output line | e.g. `Python 3.12.x \| IPython 7.34.0 \| ipykernel 6.17.1` | the line |
| R12 | File → Save a copy in Drive, open the copy | — | still collapsed? (information only) |

**Notebook 2: `colab_test_editor.ipynb`** (never run it; press Connect so the checker runs)
- For cells E1–E7, click in and wait 5 s. Note: underlined?, coloured?, any "unknown magic" warning (E6)?
- Repeat with Tools → Settings → Editor → Code diagnostics = "Syntax and type checking", then restore the default.
- Expected: E1 underlined, E4 (strings) not underlined, E7 not underlined. E2, E3, E5 and E6 are the unknowns.

**Notebook 3: `colab_test_stop.ipynb`**
- S1: Run all; press Runtime → Interrupt execution after about 10 s. Expected: no "END".

**Pilot page (Stage 3)**, opened from branch `yr-review-runall` at `.../blob/yr-review-runall/yr/chap05_review.ipynb`:

| # | Do | Expected |
|---|---|---|
| P1 | Open | all 17 Answers collapsed; questions show code as text; help cell visible |
| P2 | Run all | no error popup; afterwards nothing beyond the setup output is visible |
| P3 | Open Q8 | three run cells with SyntaxError, SyntaxError, IndentationError matching the text blocks |
| P4 | Open Q14 | RecursionError (short traceback on IPython 7.34) |
| P5 | Open Q17 | stored PNG tree, plus the live tree drawn |
| P6 | Open Q9 (write code) | explanation and solution only; your own code in `# Your code here` runs with Ctrl+Enter |
| P7 | Collapse an Answer again | it hides again |

**What the results mean**

| Outcome | Action |
|---|---|
| R1 Test 1 collapsed, R4 END, R5/R6 clean | main design with variant A |
| R4 stops right after MARKER 5 (variant A blocks Run all) | switch `run_code` to variant B; the check already parses stderr; redo R4 |
| R5 shows red icons only on the A rows | switch to B (avoids hinting which Answers are errors) |
| R1 Test 1 **not** collapsed, or R5 shows auto-expansion | fallback C (section 11) |
| R1: Test 2 also collapsed | keep writing `metadata.id` anyway (harmless); no change |
| R9: Shift+Enter or Down opens Answers | keep the design; the help cell says "use Run all, then click Answers; don't step with Shift+Enter" (the questions are text, so stepping isn't needed) |
| S1: END printed | look into Colab's interrupt handling; minor (documented) |
| R11 shows IPython ≥ 8 | nested `run_cell` still looks normal (verified on 9.17); keep the `>>>` rule; re-run `check --colab-like` with that version |

## 11. Fallbacks
- **Fallback B** (stderr tracebacks): section 6. Verified locally; one function changes.
- **Fallback C** (collapsed sections unreliable in Colab):
  - Use the same question-code cells and generated run cells, but the run cells sit **outside** any collapsed section and call `run_hidden(r"""…""")`.
  - `run_hidden` captures stdout, stderr tracebacks, rich displays (the last version of each turtle display) and the last expression. It shows them inside one closed HTML `<details>` "Show the output" box, and the explanation stays a markdown `<details>` as today.
  - Verified locally: one `display_data`, status ok, on both stacks. It needs no collapse metadata, nothing reveals on Shift+Enter, and Colab cannot stop on an error output because none exists. Test R8 shows whether Colab renders it.
  - For the check, `run_hidden` also attaches `metadata={"yr": {"stdout":…, "errors":[…], "result":…}}` to its display, so check_review reads exact values rather than parsing HTML. prep drops the run cells as in the main design.
  - Costs: no live animation, and tracebacks lose colour.
- **Squiggles:** the main design has no visible erroneous code, so the E-test results are informational. If E2 shows undefined names underlined on default settings, keep definition cells free of undefined names (they already are).
- **Rollback at any stage:** section 12.

## 12. Rollout stages, gates and rollback

| Stage | Work | Gate before moving on |
|---|---|---|
| 0 (done) | Research, prototype, skeptic verification, smoke notebooks (scratchpad) | — |
| 1 | You run Colab notebooks 1–3 (needs your OK to push `colab-smoke-test`) | outcome table, section 10 |
| 2 | Branch `yr-review-runall`: dual-format tools, sync, normalize, selftest, prep guard, lint, docs. No page changes | old pages pass the old check unchanged; site HTML identical; selftest green; `check_notebooks` OK |
| 3 | Convert ch05 on the branch; local verification (section 10) | you run P1–P7 from the branch link; then merge to v3 via `yrpublish`; check the live page and the real v3 Colab link |
| 4 | Convert ch02, ch03, ch06, ch07, then ch04, one commit each, each through the same local checks; one Colab spot-check per page (an error question + a turtle question) | green checks; your spot-check |
| 5 | Cleanup: remove old-format paths (check rejects `<details>` Answers), delete `convert_answers.py`, add the CI lint step, final docs | all six pages green |

**Rollback**
- **Stages 3–4:** `git revert <page commit>` on v3 brings back the old page. The tools still read both formats, the site redeploys on push, and Colab links (which point at v3) change at once.
- **A bad tools commit:** revert it. Pages still in the old format don't depend on it.
- **After Stage 5:** revert the cleanup commit first.
- Never push to v3 without `review.sh check` on all six pages and a build with no new warnings.

## 13. Open decisions for you (with recommendations)
1. **Order inside an Answer.** Recommend: explanation first, run cell(s) last (prototype-tested; the site shows the same explanation). Alternatives: run cells first, or two sections ("Run it" / "Explanation").
2. **Write-code Answers.** Recommend converting them to `#### Answer` sections too, so there is one way to open an answer. They contain markdown only.
3. **Credits.** Recommend a `## Credits` heading (one extra TOC entry). The alternative is moving the credit line into the title cell.
4. **Rollout.** Recommend page by page, piloting with the page your students will use next (or ch05), rather than all six at once.
5. **Variant A vs B.** Recommend A (normal red tracebacks) if R4 and R5 pass; otherwise B.
6. **If Colab ignores collapse metadata.** Recommend fallback C over keeping today's layout.
7. **Help cell.** Recommend a short Colab-only cell (tagged `remove-cell`): Run all is safe, click the arrow next to Answer, don't step with Shift+Enter, VS Code shows everything.
8. **CI lint in deploy-book.yml.** Recommend yes.
9. **Website code blocks.** The question code shows as plain markdown code blocks instead of code-cell styling. Recommend accepting this.
10. **Colab-like second check.** Recommend adding `review.sh check --colab-like` (Python 3.12, IPython 7.34), run at each page conversion. CI already uses Python 3.12.
11. **Permissions.** Pushing `colab-smoke-test` and `yr-review-runall` needs your approval. Nothing has been pushed or changed in the repo.

## 14. Files from this planning step
These are in `/tmp/claude-0/-home-user-yrThinkPython/6571a165-f8cc-5e43-8b74-c00357a4a6f6/scratchpad/ultra/plan-risk/`. The scratchpad is lost when the container is reclaimed; commit `make_smoke.py` on the smoke branch.
- `make_smoke.py`: builds `out/colab_test_runall.ipynb`, `colab_test_editor.ipynb`, `colab_test_stop.ipynb`.
- `verify.py`, `stoptest.py`, `showhidden.py`, `uniform.py`, `dt_debug4.py`.
- Logs: `logs_runall_ipy{7,9}.txt`, `logs_stop_ipy{7,9}.txt`, `logs_uniform_ipy{7,9}.txt`, `logs_doctest_strip_ipy{7,9}.txt`.

`/home/user/yrThinkPython` was not modified (git status clean, HEAD b389c80).


## assumptions_needing_colab_test

- R4: Runtime > Run all continues past a cell that shows a red error output while its execute_reply status is 'ok' (run_code via nested get_ipython().run_cell). Verified in kernel, nbclient, JupyterLab and Notebook 7, but not in Colab's frontend, which has server_execution_queue / execution_status_propagation flags.
- R4: if variant A stops Run all, a traceback printed on stderr (variant B, no 'error' output) lets Run all continue in Colab.
- R1: a notebook opened via colab.research.google.com/github/... opens with the '#### Answer' sections listed in metadata.colab.collapsed_sections collapsed, when each heading has id == metadata.id. Also: whether the top-level id alone (Test 2) or only jp-MarkdownHeadingCollapsed (Test 3) is enough.
- R5/R6: Run all executes the cells inside collapsed sections without expanding them or scrolling to them, and their outputs (prints, tracebacks, turtle drawings) stay hidden.
- R5: no red error badge or status icon appears on a collapsed Answer heading, its 'N cells hidden' row or the TOC sidebar that would reveal which Answers contain errors (compare stderr rows vs error-output rows).
- R9: whether Shift+Enter, Down-arrow or Ctrl+Enter moving into a collapsed Answer expands it (JupyterLab: verified yes for Shift+Enter; Colab: Down-arrow did in 2018).
- S1: pressing Interrupt during a run_code cell stops Run all (the re-raise is verified kernel side on IPython 7.34 and 9.17).
- R11: Colab's live runtime versions (believed Python 3.12 with IPython 7.34.0 / ipykernel 6.17.1, possibly moving to Python 3.13). This affects traceback headers, the IPython >=8 stripping of '>>>' lines inside strings, and version-specific error messages.
- R7: tracebacks from nested run_cell look like a normal cell's in Colab (frames listed outer then inner for ch03 Q14), and Colab's ModuleNotFoundError NOTE is the only extra text.
- R8: an HTML <details> box inside a cell output renders and opens in Colab's output iframe (needed only for fallback C).
- E1-E7: markdown ```python blocks and code inside run_code strings are never underlined. Also: whether Colab underlines undefined names on default settings, honours a top-of-cell '# type: ignore', and how it shows or lints a custom %%question cell magic.
- A markdown cell tagged remove-cell, and question-code / answer-run tags, are invisible and harmless in Colab (believed: Colab has no tag UI).
- R10: Colab's TOC sidebar lists every '#### Answer' heading (cosmetic only).
- R12: saving a copy to Drive keeps or drops the collapsed layout (information only; the GitHub source keeps the default).

## dry_choice

Option A with an explicit, invisible marker. Each question's code is written once, in markdown cells tagged `question-code` (one ```python block per cell or part). `review.sh sync` (new yr/tools/sync_answers.py) generates the Answer's run cells from those blocks. A run cell is the plain code, or `run_code(r"""...""")` when actually running the page shows that the code raises. sync picks r""" or r''' (needed for docstrings) and refuses code it can't quote exactly, or code with `>>>` lines (IPython >=8 strips them inside strings; verified). Multi-part run cells get a `# Part x` comment line outside the string. `review.sh check` extracts each run cell's code with ast and fails on any byte difference from its question-code block. Rejected: B (string variable: one-colour code, `q8a = """` on the site, order dependency) and C' (%%question magic: Pyright flags the magic line and the hidden syntax error, Colab linted %%writefile bodies before, and a missing or misspelled magic raises a UsageError that stops Run all). C (reading the .ipynb) doesn't work in Colab.

