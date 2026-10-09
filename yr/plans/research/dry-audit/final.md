# DRY / generated-answers audit: final answer

Workflow `dry-generated-answers-audit.js`, run on Prof. Rosenthal's laptop on 2026-10-09 (17 agents, all completed).
Full results (audits, designs, judges, draft, critic): `result.json`. Agents' working files and prototypes: `work/`.

## 1. Where DRY fails, today and in v2

Short answer: no. v2 meets your two rules (R1: type each text once; R2: generate every answer by running code) only for the "what is displayed / what happens / find the error" questions. It does not meet them for write-code questions, fixes, provided helpers, examples or prose. Counts cover all six pages (ch02 to ch07).

| Question kind / text | Today | v2 design | Count (six pages) | Examples |
|---|---|---|---|---|
| **Predict / error / drawing question code** | Typed once, as a code cell | Typed once, as a run block. Sync writes a hidden copy into the run cell, so the FILE holds it twice, but the author types it once | about 84 run blocks | ch02 Q1 `x = 8 ...`; ch05 Q8a-c |
| **Their outputs and error messages** | Hand-typed `text` blocks; today's check compares most with the real output | **Generated** (stored real output) | 82 blocks (ch02 20, ch03 15, ch04 12, ch05 12, ch06 11, ch07 12) | ch05 Q8a-c |
| **Error-name records** | none | **New hand-typed copies** of the generated error name, `<!-- error: X -->` (checked by S10) | 24 (8+4+6+4+1+1) | ch02 Q10 types "TypeError" 4 times |
| **Write-code function headers** | Typed in the question and again in every solution | Same | 30 headers, each typed 2-4 times | `def sign(x):` 3 times (ch05 Q4); `def is_teen(age):` 4 times (ch06 Q12) |
| **Write-code example calls and inputs** | Typed in Examples and again in each Answer approach | Same (S13's ".py must run alone" rule forced the repeat) | 145 repeated lines in 57 Answer blocks (34 questions) | ch02 Q11 `hours = 1 / minutes = 2 / seconds = 3` 3 times; ch03 Q12 `verse('cow', 'moo')` 3 times |
| **Write-code example outputs** | Hand-typed; no check compares them with a solution (checks only count them) | Same | about 52 text blocks | ch06 Q16 `-12 0`; ch03 Q11 right-aligned lines with typed leading spaces |
| **"Two correct ways to call it" outputs and help() output** | Hand-typed, unchecked | Same | 12 text blocks plus ch04 Q12 help() (ch04 Q14's two pictures are already generated) | ch03 Q10 `2 + 3 = 5`; ch06 Q15 `6`, `1` |
| **Turtle example and answer pictures** | Already generated (turtle_images.py) | Generated | 19 examples plus 4 answer drawings | none |
| **Helpers the question provides** | Shown as markdown text, then pasted again into the Answer | Same | ch04: jump typed 7 times, square 5, polygon 4, describe 2 (Q5, Q15); ch07: run_doctests 3 | ch04 Q17: square and jump in the question and in both approaches |
| **Fixes and second approaches** | Retype most of the question code or of the first approach | Same | ch02 Q4, Q15; ch05 Q7, Q10, Q14; ch06 Q5, Q8, Q15; ch07 Q8, Q12, Q14 | ch07 Q14 retypes all 19 lines to change `word` to `word.lower()`; ch05 Q10's second approach repeats 7 of 9 lines |
| **Outputs of fixes and counterfactuals** | Typed in prose, typed in a text block, or never shown | Same. S13 compares stdout with a text block that follows an Answer block (ch02 Q4 `8`/`12`, Q15 `80.0`). A block with no text block after it (ch07 Q14 fix, ch07 Q17) is checked by exit code only, so a failing doctest passes. Outputs quoted in prose are never checked | about 15 | ch07 Q8 "This displays `3`"; ch05 Q6 "with elif only `big`" |
| **Values quoted in prose (Answers and Concepts)** | Hand-typed, unchecked | Same | 275 claims: 264 evaluable, 263 correct, 1 likely wrong (ch05 "about 3000" frames) | ch05 Q17 "70, 42, 25.2, 15.12, 9.072"; ch02 Concepts "`round(3.14159, 3)` is `3.142`" |
| **Verdicts, traces, drawing descriptions** | Hand-typed | Same; these cannot be generated | about 11 claims plus the verdicts | "It is a semantic error"; "the calls get n = 5, 3, 1, -1, ..." |
| **Part labels** | Typed in the question and again in the Answer | Same (sync only writes a TODO stub) | 22 parts (ch02 10, ch03 3, ch04 6, ch05 3) | ch02 Q9 a-e |
| **Boilerplate** | Answer wrapper, hand-numbered headings, "Start from this header", **Examples**, `# Your code here` | `#### Answer` still typed; the rest unchanged | 103 Answer wrappers; 30 header prompts | none |
| **Page frame** | Title, intro, credits, download() and the chapter number typed on every page | Only the help note is generated | 6 pages | the intro sentence about `run_code` (the plan already has the new wording; the dry-run converter has not applied it on ch02, ch03, ch04, ch07) |
| **Concepts vs the questions, and Concepts vs itself** | Same code or facts in two places | Same (editorial) | every page | ch03 `<function __main__.greet()>`; ch07 Gadsby facts; ch04 jupyturtle facts in Concepts and the intro; ch02 keyword/statement/error facts listed twice inside Concepts |

**Verdict.** v2 closes the biggest R2 gap: the 82 predict and error outputs are generated. For R1, the only duplicate it leaves is a generated copy of the question code. It does not change the write-code questions, which are the most repetitive part of every page, and it adds 24 new hand-typed error records. Every example output, fix output and prose value is still typed. Today they are all correct except probably one (ch05's "about 3000" frames: 1000 locally, Colab not yet checked). But no tool keeps them correct.

## 2. Recommendation

# Recommendation: design-3 (v2 plus a "fill markdown" step), with the best generators from design-1

**Which design is which** (folders under `yrThinkPython-work/dry/`):

| Folder | Design | Status |
|---|---|---|
| `design-1/` | Generator-first: sync generates headers, imports and inline values (gen_static.py, inline_values.py) | take its generators |
| `design-2/` | `%%question` / `%answer` magics (yr_review.py, proto.ipynb) | fallback only |
| `design-3/` | v2 plus one sync step that fills markdown (proto_writecode.py) | **recommended base** |

Three judges scored the three designs. design-3 scored best on balance (8/8/8). It has the lowest Colab risk and needs the least new work. Its evidence on disk:
- **R3 for write-code questions:** all 34 were trimmed and run, with 0 failures. Trimmed *fixes* (the 11 fix blocks) have not been prototyped yet.
- **Examples:** 72 of 72 text examples matched exactly. The turtle examples were only run; `verify-examples/` reproduced their pictures separately (all 86 typed example outputs are correct).
- **Headers:** 29 of 30 are identical to today's typed header block.

Take from design-1:
- generated visible error names;
- generated import lines in Answers;
- checks on error-kind words, on "nothing is displayed", on quoted code and on names in the prompt;
- generated setup sentences and "Run this cell to define ..." sentences;
- derive markers for fixes that change one token.

Keep design-2 as a fallback only, for three reasons:
- Colab's editor may underline the errors before the student predicts them.
- During Run all, the Answer cells overwrite the student's own function.
- Clicking an Answer cell before setup has run wipes its stored output.

## The rule in one line
The author types each fact once: the question code, each helper, the reference solution, each example call, each fix, and the expression behind each quoted value. `review.sh sync` runs the code and writes every output, header, import line, error name and quoted value. `review.sh check` fails if running sync again would change anything.

## By question kind

**1. What is displayed / drawn / happens; errors; multi-part.** As in v2: a run block, a hidden run cell and a stored output. One change: v2's invisible `<!-- error: X -->` records go away, and the visible error name is generated.
```
Author types:   `=` assigns; comparing needs `==`, so this is a <!--=error-->`?`.
Student sees:   ... so this is a `SyntaxError`.   [then the real traceback]
```
Part labels and question numbers are rewritten on every sync.

**2. Write a function.** The author types the prompt, the example calls (no outputs) and one reference solution with its own imports (no example calls).
```
Author types (question):   end_hour(9, 3)
                           end_hour(22, 5)
Author types (Answer):     def end_hour(start, duration):
                               print((start + duration) % 24)
Student sees (question):   Start from this header ... def end_hour(start, duration): ...   [generated]
                           end_hour(9, 3) -> 12;  end_hour(22, 5) -> 3                   [generated]
```
- Each other approach is checked against every example whose function it defines.
- A near-copy approach can be written as a derive marker.
- ch04 Q12's help() output is generated too.
- **Trimmed Answers are silent.** A copied Answer defines the function and prints nothing, because the example calls are not repeated (your rule allows this). Optionally, sync can add a line under it: "Then try: `end_hour(9, 3)`". That line is a generated copy, not retyping.

**3. "Two correct ways to call it".** These are ordinary example pairs. sync fills in their outputs.

**4. Write code with no function (ch02 Q11, Q12, Q16, Q17).** Example 1's inputs become a definition cell, "Run this cell to assign `hours`, `minutes` and `seconds`", and its output is generated. The Answer holds only the computation.

**5. Provided helpers.** They move from markdown text into a runnable definition cell. It is typed once and placed where the helper is first provided. Later questions get a generated pointer ("uses `square` and `jump` from Question 11"), which sync renumbers when questions move.
- ch04 `square` and `jump`: one cell in Q11; Q17 and Q18 point to it.
- ch04 `polygon`: stays in Q14's own cell, because Q14 asks students to read its docstring; Q18 points to it. Q3's second approach *defines* polygon as its answer. That is not a repeat, because polygon is not provided until Q14.
- ch04 `describe`: Q5 (predict) and Q15 (definition cell) both type the same two lines. Keep both so each question stands alone; this is listed below as a repeat by design.
- ch07 `run_doctests`: one cell where it is first used; later questions point to it.
- Answers never repeat a provided helper.

**6. Fixes and counterfactuals.** The fix block shows only what changed. sync runs it after the question's code and writes its output, including a generated "(nothing is displayed)" when it prints nothing.
- ch02 Q15: just the corrected `average = ...` line plus `print(average)`, then the generated `80.0`.
- ch07 Q14: a derive marker, so the 19 lines are not retyped.
- **Name reuse hazard.** ch02 Q4's code sets `price = 4`, but Q16's Example 1 inputs (`price = '19.99'`) run later. After Run all, a trimmed Q4 fix `print(price * 2)` displays `19.9919.99`, not `8`. Three safeguards:
  - check C4 runs each Answer block in the namespace as it is at the END of Run all;
  - a lint lists module-level names that more than one question assigns;
  - a fix that uses such a name keeps its input line (a short, checked repeat), or one of the names is renamed.

**7. Refactor / generalize (ch03 Q12; ch04 Q18, Q19; ch06 Q12).** The given code runs privately. "Same output before and after" becomes a check:
- for text, the stdout must be identical (ch03 Q12: the given verse code against `verse('cow', 'moo')` plus `verse('duck', 'quack')`);
- for drawings, the SVG hashes must be identical.

**8. Values quoted in prose.** The author types the expression, and sync writes the value:
```
Author types:   `-7 // 2` is <!--=-->`?`, not `-3`.   Only <!--= n -->`?` words.
Student sees:   `-7 // 2` is `-4`, not `-3`.          Only `10` words.
```
Here `n` must be a variable that the Answer's code defines, or one set by a `<!--do-->` context line.
- **This is mostly manual work**, not an automatic conversion:
  - Today's claim list (prose-claims/check_claims.py) stores each claim as a hand-written expression plus a section label, not as a position in the cell.
  - The regex extractor finds only 86 of the 275 claims.
  - Many claims have no literal expression in the prose ("counts all 11 letters", "only 10 of about 114,000 words"). They need a hidden expression or context.
  - Each page is converted claim by claim. The gate is that the rendered page stays unchanged.
- A lint warns about any new "`A` is `B`" claim that has no marker.

## The marker set (what the author must learn)
| Form | Use | How often |
|---|---|---|
| `` `EXPR` is <!--=-->`?` `` | value of the code span just before | most prose values |
| `<!--= EXPR -->`?`` | value of an explicit expression | prose values with no code span |
| `<!--=error-->`?`` | the stored error name | error questions |
| `<!--do--> CODE` | hidden context for the values after it | a few |
| `<!-- reference -->` | which block is the reference solution | 1 question (ch06 Q17) |
| `<!-- header: f g -->` | override the header guess | about 1 of 30 |
| `<!-- derive: from=... replace="OLD" with="NEW" -->` | near-copy fix | 3 questions |

The comment always goes **before** the value it fills. sync writes the delimiters around generated regions (header, example outputs); the author never types them. If the Colab test shows that inline comments are not invisible, the expressions move to cell metadata instead.

## What R3 looks like
Each Answer block:
- runs when copied into the notebook after Run all;
- carries its own imports, which sync generates from the names the block uses;
- never repeats a provided helper, an example call or an example input (except under the name-reuse rule above).

**Check C4** replaces S13:
- It runs Run all once, then runs each Answer block in that end-of-page namespace **with the setup cell's imported names removed**, so a missing import fails.
- That namespace includes the question's own run blocks, so trimmed fixes (ch02 Q15 `average`, ch06 Q8 `bill`) can use their variables.
- A doctest that prints anything fails.
- A block followed by a text block must print exactly that text.

## Generated text comes from one pinned stack
sync and check refuse to generate on any stack other than `colablike.lock`, as check_v2's R0 already does for run cells. Some text may differ on Colab: error wording (such as ch04 Q15c "Did you mean"), the help() layout, float reprs and the recursion limit. Where it does, either update the lock to Colab's versions or reword the text so that it does not depend on the version.

## Website build
The site is built with Jupyter Book 1.0.4 and MyST-Parser 3.0.1 from notebooks that prep_notebooks.py prepares, and verify_site.py checks it. It must also handle the new pieces:
- prep strips or keeps the markers;
- generated regions and helper cells render correctly;
- an inline comment before a code span leaves no trace in the MyST HTML.

The gate: build the site locally (build_site.sh) and diff the rendered review pages before and after.

## What cannot be generated, and how it is kept correct
| Prose | Kept correct by |
|---|---|
| Verdicts ("runs", "syntax / runtime / semantic error") | Check C8 compares them with the stored exception type |
| "nothing is displayed", "`end` is never displayed" | Check C8 on the stored stdout |
| Code quoted in explanations (`range(4)`, `x = x + 1`) | Check C9: each code span must still appear in the question code or a solution |
| Names in the prompt ("takes `start` and `duration`") | Check C11: they must appear in the generated header |
| Traces ("n = 5, 3, 1, -1, ...") | A small variant block with generated output, or sys.settrace; otherwise listed for a reread |
| Drawing descriptions ("below the starting line") | "Same picture" claims become SVG-hash checks; the rest is a human reread, listed by check |
| General statements ("`X % 10` is the last digit") | Reread. This one (taken from the book) holds for non-negative X; add "for a non-negative X" if you want it exact |

## What still repeats, by design
Typed twice but **checked**, not removed:
- code quoted in prose (C9) and parameter names in prompts (C11);
- the OLD token in a derive marker (derive fails if OLD is not found);
- example inputs quoted in prompt prose (ch02 Q16 "for example `price = '19.99'`"; ch02 Q15 "which is `80.0`" can become a value marker instead);
- refactor prompts whose given code repeats the example output (ch03 Q12, checked by item 7).

Not checked, accepted:
- the `def` lines in each full approach (a solution must contain its own `def` to run);
- ch04 `describe` in Q5 and Q15, and fix inputs kept under the name-reuse rule;
- `#### Answer` and the difficulty/kind labels;
- Concepts entries that overlap a question or each other (ch02 lists some facts twice inside Concepts). A lint warns about any shared code line of 15 characters or more, both within Concepts and between Concepts and the questions.

check keeps the generated copies in the file (run-cell code, outputs, headers, imports) in step.

## Order of work
1. **Tests first:** the Colab tests and the local site-build test.
2. **Prototype C4 on the 11 fix blocks** (ch02 Q4, Q15; ch05 Q7, Q10, Q14; ch06 Q5, Q8, Q15; ch07 Q8, Q12, Q14), together with the name-reuse lint. So far only the write-code Answers have been tried.
3. **Extend sync and check, in this order:**
   1. example outputs;
   2. headers;
   3. trimmed Answers and C4;
   4. error names;
   5. imports;
   6. prose markers;
   7. support in prep_notebooks / V7.
4. **Convert ch05 first**, then ch02, ch03, ch06 and ch07, and ch04 last because it has the most helpers. The gates:
   - each generated block equals the typed block it replaces (86 of 86 already do);
   - the rendered page and the built site change only where intended.

## Where the work is saved
Under `/home/yitz/Dropbox/_yrQuarto-master/yrThinkPython-work/dry/`:
- **`final/answer.json`: this whole answer** (table, recommendation, bugs, decisions, tests);
- the page audit files for ch03, ch04, ch06 and ch07 (`chap03-audit/`, `chap04-audit/`, `ch06-audit/`, `chap07-audit/`). The ch02 and ch05 audits wrote no files, so their findings survive only in the counts and examples above;
- `verify-examples/`, `prose-claims/`, `design-1/`, `design-2/`, `design-3/` and `critique/`.

These are plain files in Dropbox and are not committed to git. The repo and its git state were not changed.

## 3. Bugs found

- Likely wrong value; confirm in Colab: yr/chap05_review.ipynb, Concepts covered > Recursion, says Python allows "about 3000" frames before a RecursionError. Locally sys.getrecursionlimit() is 1000 (Python 3.12.3, ipykernel 7.3.0, IPython 9.17.1, also through nbclient), and the error came at depth 977. Neither ipykernel 6.17 nor IPython 7.34 (the Colab-era versions) changes the limit. The number comes from the book itself (chapters/chap05.ipynb: 'almost 3000 frames on the stack'), measured in Downey's environment. If Colab also shows 1000, the book has the same problem, and it is a candidate for an upstream issue.
- Converter not finished (not a design flaw): the intro still says 'Run the next cell first: it ... defines `run_code`' on ch02, ch03, ch04 and ch07, but the setup cell no longer defines run_code (on ch03 it is now empty). The plan already has the replacement sentence for each page (runall-collapsible-answers.md, the section 5 table, around lines 261 and 749). The dry-run converter had only ch05's edits, hence 'edit did not match' in dryrun.txt. ch06 is correct.
- v2 conversion defect: lead-in sentences dangle where a text block was removed. ch03 Q10a and Q14: 'The call works and displays ... and then ...'. ch04 Q7: blank lines are left after 'draws one line ... to the east:'. ch07 Q14: 'something like this (the line number may differ)' is stale. ch04 Q2, Q14 and Q15: 'run it/the cells to check' is stale.
- v2 conversion defect: ch02 Q10's run cells rely on the setup cell's 'import math'. Clicking one before setup gives a NameError instead of the TypeError answer.
- Tool gap: check_v2 S13 compares stdout only when a text block follows the Answer block (that is how ch02 Q4 and Q15 are checked). A block with no text block after it is checked by exit code only, and a failing run_docstring_examples prints its failure but still exits 0 (verified with chap07-audit/failing.py). So a broken ch07 Q14 fix or ch07 Q17 solution would pass.
- Tool gap: neither today's check nor check_v2 compares write-code example outputs or 'Two correct ways' outputs with any solution; both only count them. All 86 are correct today (verified by verify-examples).
- Tool false alarms: (a) verify_removed.py reports ch03 Q9 as BAD because it compares only stdout, while that answer is an execute_result. (b) verify_removed.py reports ch07 Q1 as BAD. The code is print(letter, end=' '), so the real output ends with a space and no newline. A markdown text block cannot show that, and today's check strips it on purpose. (c) check_v2 S18 flags ch07 Q8 because its own run block assigns num_letters inside the loop. This contradicts the plan's 'ch07 Q8 passes'.
- Minor: some ch04 Answer blocks import names they never use, for example `right` in Q3 and `left` in Q10 approach 1. After trimming, `penup` and `pendown` are also unused in some blocks. Generated imports would fix this.
- Version-dependent text, already known (D17 in the plan): ch04 Q15c's message is the Python 3.13+ wording ('Did you mean 'sides'?'). Colab's Python 3.12 leaves out the suggestion.

## 4. Decisions for Prof. Rosenthal

1. D1 Base design: build on design-3 (folder design-3/: v2 plus a sync step that fills markdown) and add design-1's generators (folder design-1/: generator-first). Keep design-2 (folder design-2/: %%question/%answer magics) only as a fallback. RECOMMEND: yes. It has the lowest Colab risk and the most evidence, and the student sees the same page as in v2.
2. D2 Example outputs (write-code, 'Two correct ways', help()): sync generates them by running the reference solution and then each example, and the author stops typing them. RECOMMEND: yes; check fails if any is stale.
3. D3 Reference solution: by default the first Answer python block; <!-- reference --> points to a different one (needed for ch06 Q17, whose first block is scaffolding). RECOMMEND: yes.
4. D4 Header block ('Start from this header'): generate it from the reference's def lines, for the functions the prompt names in backticks, with <!-- header: f g --> to override (needed for about 1 of 30). Alternative: design-2's single starter code cell `def f(...): ...` in place of the header block plus '# Your code here'. RECOMMEND: generate the header block, keeping today's look; consider the starter cell later.
5. D5 Answer code under R3: drop example calls, example inputs and provided helpers; keep imports, which sync generates. Check C4 replaces S13. It runs each Answer block in the end-of-Run-all namespace with the setup cell's imported names removed; doctests must be silent; a text block that follows must match. RECOMMEND: yes, once the C4 prototype on the 11 fix blocks passes.
6. D6 Provided helpers: put a runnable definition cell where each helper is first provided (ch04 square and jump in Q11; polygon stays in Q14 with its docstring; ch07 run_doctests at first use), with generated 'uses X from Question N' pointers later. Alternative: one page-level helper cell after setup. But that separates polygon's docstring from Q14, and it defines polygon on the page before Q3 asks students to write it. RECOMMEND: a definition cell at first use.
7. D7 ch04 describe is typed in Q5 (predict) and in Q15 (definition cell): keep both so each question stands alone, or have Q15 point back to Q5. RECOMMEND: keep both (two lines; listed as a repeat by design).
8. D8 Error names: drop v2's invisible <!-- error: X --> records and generate the visible name from the stored output (<!--=error-->). RECOMMEND: yes; snapshot acceptance (--accept) still protects the author's intent.
9. D9 Fixes that change one token in a long function (ch07 Q14, ch05 Q14, ch05 Q10 approach 2): a derive marker (the student still sees the full fixed code) versus typing the full fix. RECOMMEND: derive only for these few; elsewhere show only the changed lines.
10. D10 Name reuse across questions (ch02: Q4 sets price = 4, Q16 sets price = '19.99'): a trimmed fix that uses a name a later cell reassigns either keeps its input line, or one of the names is renamed. A lint lists every module-level name that more than one question assigns. RECOMMEND: keep the input line (short, checked); rename only where the reuse could also confuse students.
11. D11 Counterfactual claims ('with elif only big', '30 would display Fizz', 'left(144) draws a flipped star'): a small variant block with generated output, or prose for a reread. RECOMMEND: convert the ones about printed output (ch05 Q5, Q6, Q10, Q11, Q15; ch02 Q16); keep the drawing descriptions as prose, except 'same picture' claims, which get an SVG-hash check.
12. D12 Prose values and the marker set: the seven forms in the recommendation's marker table, with the comment always before the value. Markers are added claim by claim (mostly by hand) with a render-diff gate, not by an automatic conversion of all 263 claims. RECOMMEND: yes, if the Colab test shows inline comments are invisible; otherwise keep the expressions in cell metadata.
13. D13 ch05 'about 3000' frames: replace it with a generated sys.getrecursionlimit(), or reword it to 'about 1000; the exact number depends on the environment'. RECOMMEND: the reworded sentence with a generated number, after checking Colab's value. If Colab also gives 1000, send the book's 'almost 3000' upstream as an issue.
14. D14 Concepts entries that repeat a question or each other (ch03 greet, ch05 x/y, ch06 double/factorial, ch07 Gadsby, ch04 jupyturtle facts in Concepts and the intro, ch02 facts listed twice within Concepts): keep them with generated values, or cut them to a cross-reference. RECOMMEND: keep the question overlaps in Concepts (it should stand alone) with generated values. Delete the duplicate jupyturtle paragraph from the Questions intro and the duplicate facts inside ch02 Concepts.
15. D15 Page frame (title paragraph, intro, credits, download(), setup sentence, 'Run this cell to define' sentences): generate it from one template and from the cells. RECOMMEND: yes; this also applies the planned replacement for the stale run_code sentence on every page.
16. D16 Question numbers, Answer part labels and 'from Question N' pointers: rewrite them on every sync. RECOMMEND: yes.
17. D17 Generated regions inside author cells (the text after a python block, the header, values) versus separate generated cells. RECOMMEND: inside author cells, with delimiters that sync writes. The page reads as it does today, and check C1 reports a hand edit before sync would overwrite it.
18. D18 Version: sync and check generate only on the colablike.lock stack (like R0). Where Colab differs, update the lock or reword the version-dependent text. RECOMMEND: yes.
19. D19 Silent trimmed Answers: a copied Answer defines its function and prints nothing. Leave it so, or let sync add a generated 'Then try: f(...)' line under it. RECOMMEND: add the generated line; it costs no typing.
20. D20 Website: extend prep_notebooks.py and verify_site.py (V7) to handle the markers, generated regions and helper cells. RECOMMEND: yes, gated by a local site build and a diff of the review pages.

## 5. Colab tests needed

- Mid-line HTML comments. In a markdown cell, put `-7 // 2` is <!--=-->`-4` and <!--= n -->`10` in the middle of a sentence. Check that Colab's rendered view shows no stray text and no broken backtick span. Also check JupyterLab and GitHub's preview. This decides the marker syntax (D12).
- Block comments. Confirm that <!-- reference -->, <!-- header: f -->, <!-- derive: ... --> and sync's region delimiters, each on its own line, are invisible in Colab. v2's error records rely on the same thing, and that is not yet checked either.
- Colab's recursion limit. Run `import sys; sys.getrecursionlimit()` and a deep recursion to see where the RecursionError comes. This decides the ch05 '3000' wording and whether to raise it upstream (D13).
- Colab's Python and IPython versions. Run a converted page and compare its outputs with the stored ones: the error wording (ch04 Q15c 'Did you mean'), the help() layout (ch04 Q12) and float reprs. This decides whether to update colablike.lock or reword the text (D18).
- Run all on a converted page that has the new definition cells: the ch02 Example 1 inputs, the ch04 Q11 and Q14 helper cells and the ch07 run_doctests cell. Confirm that they display nothing, that Run all reaches the end, and that no NameError answer (ch02 Q9, ch04 Q7, ch07 Q8) changes.
- Copy-and-run. After Run all, paste trimmed Answer blocks into a new cell (the ch02 Q4 and Q15 fixes, ch04 Q11, ch07 Q17). Confirm that each one runs and shows the right output (ch02 Q4 must show 8, not 19.9919.99). Then try them in a fresh runtime without Run all, and check the help note's wording.
- Out-of-order clicks. In a fresh runtime, click the run button on a run cell (for example ch02 Q10) before the setup cell, and record what replaces the stored answer (the known NameError issue).
- The open v2 items, needed whichever design is chosen: are collapsed_sections honoured when the notebook is opened from GitHub (A2-1)? Also the hidden-code title wording (A2-2) and the red error marks after Run all (A2-4).
- Local, not Colab: build the website (build_site.sh; Jupyter Book 1.0.4 / MyST-Parser 3.0.1) from a converted page, diff its rendered review page against today's, and run verify_site.py. Confirm that the markers leave no trace in the HTML and the dropdowns still work.
- Fallback gate only, if design-2 is ever reconsidered: a notebook whose %%question cells contain a SyntaxError, an undefined name and a call with the wrong number of arguments. Record whether Colab underlines or decolours the body, or shows an 'unsupported magic' toast, using %%writefile as a control.
