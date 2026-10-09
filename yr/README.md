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
  tools/
    review_cells.py        create a page skeleton; add, list, renumber questions
    review.sh images NB    draw the turtle pictures by running the code
    review.sh check NB     run the page and verify every question and answer
    turtle_images.py, check_review.py   (used by review.sh)
```

Claude Code skills that use all this: `yr-review-page` (create a page or write its concept
summary) and `yr-review-questions` (add or revise questions).

## Review pages: `yr/chapNN_review.ipynb`

One notebook per chapter, titled `NNb. Prof. Rosenthal's Review` (e.g. `4b.` for chapter 4).

### Where it appears

- **Website:** right after its chapter in the sidebar, as "4b. Prof. Rosenthal's Review".
  The previous/next buttons go 4 → 4b → 5. The book's chapter and section numbers do not change.
- **Colab:** each page has a "Run this page on Colab" link at the top, and `jb/index.md` lists
  it under its chapter. (The links point at `v3`, so they work once the page is merged there.)

### Layout of a page

1. **Title cell**: `# NNb. Prof. Rosenthal's Review`, a link to the chapter on the website, how
   to use the page, and the Colab link.
2. **`## Concepts covered`**, with two collapsible lists, shown by default:
   - **Python Syntax and Semantics**: what the chapter teaches about Python itself.
   - **Definitions, etc.**: the definitions (each bullet starts with `DEFINITION:`), then
     "Other ideas" (programming practices and other concepts that are not syntax).
3. **`## Questions`**: a short introduction (e.g. what the turtle functions do), the setup code
   cell (tagged `setup`), then `### Question N (easy|medium|hard): <kind>`, ordered easy → hard,
   each followed by its collapsible Answer.
   **Question numbers stay fixed during a semester** (homework is assigned by number): a question
   inserted between Questions 3 and 4 is numbered **3b** (then 3c, ...), and no other number
   changes. Renumber 1, 2, 3, ... only when starting a new semester (`review_cells.py renumber`).
4. A short credit line at the end.

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
  - **what is displayed / drawn / happens?**: a code cell to predict and then run;
  - **write code**: write a function, or refactor given code.
  A few other kinds are fine (find the bug, write a docstring, which call is wrong...).
- A mix of easy, medium and hard, ordered easy → hard. The level is in the heading.
- **Each question must make sense to someone who never saw Think Python.** These questions may be
  reused in other materials. So: no references to the book, its sections or its examples
  ("like `circle` in the chapter"); show any helper function a question uses, in the question
  itself; introduce any module the page uses (e.g. `jupyturtle`) at the top of the Questions section.
- **Write-code questions give the function header** of each function to write, as a ```python
  block with `...` as the body (e.g. `def spiral(n, length, angle, increase):` / `    ...`),
  introduced with "Start from this header (replace `...` with the body):". Exception: a question
  whose point is writing the header itself; tag its `# Your code here` cell `no-signature`.
- **Write-code questions show at least two examples**: a ```python block calling the function,
  each followed by its output: a ```text block, or a turtle picture.
- **Questions about wrong calls** (predict the error) first show the function being used
  correctly in at least two ways, each with its output ("Two correct ways to call it:").
- Put the main point about the *Python* first. Side remarks about the context of an example go
  last, in a paragraph that starts "**By the way:**".

**Answers**

- Each question ends with a collapsible Answer. For "what is displayed" questions, show the exact
  output in a ```text block, then a short explanation. For drawings, show the picture.
- Give more than one approach when there is more than one reasonable one.
- **Every ```python block in an answer must run unchanged when pasted into a new .py file**: it
  includes its imports, every helper function it uses, and a call that shows it working.
  (Turtle code also needs `jupyturtle.py` in the same folder, and shows its drawing only in
  Jupyter or Colab.)

### Cell conventions

- **Collapsible sections** are markdown cells written as HTML `<details>`, so they work in Colab
  and Jupyter too. `jb/prep_notebooks.py` turns them into the site's collapsible boxes.
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

- **Turtle pictures**: write `<img data-turtle src="">` right after a ```python block (in a
  question's examples) or in an Answer (the picture of what the question's code cell draws). Then
  run `yr/tools/review.sh images yr/chapNN_review.ipynb`, which runs the code and stores each
  picture in the notebook as a PNG, so it shows in Colab, Jupyter and on the website. To draw an
  example that calls the function the student must write, the tool first runs the question's
  answer code and the question's code cells above the picture. Example code should start with
  `make_turtle()`. Pictures stay within the canvas:
  the turtle starts in the middle of a 300 × 150 canvas; use `jump(-x)` or
  `make_turtle(width=..., height=...)` to make room.
- **`# Your code here`**: a code cell whose entire source is this is space for the student's
  code in Colab. The website drops it.
- **Questions whose answer is an error**: tag the code cell `raises-exception`. Students see the
  error when they run the cell, and the checks still run the page top to bottom. Do **not** use
  `%%expect`: it would show the answer.
- **Errors an editor can see without running the code** (syntax errors, a name that is not defined,
  a call with missing, extra, misnamed or wrongly typed arguments, an unknown module): Colab's editor
  checks code as you type and underlines these, which gives the answer away. Put such code in a
  string run by `run_code`, which the setup cell defines (`exec(code, globals())`, with a docstring
  saying why):

  ````
  run_code("""
  x = 5
  if x = 5:
      print('five')
  """)
  ````

  Do the same for every part of the question, including parts with no error, so the cells don't
  hint which ones are wrong, and say in the introduction of the Questions section what `run_code`
  is for (see `chap05_review.ipynb`). `review.sh check` fails if a syntax error is not inside
  `run_code`. To find the other cases, run Pyright (the checker Colab's editor is based on) on
  each code cell together with the cells above it; errors it reports, other than "unknown import
  symbol" for `jupyturtle`, give the answer away. Runtime errors such as `ZeroDivisionError` or
  `RecursionError` are not visible to the editor and can stay as normal code.
- **Setup cell**: tag it `setup`. It runs before every picture and in the checks.
- **Avoid text the website turns into symbols**: `(c)`, `(r)`, `(tm)` and `+-` become ©, ®, ™
  and ±. For parts of a question write **Part a**, **Part b**, **Part c**.
- No stored outputs; every cell has a unique 8-hex-digit id (`review_cells.py` takes care of this).

### Tools

All run from the repository root.

```bash
python3 yr/tools/review_cells.py new 5 "Conditionals and Recursion"   # skeleton yr/chap05_review.ipynb
python3 yr/tools/review_cells.py list yr/chap04_review.ipynb
python3 yr/tools/review_cells.py add yr/chap04_review.ipynb spec.txt [--before 7]
python3 yr/tools/review_cells.py renumber yr/chap04_review.ipynb   # only between semesters
yr/tools/review.sh images yr/chap04_review.ipynb
yr/tools/review.sh check yr/chap04_review.ipynb
```

`review_cells.py add` takes a small text file of cells (`%%% markdown`, `%%% code [tags]`,
`%%% placeholder`, `%%% answer`); run it without arguments for the format.

`review.sh check` runs the page in Jupyter and fails if: a cell raises without the
`raises-exception` tag; a question's printed output or error is not shown exactly in its
Answer; a syntax error is not inside `run_code`; an answer's ```python block does not run as a standalone .py file; a write-code question
lacks the function header or has fewer than two examples with output; a wrong-call question
shows fewer than two correct calls; a turtle picture is missing; or the text contains
`(c)`-style symbols.

### Adding a review page for another chapter

Use the `yr-review-page` skill, or by hand:

1. `python3 yr/tools/review_cells.py new NN "Chapter title"` and fill it in, following the style rules.
2. `jb/_toc.yml`: split the numbered "Chapters" list after `chapNN` and put the review page in
   its own unnumbered part between the two halves (see how `yr/chap04_review` is listed).
   Numbering continues across numbered parts, so chapter numbers stay the same; a page in an
   unnumbered part shows its own title (`NNb. …`) without an added number.
3. `jb/index.md`: add a Colab line under the chapter.
4. `review.sh images`, `review.sh check`, `python3 .claude/skills/check-notebooks/check_notebooks.py`,
   then `.claude/skills/build-book/build_book.sh` (no new warnings) and look at the page.

### How the build handles `yr/`

- `.github/workflows/deploy-book.yml` and `.claude/skills/build-book/build_book.sh` copy
  `yr/*.ipynb` into `jb/yr/` (gitignored) next to the chapter copies.
- `jb/prep_notebooks.py` (`process_review`) converts the `<details>` cells to collapsible boxes
  and drops `# Your code here` cells. The notebooks in `yr/` are never modified by the build.
- `check_notebooks.py` lints `yr/*.ipynb` and checks that each one is in the TOC and that the
  workflow copies `yr/`.

## Other course additions outside this folder

These came earlier and live elsewhere because the tooling expects them there:

- `solutions/`: suggested solutions to the book's own exercises (chapters 4 and 5), shown on
  the site behind "Suggested solution" dropdowns.
- `.claude/skills/`: Claude Code skills for building, checking, deploying and syncing the book
  (they must stay in `.claude/`).
- Cells tagged `course` in `chapters/`: any course-specific edits made directly in a chapter
  (see the `notebook-conventions` skill). Prefer putting new material in `yr/` instead.
