# research:repo

I can't tell why the 3rd and 4th research workers failed: this worker (repo-map) has no view of their runs, so their transcripts need checking. What follows is the repo map I was asked for.

Baseline: all six pages pass `review.sh check` today. They hold 103 questions. 69 of them show their answer right under the question as soon as the cell runs; the 34 write-code questions show nothing.

Run all stops on each page at the first cell that raises: ch02 cell 33, ch03 cell 36, ch04 cell 25, ch05 cell 28, ch06 cell 51, ch07 cell 28. 24 cells raise: 19 already use `run_code` and 5 are plain code. The ch06 setup cell has no `run_code`. I confirmed the stop with nbclient (allow_errors=False); Colab itself is not reachable from here.

## (1) Every question
Abbreviations used in the table:
- **cell types:** `code` = plain cell, `rc` = `run_code` cell, `RX` = tagged raises-exception, `def` = 'Run this cell to define X' cell (no output), `YC` = '# Your code here' cell.
- **kinds:** `wid` = what is displayed, `pic` = picture placeholders in the question's examples, `hdr` = function headers shown.
- **Giveaway** = the cell shows something when run that reveals the answer.

| Page | Q | Level | Kind | Question-side cells | Live output when run (giveaway?) |
|---|---|---|---|---|---|
| 02 | 1 | easy | wid | code | 3 printed lines (yes) |
| 02 | 2 | easy | wid | code | 3 lines (yes) |
| 02 | 3 | easy | wid | code | 2 lines (yes) |
| 02 | 4 | easy | wid (last-expression display) | code | execute_result `12` (yes; not checked today) |
| 02 | 5 | med | wid | code | 1 line (yes) |
| 02 | 6 | med | wid (comments) | code | 2 lines (yes) |
| 02 | 7 | med | wid (math) | code | 4 lines (yes) |
| 02 | 8 | med | wid | code | 3 lines (yes) |
| 02 | 9 | med | legal/illegal names, Parts a-e | 5 rc (b,c,d RX) | a and e print; b, c, d SyntaxError (yes) |
| 02 | 10 | med | wrong calls (math.pow), Parts a-c, 2 correct calls in markdown | 3 rc+RX | TypeError ×3 (yes) |
| 02 | 11 | med | write code, no function (no-signature) | YC | none |
| 02 | 12 | med | write code with comments (no-signature) | YC | none |
| 02 | 13 | hard | wid (swap) | code | 1 line (yes) |
| 02 | 14 | hard | syntax vs runtime errors, Parts a,b | 2 rc+RX | a: 'start' + ModuleNotFoundError; b: SyntaxError (yes) |
| 02 | 15 | hard | find the error (semantic) | code | `193.33…` (yes) |
| 02 | 16 | hard | write code (no-signature) | YC | none |
| 02 | 17 | hard | write code (no-signature) | YC | none |
| 03 | 1-4 | easy | wid | code each | 4 / 3 / 2 / 5 lines (yes) |
| 03 | 5 | easy | write a function `underline` (hdr, 2 text examples) | YC | none |
| 03 | 6-8 | med | wid | code each | 3 / 2 / 6 lines (yes) |
| 03 | 9 | med | wid (function object as last expression) | code | execute_result `<function __main__.greet()>` (yes; not checked today) |
| 03 | 10 | med | local variables + wrong calls, Parts a-c | def + 2 correct calls in markdown + 3 rc+RX | a: print + NameError; b, c: TypeError (yes) |
| 03 | 11 | med | write `print_right` | YC | none |
| 03 | 12 | med | refactor into `verse` | YC | none |
| 03 | 13 | hard | wid (nested calls) | code | 5 lines (yes) |
| 03 | 14 | hard | tracebacks (the answer is about traceback order) | def + 2 correct calls + plain code+RX `outer('hi')` | print + TypeError traceback (yes) |
| 03 | 15 | hard | write `pyramid` | YC | none |
| 03 | 16 | hard | write two functions `print_border`/`print_grid` (3 examples) | YC | none |
| 04 | 1 | easy | wid | code | 4 lines (yes) |
| 04 | 2 | easy | what is drawn | code (make_turtle) | live drawing (yes); answer has stored PNG drawn from this cell |
| 04 | 3 | easy | write `triangle` (2 pic) | YC | none |
| 04 | 4 | easy | wid (function with docstring) | code | 1 line (yes) |
| 04 | 5 | easy | wid (keyword arguments) | code | 2 lines (yes) |
| 04 | 6 | med | what is drawn | code | drawing (yes); answer PNG |
| 04 | 7 | med | what happens ('assume restarted') | rc+RX | drawing + NameError (yes); answer PNG + text |
| 04 | 8-9 | med | wid | code each | 2 / 5 lines (yes) |
| 04 | 10 | med | write `star` (2 pic) | YC | none |
| 04 | 11 | med | write `row_of_squares` (2 pic) | YC | none |
| 04 | 12 | med | write with docstring `staircase` (2 pic + help() text example) | YC | none |
| 04 | 13 | hard | wid | code | 5 lines (yes) |
| 04 | 14 | hard | preconditions, Parts a-c, 2 correct uses with pic | def `polygon` + 3 plain code (a,b RX; c untagged) | empty canvas + TypeError / empty canvas + ZeroDivisionError / empty canvas and no error (yes) |
| 04 | 15 | hard | keyword-argument wrong calls, Parts a-c | def + 2 correct calls + 3 rc+RX | SyntaxError, TypeError, TypeError (yes; part c message depends on Python version) |
| 04 | 16 | hard | write `spiral` (2 pic) | YC | none |
| 04 | 17 | hard | write `grid` (2 pic) | YC | none |
| 04 | 18 | hard | refactor `polygon_row`/`triangle_row`/`square_row` (3 hdr, 2 pic, `jump` given in markdown only) | YC | none |
| 04 | 19 | hard | generalize `arc_n`/`circle` (2 hdr, 3 pic) | YC | none |
| 05 | 1-3 | easy | wid | code each | 3 / 5 / 3 lines (yes) |
| 05 | 4 | easy | write `sign` | YC | none |
| 05 | 5-7 | med | wid | code each | 3 lines each (yes) |
| 05 | 8 | med | find the error, Parts a-c | 3 rc+RX | SyntaxError, SyntaxError, IndentationError (yes) |
| 05 | 9-11 | med | write `end_hour` / `fizzbuzz` / `largest` | YC each | none |
| 05 | 12-13 | hard | wid (recursion) | code each | 5 / 6 lines (yes) |
| 05 | 14 | hard | infinite recursion | def + 2 correct calls + plain code+RX | RecursionError (yes) |
| 05 | 15 | hard | write recursive `stairs` | YC | none |
| 05 | 16 | hard | write `digits_backward`/`digits_forward` (3 examples) | YC | none |
| 05 | 17 | hard | what is drawn (recursive tree) | code (def + drawing) | drawing (yes); answer PNG |
| 06 | 1-3 | easy | wid | code each | 2 lines each (yes) |
| 06 | 4 | easy | write `average` (returns) | YC | none |
| 06 | 5-7 | med | wid | code each | 1 / 4 / 3 lines (yes) |
| 06 | 8 | med | find the bug (return value ignored) | code | `50` (yes) |
| 06 | 9 | med | wid (isinstance) | code | 3 lines (yes) |
| 06 | 10 | med | write `larger`/`largest` | YC | none |
| 06 | 11 | med | write boolean `is_leap` | YC | none |
| 06 | 12 | med | simplify/refactor `is_teen` | YC | none |
| 06 | 13-14 | hard | wid (recursion) | code each | 8 / 1 lines (yes) |
| 06 | 15 | hard | missing base case + write a fix | def + 2 correct calls + plain code+RX | RecursionError (yes) |
| 06 | 16 | hard | write recursive `multiply` | YC | none |
| 06 | 17 | hard | incremental development `triangle_area` | YC | none |
| 07 | 1-3 | easy | wid | code each | 3 / 1 / 3 lines (yes) |
| 07 | 4 | easy | write `exclaim_letters` | YC | none |
| 07 | 5-7 | med | wid | code each | 1 / 2 / 2 lines (yes) |
| 07 | 8 | med | what happens | rc+RX | NameError (yes) |
| 07 | 9 | med | reading a file (words.txt) | code | 2 lines (yes) |
| 07 | 10-11 | med | write `count_vowels` / `first_vowel` | YC each | none |
| 07 | 12-13 | hard | wid | code each | 1 / 3 lines (yes) |
| 07 | 14 | hard | doctests (code defines run_doctests and count_e, then runs them) | code | 8-line doctest failure report (yes) |
| 07 | 15 | hard | searching a file | code | the count (yes) |
| 07 | 16 | hard | write `is_abecedarian` | YC | none |
| 07 | 17 | hard | write with doctests `count_doubles` | YC | none |

## (2) What each tool would have to change
The new layout assumed here: a `#### Answer` heading, then markdown and code cells, with the question's code moved into markdown.

**`check_review.py`**
- `groups_of` (L53) can stay. `#### Answer` stays inside its question's group; I checked this.
- `is_answer` (L49) has to work by position: every cell after `#### Answer` in the group. It feeds `answers` (L98, the source of the ```text blocks), the question text (L129, used for example and header counts) and the 'no Answer cell' check (L142). If it stays cell by cell, the answer's text blocks count as question examples, which silently weakens the write-code check.
- `code_cells` (L100) would then hold the answer run cells plus the definition cells. The stdout and error matching (L102-122) works unchanged; a catching `run_code` keeps error outputs with the right ename and evalue (tested).
- The syntax-error rule (L113, cell must start with `run_code(`) and the raises-exception tag rules (L105-108) need to be updated.
- The EXAMPLE regex (L40) can overcount once question code is in markdown. The wrong-call check (L139-141) assumes definition cells are code cells.
- New checks to add:
  - no code cell before the Answer heading has any output (setup exempt);
  - the page runs with allow_errors=False (L93 currently uses True);
  - for option A, the question's markdown code matches the answer run cell;
  - execute_result checking (today ch02 Q4 and ch03 Q9 are not checked).

**`turtle_images.py`**
- `is_answer` (L42/99) has to work by position, as above.
- The `last_code` rule (L104-118) only works if the answer's run cell comes before the markdown holding the picture.
- Definition cells have to stay code cells (ch04 Q14's example pictures need `polygon`).
- With option B, the `make_turtle(` check (L121) gives a false warning.
- `run_code` must not assume `get_ipython()` exists.

**`prep_notebooks.py`**
- `details_to_dropdown`/`DETAILS` (L139-150) can stay for the concept lists.
- It needs a new step that merges `#### Answer` plus its markdown and code cells into one `:::{admonition} Answer` dropdown cell, with code turned into ```python blocks or dropped. I tested two things in a small Jupyter Book build:
  - the headings would otherwise appear as 'Answer' entries in the page's right-hand table of contents;
  - a dropdown cannot span cells.
- The merge must stop before the credit cell.
- `process_review` (L162) and `process_cell` (L62): never tag answer cells 'solution' (they get blanked), and only %%expect is stripped.

**`review_cells.py`**
- `parse_spec` (L77-93): '%%% answer' must emit a heading, markdown and run cell(s); option A also needs a new kind for question code, which could be generated or synced.
- The skeleton (L137-176) needs the catching `run_code`, something that ends the last answer before the credit cell, and collapsed-section metadata (L188).
- `fresh_id` sets only the top-level id, while Colab stores cell ids in `metadata.id` (seen in a Colab sample notebook).
- `QUESTION`, `list`, `renumber` and `add` need no change.

**`check_notebooks.py`**
- No change needed: notebooks stay output-free, and headings and metadata are not checked.
- A custom cell magic would have to be added to `KNOWN_MAGICS` (L18).

**`build_book.sh` / `deploy-book.yml`** need no change unless helper files are added. `execute_notebooks.py` never runs `jb/yr`.

**Docs:** `yr/README.md`, both yr-review skills, notebook-conventions SKILL.md L86, and the question wording on all pages ('then run it to check', 'Run this cell to define', the `run_code` intros).

## (3) Subtle cases
- **Definition cells** (ch03 Q10, Q14; ch04 Q14, Q15; ch05 Q14; ch06 Q15) produce no output. They can stay visible and run first under Run all, and the wrong-call check and turtle pictures depend on them being code cells.
- **Multi-part questions** (8 questions, listed in F24) compare each cell's stdout with exactly one text block, so keep one answer cell per part. Parts with no error (ch02 Q9 a and e, ch04 Q14 c) keep the same wrapper so they don't hint which parts fail.
- **Write-code examples** exist only in markdown, so Run all is safe for those questions.
- **Turtle:** the live drawing appears in the cell that called `make_turtle()`, i.e. the answer cell in the new layout; the stored PNG stays in the markdown for the website. ch04 Q14's empty canvases reveal answers today. jupyturtle waits 0.2 s per command by default; ch05 Q17 and ch04 Q18/Q19 use delay=0.
- **Last-expression display:** ch02 Q4 and ch03 Q9 break if their code goes through `exec`/`run_code` (option B) unless the helper reproduces the display.
- **Doctests:** ch07 Q14's output is the same through `exec` (tested).
- **Tracebacks:** ch03 Q14 needs the clean traceback variant (skip the helper's frame and register the source with linecache; tested).
- **help()/docstring:** only ch04 Q12's question shows help() text, as an unchecked example.
- **Setup downloads:** ch04, ch05 and ch07 print 'Downloaded …' on first run. Harmless.
- **NameError answers** (ch03 Q10a, ch07 Q8, ch04 Q7) rely on page order and nothing earlier defining those names. I found no dependencies between questions.
- **Credit cell:** it would collapse into the last answer.
- **The ch04 page** is the most complex: 22 pictures, answer pictures drawn from question cells, the 'assume restarted' premise in Q7, Q14's plain raising cells, a version-dependent error message in Q15, and Q18's `jump` defined only in markdown.

Everything is in /tmp/claude-0/-home-user-yrThinkPython/6571a165-f8cc-5e43-8b74-c00357a4a6f6/scratchpad/ultra/repo-map/:
- **Scripts:** `listcells.py`, `analyze.py`, `execnb.py`
- **Executed copies of the six pages:** `run/*.executed.ipynb`
- **Traceback and doctest tests:** `tbtest/t.py`, `t2.py`, `t3.py`
- **Small Jupyter Book test:** `jbtest/`
- **Downloaded Colab sample notebooks:** `dl/`

## Findings

- **F1** [verified]: Baseline: all six review pages pass the current checker unchanged (`check_review.py`, run on copies of the notebooks with the python 3.13 venv). Together the pages have 103 questions: ch02 17, ch03 16, ch04 19, ch05 17, ch06 17, ch07 17. Every question has exactly one `<details><summary>Answer</summary>` markdown cell.
  - Evidence: I ran check_review.py on copies in scratchpad/ultra/repo-map/nbs and every page printed `OK: nbs/chapNN_review.ipynb`. A count script found questions == answers on every page (17/16/19/17/17/17).
  - Impact: This is the reference point. Any redesign has to keep all six pages at OK without weakening a check.
- **F2** [verified]: After running a page, 69 of the 103 questions show output right under the question that gives away the answer. These are every question that is not write-code (ch02 13, ch03 11, ch04 11, ch05 11, ch06 11, ch07 12). The output types are stdout prints, execute_result (ch02 Q4 shows `12`, ch03 Q9 shows `<function __main__.greet()>`), turtle display_data (ch04 Q2, Q6, Q7, Q14 parts a/b/c, ch05 Q17) and error tracebacks. The 34 write-code questions (`# Your code here`) and the 6 'Run this cell to define X' cells produce no output.
  - Evidence: I executed every page with nbclient (scratchpad/ultra/repo-map/run/*.executed.ipynb), and analyze.py lists the outputs of each question's cells. Definition cells ch03 [34],[52], ch04 [46],[55], ch05 [50] and ch06 [49] have no outputs.
  - Impact: Every one of the 69 code cells has to move into the answer section, or have its output hidden. Definition-only cells can stay visible in the question.
- **F3** [verified]: There are 24 cells tagged `raises-exception`. 19 of them are `run_code(...)` cells: ch02 8, ch03 3, ch04 4, ch05 3, ch07 1. The other 5 are plain code that raises a runtime error: ch03 Q14 [54] `outer('hi')`, ch04 Q14 [48] `polygon(4.5, 20)` and [50] `polygon(0, 20)`, ch05 Q14 [52] `countdown_by_two(5)`, ch06 Q15 [51] `factorial(1.5)`. Separately there are 21 `run_code` cells in all, including ch02 Q9 parts a and e, which do not raise. The ch06 setup cell defines no `run_code` (it is only `import math`).
  - Evidence: Count script output, e.g. 'RX 4 RX-plain [54]' for ch03 and 'setup has run_code False' for ch06.
  - Impact: For Run all to finish, all 24 cells (not just the 19 `run_code` ones) must catch their exception. ch06 needs `run_code` (or a similar helper) added to its setup.
- **F4** [strong-evidence]: Run all would stop at the first raising cell on each page: ch02 cell 33 (Q9 part b), ch03 cell 36 (Q10 part a), ch04 cell 25 (Q7), ch05 cell 28 (Q8 part a), ch06 cell 51 (Q15), ch07 cell 28 (Q8). nbclient with allow_errors=False stops at a plain raising cell; that is the stand-in for Colab's Run all.
  - Evidence: Cell indices come from the cell listings. In tbtest/t.py a plain `outer("hi")` cell raised CellExecutionError and the later cell never ran. Colab itself was not tested (its site is not reachable from this container).
  - Impact: Without a fix, students who use Run all never get past the first third of most pages.
- **F5** [verified]: A catching `run_code` (try/except around exec, then `get_ipython().showtraceback()`) gives an output of type 'error' with the right ename and evalue, and nbclient with allow_errors=False keeps going. So check_review's `error_line()` and its check that the error text appears in the Answer keep working. Its regex also strips the SyntaxError suffix ' (<string>, line N)'.
  - Evidence: tbtest/t.py and t2.py: for example ename='SyntaxError', evalue="invalid syntax... (<run_code>, line 3)", and the last cell printed 'reached end'.
  - Impact: The output checks in check_review can stay as they are, as long as the wrapper keeps reporting errors this way.
- **F6** [verified]: The basic catching `run_code` adds noise to tracebacks: a frame for run_code itself and 'File <string>:2 ... Could not get source'. `tb_offset=1` did not remove them. A variant fixes this: register the code in linecache under '<run_code>' and call `showtraceback((etype, value, tb.tb_next))`. Its traceback starts at the student's line, like a normal cell.
  - Evidence: tbtest/t.py output (noisy) compared with tbtest/t2.py output, which starts with 'File <run_code>:2 ----> 2 outer('hi')'.
  - Impact: This matters for ch03 Q14, whose answer is about the order of frames in the traceback. The helper should use the clean variant.
- **F7** [verified]: Passing code through `exec`/`run_code` loses the notebook's display of the last expression. Two questions depend on that display: ch02 Q4 (`price * 3` shows `12`) and ch03 Q9 (`greet` shows `<function __main__.greet()>`). check_review does not check execute_result outputs today; it checks only stdout and errors.
  - Evidence: `exec('price = 4\nprice * 3')` displays nothing. The executed copies show execute_result '12' and '<function __main__.greet()>'. check_review.py L102-104 reads only stream stdout and error outputs.
  - Impact: With option B (question code stored in a string and run with `run_code(qvar)`), these two questions break unless the helper reproduces the last-expression display. With option A (code copied into a plain answer cell) they keep working. A new check for execute_result would close the existing gap.
- **F8** [verified]: ch07 Q14's doctest report is identical whether the code runs as a plain cell or through `exec`, including 'File "__main__", line 9, in count_e'.
  - Evidence: tbtest/t3.py printed the same 8-line output for both.
  - Impact: Doctest questions do not limit which DRY option can be used.
- **F9** [verified]: check_review.groups_of (L53) and turtle_images.questions (L46) start a new group only at '### ' and end it only at '# ' or '## '. A '#### Answer' cell matches neither, so it stays inside its question's group. The closing credit cell ('*Summary and questions by…*') is the last cell on every page and already falls inside the last question's group.
  - Evidence: Python: '#### Answer'.startswith('### ') is False, and so is startswith(('# ','## ')). The credit cell is the last cell on all six pages.
  - Impact: Grouping can stay as it is. But in Colab a collapsed last '#### Answer' would also hide the credit cell, and a prep step that merges 'everything up to the next heading' would pull the credit line into the last answer. The pages need something that ends the last answer, such as a heading or a tag.
- **F10** [verified]: `is_answer` (check_review L49, turtle_images L42) matches one markdown cell by its `<details><summary>Answer</summary>` prefix. Three places use it: check_review L98 (`answers`, which supplies the ```text blocks), L129 (question text = markdown cells that are not answers, used to count examples and find headers) and L142 (the 'no Answer cell' check), plus turtle_images L99 (runs the answer's python blocks before drawing).
  - Evidence: Read the source of both tools.
  - Impact: With heading sections, `is_answer` has to work by position (every cell after '#### Answer' in the group), not cell by cell. Otherwise the answer's ```text blocks would count as examples in the question text, which silently weakens the check that write-code questions show at least 2 examples.
- **F11** [verified]: Jupyter Book shows '#### Answer' headings as 'Answer' entries in the right-hand page table of contents, under each question. Repeated 'Answer' headings produce no WARNING or ERROR. A MyST `:::{admonition}` opened in one markdown cell cannot contain later cells: it closes at the end of that cell, the code cell and the next markdown render outside it, and the stray ':::' becomes an empty div.
  - Evidence: I built a small book in scratchpad/ultra/repo-map/jbtest: the page TOC read 'Question 1… | Answer | Question 2… | Answer', the build exited 0 with no warnings, and the HTML showed the admonition closing after 'opened here'.
  - Impact: prep_notebooks has to merge the heading, its markdown and its code cells into one dropdown markdown cell (code turned into ```python blocks, or dropped). Leaving the heading in pollutes the page TOC, and splitting the dropdown across cells leaves the answer visible.
- **F12** [verified]: The website does not run review pages. Jupyter Book execution is off (`execute_notebooks: 'off'` in _config.yml). execute_notebooks.py only globs 'chap*.ipynb' in jb/ and never looks at jb/yr/. process_review drops '# Your code here' cells, wraps data-turtle images in a div, converts every whole-cell <details> to a dropdown (`DETAILS.fullmatch`), then calls process_cell. process_cell blanks code that starts with '# Solution' or is tagged 'solution', and strips only %%expect.
  - Evidence: jb/_config.yml, jb/execute_notebooks.py L139, jb/prep_notebooks.py L62-83 and L139-170.
  - Impact: Answer code cells would show on the website as unrun code outside any dropdown unless prep handles them. Never tag answer cells 'solution' (prep would blank them). A custom cell magic would show its %% line on the site unless prep strips it.
- **F13** [verified]: turtle_images decides what to draw like this: the nearest ```python block above the img tag in the same cell, otherwise the last code cell above it (`last_code`, L104-118). It runs each question's code cells in order before reaching the pictures. Four answer pictures are drawn from the question's code cell this way: ch04 Q2, Q6, Q7 and ch05 Q17. ch04 Q14's example pictures need the `polygon` definition cell to run first. There are 23 data-turtle pictures in all: 22 in ch04 and 1 in ch05.
  - Evidence: Read turtle_images.py. analyze.py shows ANSWER(img=1) for ch04 Q2, Q6, Q7 and ch05 Q17, and the count script shows 22 and 1 pictures.
  - Impact: In the answer section, put the run cell before the markdown that holds the picture, or `last_code` points at the wrong cell. Definition cells must stay code cells. With option B, `last_code` would be 'run_code(q2)': the 'make_turtle(' check at L121 would give a false warning, but the picture would still be right.
- **F14** [believed]: If `run_code` calls `get_ipython()` without checking it exists, it breaks outside IPython. turtle_images runs code with plain exec, where get_ipython is undefined: the except branch would raise NameError, turtle_images' `run()` would catch it, and it would print 'raised NameError: get_ipython'. The picture would still be drawn up to that point.
  - Evidence: turtle_images.run L61-69 catches Exception. get_ipython is defined only inside IPython.
  - Impact: The helper should fall back (re-raise or print the traceback) when get_ipython is missing, so turtle_images and standalone runs stay quiet.
- **F15** [verified]: In every write-code question, the examples that call the student's function are markdown only. The only code cell in those questions is '# Your code here'. 30 of the 34 show a function header (ch02 Q11, Q12, Q16 and Q17 are tagged no-signature). All show at least 2 examples with output, as ```text blocks or turtle pictures; ch04 Q12 also shows a help() text example.
  - Evidence: analyze.py shows write-code groups as [md, YOURCODE, ANSWER]; the header/example script shows ex 'TT'/'II'/'IIT'/'III' and the headers found.
  - Impact: Run all never calls an undefined student function, so these questions need no structural change. Only a student's own broken code could stop Run all.
- **F16** [strong-evidence]: Each question uses only names defined in its own cells or the setup cell. The only exception is ch04 Q7's `jupyturtle`, which is meant to be undefined (the NameError is the answer). Three answers are NameErrors that depend on nothing earlier defining the name: ch03 Q10a `total`, ch07 Q8 `num_letters`, ch04 Q7 `jupyturtle`.
  - Evidence: Static analysis with ast of each group's code cells, including the code inside run_code strings, against the names its own cells and setup define. The whole-page run in check_review passes.
  - Impact: Answer run cells can run in page order under Run all. Keep them self-contained so the NameError answers hold.
- **F17** [verified]: The setup cells print text on first run only: ch04 and ch05 print 'Downloaded jupyturtle.py', and ch07 prints 'Downloaded words.txt' (seen in the executed copy). The ch02, ch03 and ch06 setup cells print nothing. None of this gives an answer away.
  - Evidence: Executed ch07 setup output 'Downloaded words.txt'. The setup source has `print("Downloaded " + str(local))` inside `if not exists(filename)`.
  - Impact: No change needed. A check that 'nothing outside an answer has output' must exempt the setup cell.
- **F18** [verified]: `review_cells.py` builds the old format. parse_spec (L77-93) turns '%%% answer' into a single `<details>` markdown cell and '%%% code' into a code cell. The skeleton (L137-176) has no `run_code` and ends with the credit cell. The notebook metadata it writes (L188) has only kernelspec and language_info. QUESTION, question_starts, list, renumber and add (which inserts before the credit cell) do not depend on the answer format.
  - Evidence: Read review_cells.py.
  - Impact: These need to change: the 'answer' kind (emit a '#### Answer' heading, markdown and run cell(s); for option A, generate the run cell from the question's ```python block), a new kind for question code, the skeleton's setup helper and credit-cell ending, and metadata that saves answers collapsed. Probably also a 'sync' command to regenerate the run cells.
- **F19** [verified]: A notebook saved by Colab keeps notebook metadata `colab.collapsed_sections` (a list) and stores each cell's id in `metadata.id`, not in the nbformat 4.5 top-level `id`.
  - Evidence: googlecolab/colabtools notebooks/colab-github-demo.ipynb has metadata {"colab": {"collapsed_sections": [], ...}} and cell metadata {'colab_type': 'text', 'id': '-pVhOfzLx9us'}. tensorflow/docs beginner.ipynb also has cell metadata.id.
  - Impact: Saving answers collapsed probably means writing `colab.collapsed_sections` with ids Colab recognises (maybe `metadata.id`) and `jp-MarkdownHeadingCollapsed` for JupyterLab. check_notebooks checks neither, and review_cells' fresh_id sets only the top-level id. Which ids Colab accepts is still unknown.
- **F20** [verified]: `check_notebooks.py` checks things that still matter: valid JSON, nbformat 4, unique cell ids, no stored outputs in code cells, an outputs key, `KNOWN_MAGICS` = {%%expect, %%add_method_to, %%expect_error}, exact '# Solution goes here' cells, every yr page in the TOC, and the workflow line 'cp yr/*.ipynb jb/yr/'. It does not look at headings or notebook metadata.
  - Evidence: Read check_notebooks.py L18, L28-76 and L79-119.
  - Impact: The heading design needs no change here as long as notebooks are saved without outputs. A custom cell magic would have to be added to KNOWN_MAGICS. New lints could be added, e.g. answer headings present and collapsed.
- **F21** [verified]: build_book.sh and deploy-book.yml only copy yr/*.ipynb into jb/yr/ and run prep_notebooks.py. known_warnings.txt has 4 entries, none from yr/ pages.
  - Evidence: Read both files; `grep -i yr/` on known_warnings.txt finds nothing.
  - Impact: No change unless new helper files are added. Any new Sphinx warning from a review page will show up as NEW.
- **F22** [verified]: The documentation that describes the current format and would need rewording: yr/README.md (Layout item 3, Answers, Cell conventions for collapsible sections, turtle pictures, raises-exception and run_code, Tools, and the review.sh check list), yr-review-page SKILL.md, yr-review-questions SKILL.md (its rules and the '%%% answer' spec example), notebook-conventions SKILL.md L86 (mentions the `<details>` answer format), and run_notebooks.sh L11 (comment only). The question text on the pages also says 'then run it to check', 'Run this cell to define', 'For each of the next three cells', and each intro explains run_code.
  - Evidence: grep across the repo plus a scan of question markdown for wording about cells.
  - Impact: Text edits on all six pages and in the docs and skills.
- **F23** [verified]: In check_review, the EXAMPLE regex (`python block .*? closing fence, then text block or img`, with re.S) can stretch across several blocks. Today the header block merges into the first example, so example counts come out right. If question code moves into the question markdown, a question block that is later followed by a ```text block in the same question text would also count as an example.
  - Evidence: The regex at check_review L40, and the counts from the example script (e.g. 'TT' for questions with a header plus 2 examples).
  - Impact: For option A, the example count should skip the question-code blocks, e.g. by marking them. Otherwise the check gets weaker.
- **F24** [verified]: Parts are checked one cell at a time: each code cell's whole stdout must equal exactly one ```text block in the Answer. Eight questions have parts: ch02 Q9 (a-e), Q10 (a-c), Q14 (a,b); ch03 Q10 (a-c); ch04 Q14 (a-c), Q15 (a-c); ch05 Q8 (a-c).
  - Evidence: check_review L102-109 and L119-120 work per cell. The cell listings show **Part x** markdown cells between the code cells.
  - Impact: Keep one run cell per part in the answer. Putting several printing parts in one cell would fail the exact-match check unless the check changes.
- **F25** [verified]: ch04 particulars. Q14 parts a-c call `make_turtle()`, so each shows an empty canvas; part c (`polygon(-4, 20)`) is not tagged, shows an empty canvas and no error, and that is its answer. Q15 part c's message varies by Python version (the answer notes that versions before 3.13 omit "Did you mean 'sides'?"). Q7 starts 'Assume you have just restarted the notebook and run only the setup cell'. Q18's examples call `jump()`, which is defined only in the question markdown and the answer. The ch04 page is about 200 KB because of its 22 stored PNGs.
  - Evidence: Cell listings of chap04 cells 24-26, 45-62 and 69-71; the outputs in the executed copy; `ls -la jb/yr` (200614 bytes).
  - Impact: Q14's live canvases must move into the answer section. Version-dependent errors rely on the substring check. A drawing made live by Run all shows next to the stored PNG inside the answer.

## Open questions

- About the user's question on the 3rd and 4th research workers: this worker (repo-map) cannot see those runs or their errors, so the orchestrator has to look at their transcripts.
- Does Colab's Run all run cells inside collapsed heading sections? Most likely yes, but not verified (colab.research.google.com is not reachable from here).
- Which ids does Colab's `metadata.colab.collapsed_sections` hold: cell `metadata.id` values only, or also nbformat 4.5 top-level `id`s? Does Colab respect it when opening a notebook from GitHub? Does Colab's collapsed-heading view hide cell outputs too?
- Does Colab's editor lint or underline code in cell-magic cells or inside a collapsed section? This decides whether answer run cells can hold raw code with syntax errors. They would still need a catching wrapper for Run all, since a SyntaxError cannot be caught in the same cell.
- How should the website show answer code cells: drop them (option A, where they duplicate the question's markdown code) or turn them into ```python blocks inside the dropdown? And what ends the last answer section so the credit cell is not absorbed: a '## ' heading, a tag, or moving the credit line?
- For option A, how are question-code ```python blocks told apart from header and example blocks (a fence info string, an HTML comment, or position), both for the DRY check and so EXAMPLE does not overcount?
