---
name: yr-review-questions
description: Add, revise or check practice questions (with collapsible answers, examples and turtle pictures) on a "Prof. Rosenthal's Review" page in yr/chapNN_review.ipynb, and verify every answer by running it. Use when asked to add/write/change/fix review questions, exercises, quiz or practice problems for a chapter's review page, or to check a review page's answers.
user-invocable: true
argument-hint: [chapter number] [how many / what topics]
---

# Add or revise review questions

Read `yr/README.md` first (format, **style rules**, cell conventions, tools), and look at a few
questions in `yr/chap04_review.ipynb` as models. If the chapter has no review page yet, use the
`yr-review-page` skill instead. Work on a topic branch, not `v3`.

## The rules that matter most

- **Focus on code.** Mostly "what is displayed / drawn / happens?" (code cell, then Answer with
  the exact output) and "write code" (task, examples, `# Your code here` cell, Answer).
- **Standalone.** Each question must make sense to someone who never saw Think Python: no
  references to the book or its examples; show every helper function the question uses, in the
  question; the main point is the Python, and context goes last in a "**By the way:**" paragraph.
- **Levels.** Heading `### Question N (easy|medium|hard): <kind>`; keep the page ordered easy → hard.
- **Write-code questions give the function header** of every function to write, as a
  ```python block with `...` as the body, after "Start from this header (replace `...` with the
  body):". Only a question that tests writing the header itself may skip it (tag its
  `# Your code here` cell `no-signature`).
- **Write-code questions show at least 2 examples**, each a ```python block followed by its
  output (```text block, or `<img data-turtle src="">` for a drawing).
- **Wrong-call questions** ("predict the error" for calls to a function) first show at least 2
  correct ways to call the function, each with its output ("Two correct ways to call it:").
- **Answers** are collapsible, give more than one approach when there is one, and every ```python
  block in them runs unchanged as a new .py file: imports, all helper functions, and a call.
- **Errors as answers**: tag the code cell `raises-exception` (never `%%expect`); show the exact
  `ErrorType: message` line in a ```text block. If an editor can see the error without running the
  code (syntax error, undefined name, wrong arguments, unknown module), Colab underlines it and
  gives the answer away: put the code of every part of that question in `run_code("""...""")`
  (defined in the setup cell; see "Errors an editor can see" in `yr/README.md`).
- **No `(c)`/`(r)`/`(tm)`/`+-` in text**: write **Part a**, **Part b**, **Part c**.
- Only use Python taught up to this chapter, or explain the extra bit in the question.

## Steps

1. `python3 yr/tools/review_cells.py list yr/chapNN_review.ipynb` to see the existing questions,
   and pick topics from the page's Concepts covered that have few or no questions.
2. Write the new questions in a spec file in your scratchpad (format: run
   `python3 yr/tools/review_cells.py` without arguments). A typical write-code question:

   ````
   %%% markdown
   ### Question 21 (medium): write a function

   Write a function called `square` that takes `length` and draws a square.

   Start from this header (replace `...` with the body):

   ```python
   def square(length):
       ...
   ```

   **Examples**

   ```python
   make_turtle()
   square(50)
   ```
   <img data-turtle src="">

   ```python
   make_turtle()
   square(20)
   ```
   <img data-turtle src="">
   %%% placeholder
   %%% answer
   ```python
   from jupyturtle import make_turtle, forward, left

   def square(length):
       for i in range(4):
           forward(length)
           left(90)

   make_turtle()
   square(50)
   ```
   ````

3. Insert them: `python3 yr/tools/review_cells.py add yr/chapNN_review.ipynb SPEC [--before N]`
   (to keep easy → hard order), then `python3 yr/tools/review_cells.py renumber yr/chapNN_review.ipynb`.
   Fix any "Question N" cross references it reports (better: avoid them).
4. If any turtle pictures were added or their code changed: `yr/tools/review.sh images yr/chapNN_review.ipynb`.
   Look at the pictures (extract a few PNGs from the data: URIs to your scratchpad and view them):
   is the drawing inside the canvas and is it what the text says?
5. `yr/tools/review.sh check yr/chapNN_review.ipynb` must print OK. It runs the page, compares
   every printed output and error with the Answer, runs each answer code block as a standalone
   .py file, and checks headers, examples, correct calls before wrong ones, pictures and
   symbol text. Fix the question or the answer
   until it passes; never weaken the check.
6. If "Concepts covered" lacks a fact a new question relies on, add it there (same style).
7. `python3 .claude/skills/check-notebooks/check_notebooks.py` and
   `.claude/skills/build-book/build_book.sh` (no new warnings); look at the page if the layout changed.

To revise existing questions, edit the cells (NotebookEdit tool or a `json` script, keeping cell
ids), then steps 4-7.

Report which questions were added or changed and that `review.sh check` passed.
