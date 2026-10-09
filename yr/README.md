# yr/ — Prof. Rosenthal's course additions

This folder holds material written for Prof. Rosenthal's classes that is **not** part of
Allen Downey's *Think Python*. Keeping it here, instead of inside the chapter notebooks, means:

- the original chapters, their numbering and their exercises are unchanged;
- `chapters/` stays close to upstream, so syncing with AllenDowney/ThinkPython rarely conflicts;
- it is always clear which material is the book and which is the course's.

```
yr/
  README.md                this file: layout, format, style rules, tools
  chapNN_review.ipynb      one review page per chapter (so far: chapters 2, 3, 4, 5, 6, 7)
  plans/                   design notes (runall-collapsible-answers.md: the new page format)
  tools/
    review_cells.py        create a page skeleton; add, list, number, renumber questions
    review.sh sync NB      write everything that can be derived, by running the code
    review.sh check NB     verify the page (fails if sync would change anything)
    review.sh normalize NB repair a page that was saved in Colab
    review.sh selftest     prove that sync and check catch broken pages
    review.sh images NB    old-format pages only: draw the turtle pictures
    review_format.py       the page format (used by all the tools and by jb/prep_notebooks.py)
    sync_review.py, check_review.py, selftest_review.py, selftest/   (used by review.sh)
    ensure_colab_venv.sh, colablike.lock   the pinned Colab-like kernel
    legacy_check_review.py, turtle_images.py   old-format pages (until all pages are converted)
    verify_site.py         check a converted page on the built website
```

Claude Code skills that use all this: `yr-review-page` (create a page or write its concept
summary) and `yr-review-questions` (add or revise questions).

**Two formats, for now.** The pages are moving to a new format, one page at a time
(`yr/plans/runall-collapsible-answers.md`, section 8). In the new format, Colab's **Run all** works, and
the answers stay hidden until a student opens them. A page is in the new format if its Answers are
`#### Answer` headings; it is in the old format if its Answers are `<details>` blocks. The tools
work on both. This file describes the new format first; see "Old format" for pages that are not
converted yet.

## Adding a question: a guide for people

This guide is for pages in the new format. For each kind of question, it tells you what to type.
The tools write everything else. You can also ask Claude: the `yr-review-questions` skill follows
these rules.

**The rule: type each fact once.** You type the question's code, the solutions, the example calls,
the fixes and the explanation. You do not type outputs, error names, values, function headers,
import lines or pictures. `review.sh sync` runs the code and writes them. `review.sh check` fails if
something that sync writes was typed or edited by hand.

**The workflow, for every kind:**

1. Get the number: `python3 yr/tools/review_cells.py next yr/chapNN_review.ipynb --before 4` prints
   `3b` (a new question between Questions 3 and 4). At the end of the page, omit `--before`.
   Numbers stay fixed during a semester.
2. Write the cells in a spec file (the examples below), then
   `python3 yr/tools/review_cells.py add yr/chapNN_review.ipynb SPEC --before 4`.
   Or edit the notebook in Jupyter (not in Colab: see "If you edit a page in Colab").
3. `yr/tools/review.sh sync yr/chapNN_review.ipynb`. Read its report: it prints each new output and
   value. If an output that was already on the page changes, sync shows the difference and does not
   write it. Read the Answer's text again; if it is still right, run sync again with `--accept`.
4. `yr/tools/review.sh check yr/chapNN_review.ipynb` must print OK.
5. `python3 .claude/skills/check-notebooks/check_notebooks.py`, then
   `.claude/skills/build-book/build_book.sh`, and look at the page.

**What is displayed / drawn / happens.** Type the prompt, the code in a `~~~python` block (a *run
block*: tildes, not backticks), and the explanation. Write each value in the explanation as an
expression with a marker, and type `?` as the value:

````
%%% markdown
### Question 3b (easy): what is displayed?

Predict what this code displays, then open the Answer to check.
%%% run
minutes = 135
print(minutes // 60, minutes % 60)
%%% answer
135 minutes is 2 hours (`135 // 60` is <!--=-->`?`) and `135 % 60` is <!--=-->`?` minutes left over.
````

Sync adds a hidden *run cell* under the Answer heading that shows the code's real output, and
replaces each `?` with the value of the expression before it.

**Find the error, in parts.** Use one run block per part (`%%% run a`, `%%% run b`, ...) and one
Answer cell per part (`%%% part a`). Name each error with `<!--=error-->`:

````
%%% run a
x = 5
if x = 5:
    print('five')
%%% run b
print(undefined_name)
%%% answer
%%% part a
`=` assigns; comparing needs `==`, so this is a <!--=error-->`?`.
%%% part b
The name was never assigned: a <!--=error-->`?`.
%%% markdown
Python finds a syntax error before it runs any of that part's code.
````

Sync writes each part's output (the traceback, as text) after the part's explanation. A last
markdown cell is the summary. Colab's editor does not underline the mistakes, because the
question's code is text, and Run all does not stop at them.

**Write a function.** Type the prompt, the example calls after a `**Examples**` line, and the
solution in the Answer. Do not type the header, the example outputs or import lines:

````
%%% markdown
### Question 9 (medium): write a function

Write a function called `end_hour` that takes `start` and `duration` and displays the hour
when the event ends, on a 24-hour clock.

**Examples**

```python
end_hour(9, 3)
end_hour(22, 5)
```

```python
end_hour(20, 28)
```
%%% placeholder
%%% answer
```python
def end_hour(start, duration):
    print((start + duration) % 24)
```
````

Sync writes "Start from this header" above the examples, the output (or picture) of each example,
the import lines of each Answer block, and a "Then try:" line. Every ```` ```python ```` block in the
Answer is a solution: check runs each one against every example. Mark a block that is not a full
solution (for example, a halfway version) with `<!-- not a solution -->` on the line above it;
sync then writes its output under it. To show a different header, write `<!-- header: f g -->`.

**Write code without a function.** As above, but the examples assign the input variables, and the
`# Your code here` cell is tagged `no-signature` (`%%% placeholder no-signature`). The solution is
only the computation; sync runs each example's assignments, then the solution.

**A helper the question provides.** Put it in a definition cell (`%%% code`): a code cell that only
defines functions or assigns values. Sync writes "Run this cell to define `square`." above it. A
later question that uses `square` gets "This question uses `square` from Question 11." Type a
helper only once, where it is first provided.

**A fix or a "what if".** In the Answer, write a short ```` ```python ```` block: only the changed
lines (they run after the question's code), or only the new `def` (the question's own calls run
after it). Sync writes its output or picture under it. A fix that uses a name that a later question
assigns keeps its own input line (`price = 4`), because after Run all the name has the later value.
To show the whole question's code with one change, write
`<!-- derive: from=Q14 replace="for letter in word:" with="for letter in word.lower():" -->` and an
empty ```` ```python ```` block under it; sync fills the block.

**After Run all, a student can copy any Answer block into a new cell and run it.** So Answer blocks
have no example calls, no example inputs and no provided helpers; sync writes their imports.

## Review pages: `yr/chapNN_review.ipynb`

One notebook per chapter, titled `NNb. Prof. Rosenthal's Review` (e.g. `4b.` for chapter 4).

### Where it appears

- **Website:** right after its chapter in the sidebar, as "4b. Prof. Rosenthal's Review".
  The previous/next buttons go 4 → 4b → 5. The book's chapter and section numbers do not change.
- **Colab:** each page has a "Run this page on Colab" link at the top, and `jb/index.md` lists
  it under its chapter. (The links point at `v3`, so they work once the page is merged there.)

### Layout of a page (new format)

Sync writes the cells marked *(template)*; do not edit them.

1. **Title cell** *(template)*: `# NNb. Prof. Rosenthal's Review`, a link to the chapter, how to use
   the page, and the Colab link. Sync keeps the chapter title that is in the link.
2. **`## Concepts covered`**, with two collapsible lists, shown by default:
   - **Python Syntax and Semantics**: what the chapter teaches about Python itself.
   - **Definitions, etc.**: the definitions (each bullet starts with `DEFINITION:`), then
     "Other ideas" (programming practices and other concepts that are not syntax).
   Values in these lists can use markers too.
3. **`## Questions`**: a short introduction (e.g. what the turtle functions do). Then the help note
   *(template; not shown on the website)*, the setup code cell (tagged `setup`), and the helper cell
   "Helper for the Answers" *(template; tagged `setup`, code hidden; it defines `run_code`)*.
4. The questions, `### Question N (easy|medium|hard): <kind>`, ordered easy → hard. Each has its
   prompt, its run blocks or examples, its definition cells or `# Your code here` cell, and the
   `#### Answer` heading, saved closed. **Question numbers stay fixed during a semester**
   (homework is assigned by number): a question inserted between Questions 3 and 4 is numbered
   **3b** (then 3c, ...), and no other number changes. Renumber 1, 2, 3, ... only when starting a new
   semester (`review_cells.py renumber`).
5. **`## Credits`** *(template)*; the website does not show the heading.

### Style rules

These come from Prof. Rosenthal's instructions; follow them for every page.

**Concepts covered**

- It is a review checklist for someone who already studied the chapter. Read top to bottom, it
  should read like an instruction manual: a complete list of the facts covered, with
  little or no explanation.
- Plain English with minimal notation. No arrows or symbols as shorthand.
- Keep the lists short. Highlight the Python syntax in the most straightforward way: show the
  general form with UPPERCASE placeholders, say what it does in one sentence, then give an
  example. For instance:

  ````
  - This repeats the indented code SOME_INTEGER times:
    ```
    for i in range(SOME_INTEGER):
        SOME_CODE
        SOME_MORE_CODE
    ```
    For example, this prints `hello` three times:
    ```python
    for i in range(3):
        print('hello')
    ```
  ````

  One-line forms can stay inline: "`import MODULE_NAME` makes a module's functions available as
  `MODULE_NAME.FUNCTION_NAME(...)`. For example, after `import jupyturtle` you can call
  `jupyturtle.forward(100)`."
- Facts only. An example is not a fact: "a loop that runs `forward(50)` and `left(90)` four times
  draws a square" does not belong in the list (it may appear as an example of a fact).
- State the underlying rule, e.g. "`range(SOME_INTEGER)` is shorthand for the integers `0, 1, 2, ...`
  up to SOME_INTEGER minus 1".
- **Python Syntax and Semantics** holds the facts about Python syntax and behavior, including
  the modules and functions the chapter uses. Group them under short bold labels.
- **Definitions, etc.** holds definitions, each bullet starting with `DEFINITION: **term** is ...`,
  and then any other conceptual facts under **Other ideas**.
- Leave out facts that are not about Python or programming (e.g. "a circle can be approximated
  by a polygon with many sides", or what the turtle looks like).
- Facts the questions rely on belong here too, even if the chapter only implies them
  (e.g. "`range(-4)` produces no values").

**Questions**

- Focus on code, not definitions. Mostly two kinds:
  - **what is displayed / drawn / happens?**: code to predict, then the Answer shows its output;
  - **write code**: write a function, or refactor given code.
  A few other kinds are fine (find the bug, write a docstring, which call is wrong...).
- A mix of easy, medium and hard, ordered easy → hard. The level is in the heading.
- **Each question must make sense to someone who never saw Think Python.** These questions may be
  reused in other materials. So: no references to the book, its sections or its examples
  ("like `circle` in the chapter"); give any helper function a question uses (a definition cell,
  or a pointer to the question that defines it); introduce any module the page uses (e.g.
  `jupyturtle`) at the top of the Questions section.
- **Write-code questions give the function header** of each function to write. In the new format,
  sync writes it ("Start from this header (replace `...` with the body):"). Exception: a question
  whose point is writing the header itself; tag its `# Your code here` cell `no-signature`.
- **Write-code questions show at least two examples**, each with its output (sync writes it).
- **Questions about wrong calls** (predict the error) first show the function being used
  correctly in at least two ways, each with its output ("Two correct ways to call it:"). In the new
  format, these are ```` ```python ```` blocks in the prompt; sync writes their output.
- Put the main point about the *Python* first. Side remarks about the context of an example go
  last, in a paragraph that starts "**By the way:**".

**Answers**

- Each question ends with an Answer that is closed until the student opens it. For "what is
  displayed" questions, the Answer shows the real output (written by sync), then a short
  explanation. For drawings, the picture.
- Give more than one approach when there is more than one reasonable one.
- **New format: a student can copy any ```` ```python ```` block of an Answer into a new cell after
  Run all and run it.** The block has its own import lines (sync writes them), and uses the helpers
  that the questions define; it has no example calls or example inputs.
- **Old format: every ```python block in an answer must run unchanged when pasted into a new .py
  file**: it includes its imports, every helper function it uses, and a call that shows it working.

### Markers (new format)

Markers are HTML comments: Colab, Jupyter and GitHub do not show them, and the website build
removes them. Type `?` as a value; sync replaces it.

| You type | Sync writes |
|---|---|
| `` `EXPR` is <!--=-->`?` `` | the value of the code span before the marker (on the same line) |
| `` <!--= EXPR -->`?` `` | the value of EXPR (statements before it are allowed: `<!--= import sys; sys.getrecursionlimit() -->`) |
| `` <!--=error-->`?` `` | the name of the error this part's code raises (in the summary: the error all parts raise) |
| `<!--do: CODE -->` | nothing: CODE runs (hidden) before the values that follow it in the same cell |
| `<!-- not a solution -->` | the output of the next ```` ```python ```` block (in a write-code Answer) |
| `<!-- header: f g -->` | "Start from this header" for these functions |
| `<!-- derive: from=QN replace="OLD" with="NEW" -->` | the next ```` ```python ```` block: Question N's code (its definition cells, then its run block) with OLD replaced by NEW; `from=solution`: this question's first solution. `\n` in OLD or NEW is a line break |

Values are computed after Run all and after the question's code (in Concepts: after the setup cell
only), with the value shown as a notebook shows it (`'abc'` with quotes, `4.0`).

- **A value marker never starts a line or a list item.** Colab then shows the line as raw HTML.
  Write "`-7 // 2` is <!--=-->`?`", not "<!--= -7 // 2 -->`?` is ...".
- A block marker (the last three) is alone on its line.

### What sync writes (new format)

- **Run cells**, one per run block, under the Answer heading (multi-part: after each part's
  explanation). The code is hidden; the title names the question ("Output of Question 8a"); the
  output is stored. A run cell whose code raises an error, or prints a line number, calls the
  page's `run_code` helper: it prints the traceback as text, so Run all does not stop and Colab
  shows no red marks.
- **Generated regions**, between `<!-- begin generated: KIND -->` and `<!-- end generated: KIND -->`
  lines: `header`, `example`, `output`, `then-try`, `uses`, `define`.
- **Import lines** at the top of Answer code blocks; the line `<!-- generated imports: N -->`
  above a block says that its first N lines are written by sync.
- **Values** in place of each `?`, and the template cells.
- **The stamp** (notebook metadata `yr_review`): the stack that wrote the outputs, and checksums
  that let check find hand edits.

Never edit what sync writes. Sync runs the code only on the pinned Colab-like kernel (Python 3.13,
IPython 7.34.0, ipykernel 6.17.1, as Colab; `yr/tools/ensure_colab_venv.sh`, which `review.sh`
calls), so that the stored outputs look like what students see.

### Format rules (new format; `review.sh check` enforces them)

1. Question headings are `### Question N (level): kind`; N is digits and an optional letter (`3b`),
   unique on the page.
2. Numbers are stable: every number of the published page (`v3`) stays on the same question, unless
   the page was renumbered between semesters. A question `Nb` may not exist while Question N has a
   part b.
3. One `#### Answer` heading per question, saved closed. No other headings in a question.
4. Run blocks (`~~~python`) only before the Answer; with two or more, `**Part a**`, `**Part b**`, ...
5. Code cells before the Answer: definition cells (define or assign only) and `# Your code here`.
6. Code cells in an Answer: only run cells.
7. In a question, a ```` ```text ```` block or a picture appears only inside a generated region.
8. Every error a run cell shows is named by `<!--=error-->` in its part's text or the summary; the
   text of a part names no other error.
9. Stored outputs only on run cells, as sync wrote them (the stamp matches).
10. Markers as in the table above; no `?` left.
11. Sync would change nothing.
12. Every Answer code block imports what it uses from the setup cell, runs after Run all, and shows
    what the page says; every solution gives every example's output; a doctest prints no failure.
13. A "NameError" answer stays true: no other cell assigns that name.
14. The page ends with the credits; tags only `setup`, `no-signature`, and `remove-cell` (help note).
15. Do not edit what sync writes, and do not save a page from Colab back to GitHub.
16. No `TODO` left. No `(c)`, `(r)`, `(tm)` or `+-` in the text: the website turns them into
    ©, ®, ™ and ±. For parts of a question write **Part a**, **Part b**, **Part c**.

Check also prints notes: names that more than one question assigns (a fix that uses one keeps its
own input line).

### If you edit a page in Colab

Colab adds metadata and outputs when it saves. Do not save to GitHub from Colab. If a page was saved
from Colab: `yr/tools/review.sh normalize NB` (removes what Colab added), then `review.sh sync NB`.
`check_notebooks.py` (also in CI) fails until the page is repaired.

### Turtle pictures (new format)

Sync draws them: the picture of a run cell's code, of an example, or of a fix. Example code should
start with `make_turtle()`. Pictures stay within the canvas: the turtle starts in the middle of a
300 × 150 canvas; use `jump(-x)` or `make_turtle(width=..., height=...)` to make room. Look at new
pictures on the built page.

### Tools

All run from the repository root.

```bash
python3 yr/tools/review_cells.py new 5 "Conditionals and Recursion"   # skeleton yr/chap05_review.ipynb
python3 yr/tools/review_cells.py list yr/chap04_review.ipynb
python3 yr/tools/review_cells.py next yr/chap04_review.ipynb [--before 7]  # the number for a new question
python3 yr/tools/review_cells.py add yr/chap04_review.ipynb spec.txt [--before 7]
python3 yr/tools/review_cells.py renumber yr/chap04_review.ipynb   # only between semesters
yr/tools/review.sh sync yr/chap04_review.ipynb [--accept]
yr/tools/review.sh check yr/chap04_review.ipynb [--static]
yr/tools/review.sh normalize yr/chap04_review.ipynb
yr/tools/review.sh selftest
yr/tools/review.sh images yr/chap04_review.ipynb                     # old format only
```

`review_cells.py add` takes a small text file of cells; run it without arguments for the format.
`review.sh check --static` runs only the rules that need no kernel (fast). `review.sh selftest`
syncs `tools/selftest/fixture.ipynb` (a page with every kind of question), checks it, and makes
sure that check catches 27 kinds of broken page; run it after any change to the tools.

The first `review.sh sync` or `check` creates the Colab-like kernel in `~/.venvs/colablike` (it
needs `uv`, which `review.sh` installs into the book's venv).

### Adding a review page for another chapter

Use the `yr-review-page` skill, or by hand:

1. `python3 yr/tools/review_cells.py new NN "Chapter title"` and fill it in, following the style rules.
2. `jb/_toc.yml`: split the numbered "Chapters" list after `chapNN` and put the review page in
   its own unnumbered part between the two halves (see how `yr/chap04_review` is listed).
   Numbering continues across numbered parts, so chapter numbers stay the same; a page in an
   unnumbered part shows its own title (`NNb. …`) without an added number.
3. `jb/index.md`: add a Colab line under the chapter.
4. `review.sh sync`, `review.sh check`, `python3 .claude/skills/check-notebooks/check_notebooks.py`,
   then `.claude/skills/build-book/build_book.sh` (no new warnings) and look at the page.

### How the build handles `yr/`

- `.github/workflows/deploy-book.yml` and `.claude/skills/build-book/build_book.sh` copy
  `yr/*.ipynb` into `jb/yr/` (gitignored) next to the chapter copies. Review pages are not run
  by the build: the website shows the outputs that sync stored.
- `jb/prep_notebooks.py` (`process_review`): on new-format pages, each Answer (its text and its run
  cells' stored outputs, without their code) becomes one closed dropdown; the helper cell and the
  "Credits" heading are dropped; markers are removed (values stay); tracebacks are shortened. On
  old-format pages, it converts the `<details>` cells to collapsible boxes. Both: the concept lists
  stay open, and `# Your code here` cells are dropped. The notebooks in `yr/` are never modified by
  the build.
- `yr/tools/verify_site.py jb/_build/html/yr/chapNN_review.html yr/chapNN_review.ipynb [BEFORE.html]`
  checks a converted page on the built site, and compares it with the page built before conversion.
- `check_notebooks.py` lints `yr/*.ipynb` (on new-format pages: outputs only on run cells, the
  stamp, the markers) and checks that each one is in the TOC and that the workflow copies `yr/`.

## Old format (pages not converted yet)

These rules apply to pages whose Answers are `<details>` blocks, until they are converted.

- **Collapsible sections** are markdown cells written as HTML `<details>`.
  - Answer (collapsed): `<details>` + `<summary>Answer</summary>`
  - Concept lists (shown by default): `<details open>` + `<summary><strong>Title</strong></summary>`

  Keep the blank lines after `<summary>…</summary>` and before `</details>`, or the markdown
  inside will not be rendered:

  ````
  <details>
  <summary>Answer</summary>

  ```text
  expected output
  ```

  Explanation, and/or ```python code blocks.

  </details>
  ````

- **The question's code** is a code cell; the Answer shows its exact output in a ```text block.
- **Write-code questions** type the header block and at least two examples with their outputs (a
  ```text block, or a turtle picture) by hand.
- **Turtle pictures**: write `<img data-turtle src="">` right after a ```python block (in a
  question's examples) or in an Answer (the picture of what the question's code cell draws). Then
  run `yr/tools/review.sh images yr/chapNN_review.ipynb`, which runs the code and stores each
  picture as a PNG. To draw an example that calls the function the student must write, the tool
  first runs the question's answer code and the question's code cells above the picture.
- **`# Your code here`**: a code cell whose entire source is this is space for the student's
  code in Colab. The website drops it.
- **Questions whose answer is an error**: tag the code cell `raises-exception`. Do **not** use
  `%%expect`: it would show the answer.
- **Errors an editor can see without running the code** (syntax errors, a name that is not defined,
  a call with missing, extra, misnamed or wrongly typed arguments, an unknown module): put such code
  in a string run by `run_code` (defined in the setup cell), for every part of the question:

  ````
  run_code("""
  x = 5
  if x = 5:
      print('five')
  """)
  ````

  `review.sh check` fails if a syntax error is not inside `run_code`. To find the other cases, run
  Pyright on each code cell together with the cells above it.
- **Setup cell**: tag it `setup`. It runs before every picture and in the checks.
- No stored outputs; every cell has a unique 8-hex-digit id (`review_cells.py` takes care of this).

`review.sh check` (through `legacy_check_review.py`) runs the page and fails if: a cell raises
without the `raises-exception` tag; a question's printed output or error is not shown exactly in
its Answer; a syntax error is not inside `run_code`; an answer's ```python block does not run as a
standalone .py file; a write-code question lacks the function header or has fewer than two examples
with output; a wrong-call question shows fewer than two correct calls; a turtle picture is missing;
or the text contains `(c)`-style symbols.

## Other course additions outside this folder

These came earlier and live elsewhere because the tooling expects them there:

- `solutions/`: suggested solutions to the book's own exercises (chapters 4 and 5), shown on
  the site behind "Suggested solution" dropdowns.
- `.claude/skills/`: Claude Code skills for building, checking, deploying and syncing the book
  (they must stay in `.claude/`).
- Cells tagged `course` in `chapters/`: any course-specific edits made directly in a chapter
  (see the `notebook-conventions` skill). Prefer putting new material in `yr/` instead.
