# yr/ — Prof. Rosenthal's course additions

This folder holds material written for Prof. Rosenthal's classes that is **not** part of
Allen Downey's *Think Python*. Keeping it here, instead of inside the chapter notebooks, means:

- the original chapters, their numbering and their exercises are unchanged;
- `chapters/` stays close to upstream, so syncing with AllenDowney/ThinkPython rarely conflicts;
- it is always clear which material is the book and which is the course's.

```
yr/
  README.md                this file: the rules for the course's pages (layout, format, style, tools)
  chapNN_additions.ipynb   material that a chapter uses but does not explain (only the chapters that need one;
                           more additions pages are chapNN_additions_TOPIC.ipynb)
  chapNN_review.ipynb      a review page of a chapter (the review format: review.sh sync writes its outputs)
  chapNN_more_review.ipynb more review questions, after the review page (only the chapters that need one; other
                           pages of review questions have their own KIND, for example chap09_palindromes.ipynb;
                           a new one is written in the review format too)
  NAME.md                  a page of the course without code (an introduction, a note)
  NAME_SOMETHING.md        a page of a hidden part of the book; the website shows the part only with
                           ?show=NAME in the address (none now: "A hidden part of the book")
  tiny_book.txt            a small "book" of 4 lines that 9b reads; the website serves it (html_extra_path)
  yrdiagram.py             draws state diagrams (variables and the objects they refer to) for 8b, 9b, 10b, 11d
  plans/                   design notes (runall-collapsible-answers.md: the review-page format)
  tools/
    review_cells.py        create a review page skeleton; add, list, number, renumber questions
    review.sh sync NB      write everything that can be derived, by running the code
    review.sh check NB     verify the page (fails if sync would change anything)
    review.sh normalize NB repair a page that was saved in Colab
    review.sh selftest     prove that sync and check catch broken pages
    review_format.py       the page format (used by all the tools and by jb/prep_notebooks.py)
    sync_review.py, check_review.py, selftest_review.py, selftest/   (used by review.sh)
    ensure_colab_venv.sh, colablike.lock   the pinned Colab-like kernel
    verify_site.py         check a converted page on the built website
```

**This file is the one place for the rules of the course's pages.** The author guide (`author-guide/`, a
Quarto book) includes it, and the Claude Code skills follow it: `yr-additions-page` (create or change an
additions page), `yr-review-page` (create a review page or write its concept summary), `yr-review-questions`
(add or revise review questions) and `add-page` (any other page). When a rule or a tool changes, change it
here, and change a skill only if its steps change. Do not repeat a rule in another file: point to the
section here.

## The pages of a chapter

Do not change Downey's chapters to add material. A chapter can have any number of pages of the course after it.
They are lettered in the order of the table of contents: `b`, `c`, `d`, ... `z`, then `aa`, `ab`, ... (Downey's
chapter is the "a" page, without a letter). The letter is not in the file name: it comes from the position, so a
page inserted before another changes the letters after it, and `review.sh sync` and `check_notebooks.py` follow.
A page is `yr/chapNN_KIND.ipynb` (KIND: lowercase letters, digits and `_`). The usual kinds, in their order:

| Order | Title on the website | File | When |
|---|---|---|---|
| 1 | NN. (Downey's chapter title) | `chapters/chapNN.ipynb` | always |
| 2 | NNb. Additions: TOPIC | `yr/chapNN_additions.ipynb`, and more additions pages `yr/chapNN_additions_TOPIC.ipynb` | only if the chapter needs it |
| 3 | NNb. Review: TOPIC, or **NNc.** after one additions page | `yr/chapNN_review.ipynb` | each chapter that has a review |
| 4 | NN<letter>. Review: TOPIC | `yr/chapNN_more_review.ipynb`, or another KIND (`yr/chapNN_palindromes.ipynb`) | more review questions, when needed |

- **The title** of every page of a chapter is `# NN<letter>. Additions: TOPIC` or `# NN<letter>. Review: TOPIC`.
  TOPIC says what is on the page, in title case, in a few words: for example `9c. Additions: Nested Loops`,
  `9f. Review: Palindromes`. The label is `Additions` for the kinds `additions` and `additions_TOPIC`, and
  `Review` for every other kind (`review_format.page_label`). The topic of the review page
  (`chapNN_review.ipynb`) is usually the chapter's title (`9d. Review: Lists`); `review.sh sync` keeps the topic
  that is in the title cell. `check_notebooks.py` checks the letter and the label, and that there is a topic.
- The additions pages come before the review page, and the review page before the more-review page.
- A page uses the format of a review page (`review.sh sync` and `check`) when its Answers are `#### Answer`
  headings (`review_format.uses_review_format`): `yr/chapNN_review.ipynb` always, and every page of review
  questions written since November 2026 (`yr/chap09_palindromes.ipynb`, `yr/chap09_practice.ipynb`). The
  additions pages, and the two older more-review pages (`yr/chap07_more_review.ipynb`,
  `yr/chap09_more_review.ipynb`), use the format of an additions page ("Additions pages"): the build runs their
  code cells, and turns their `<details>` Answers into closed dropdowns. Write a new page of review questions in
  the review format ("More review pages").
- `review.sh sync` writes the letter of a review page in its title (`review_format.page_letter`: the page's
  position in the TOC). So after you add a page before a review page, run `review.sh sync` on the review page,
  and change its line in `jb/index.md` (`NNb.` to `NNc.`). The letter of every other kind is typed in its
  title cell; `check_notebooks.py` reports the right one.
- `jb/_toc.yml` lists the pages in one unnumbered part after the chapter. Numbering continues across the
  numbered parts, so the chapter numbers stay the same, and a page in an unnumbered part shows its own
  title (`NNb. …`) without an added number:
  ```yaml
      - file: chap07
  - chapters:
      - file: yr/chap07_additions_data
      - file: yr/chap07_additions
      - file: yr/chap07_review
      - file: yr/chap07_more_review
  - numbered: True
    chapters:
      - file: chap08
  ```
- `jb/index.md` lists a Colab link for each page under the chapter, in the same order:
  `* [Click here to run 7c. Additions: File Paths and for Loops on Colab](https://colab.research.google.com/github/y-rosenthal/yrThinkPython/blob/v3/yr/chap07_additions.ipynb)`.
- `check_notebooks.py` checks the titles, and that the TOC lists the pages right after the chapter, in the
  order of the kinds.

## More review pages: `yr/chapNN_more_review.ipynb` and other kinds

A page of more review questions, "NN<letter>. Review: TOPIC" (for example "9f. Review: Palindromes"), holds
extra practice questions for a chapter when its review page is full or when a topic needs more practice. Write
it in the review format, as the review page ("Review pages"): `review.sh sync` writes every output and value by
running the code, and `review.sh check` verifies the page. **No output on a page of questions is typed by
hand**: a typed output is not checked, and a wrong one teaches the student something false. The differences
from the review page:

- `python3 yr/tools/review_cells.py new NN "TOPIC" --kind KIND` makes the skeleton `yr/chapNN_KIND.ipynb`
  (KIND: `more_review`, or a name for the topic, for example `palindromes`).
- The title cell may hold the page's own introduction in place of the template text: sync rewrites only a title
  cell in the template form ("A review of [Chapter ..."). Keep the title `# NN<letter>. Review: TOPIC` and the
  Colab link to the page's own file, and type the letter (`check_notebooks.py` reports the right one).
- `## Concepts covered` is optional. A page of questions only has `## Questions` (then the help note, the setup
  cell and the helper cell, which sync writes), the questions, and `## Credits`.
- A later question may call a function that an earlier question's Answer wrote (`isPalindrome` from Question 1
  in `findPalindromes`). The Answer block of the later question repeats that function, because a block runs on
  its own after Run all, and a note under the block says so. Put `<!-- header: NAME -->` in the prompt, so that
  the header block shows only the function to write; the prompt says which question wrote the helper.

`yr/chap09_palindromes.ipynb` is the reference example (`yr/chap09_practice.ipynb` is a long one). The
questions follow the rules of review questions ("Style rules": Questions and Answers), and their numbers are
stable in the same way ("Adding a question", "Question numbers between semesters").

Two older pages, `yr/chap07_more_review.ipynb` and `yr/chap09_more_review.ipynb`, are still in the additions
format: `## Practice questions`, `<details>` Answers with typed outputs, no stored outputs; the build runs their
code cells. Do not write a new page in that format. Converting them is issue #13.

**Exception: a project page.** A page with one large program that reads the user's input, such as
"11f. Review: A Tic-Tac-Toe Game" (`yr/chap11_tictactoe.ipynb`) and "11g. Review: An Othello Game"
(`yr/chap11_othello.ipynb`), is in the additions format: `review.sh sync` cannot type replies to `input()`,
and the build can ("Code that calls `input()`", with `input_replies` and `random_seed`). Its layout: the problem
(the rules, what the program must do, example runs), a `# Your code here` cell, and, if the page teaches the
solution, a section that develops the program one step at a time. In that section, **Thoughts ...** boxes
(blockquotes) show what a programmer thinks, **Stop and check** paragraphs make the student run and read each
step, and **Thinking ... refactor** boxes improve the code without changing what it does (each refactored
version runs with the same replies and seed, and gives the same output). A cell of that section may use the
functions of the cells before it. An example run in the text is captured from a real run of the program, not
typed: on 11f, the last cell runs the same game with the same replies and seed, so the build shows that the
example is right. A page that gives the problem only (11g) gets its example runs from a solution that is not
in the repository; keep the solution where you can run it again.

To add a page: write the notebook, list it in `jb/_toc.yml` after the chapter's review page (and after the
other pages of review questions), add its Colab line in `jb/index.md` in the same place, then verify it as a
review page ("Adding a review page for another chapter", step 6).

## Other pages of the course: `yr/NAME.md`

A page of the course without code (an introduction, a note to the students) is a markdown file `yr/NAME.md`.
List it in `jb/_toc.yml` in the part where it belongs (for example `Front Matter`), as `- file: yr/NAME`. It has
no Colab link. The build copies every `yr/*.md` except this README into `jb/yr/`; `check_notebooks.py` fails if a
markdown page is not in the TOC. The `add-page` skill gives the steps. MyST extensions that `jb/_config.yml`
enables (`colon_fence`, `dollarmath`, `deflist`, `tasklist`) work: `:::{note}` admonitions and `$x^2$` math.

**Thonny.** The class uses Thonny to run programs on the students' computers. Three pages explain it:
`yr/prof_r_thonny.md` (install Thonny, the editor and the Shell, `print` in a program), "3c. Additions: More
About for Loops" (a first look at the debugger) and "11c. Additions: The Thonny Debugger". The menu names, keys
and buttons on these pages are the ones of Thonny 4.0 (checked in its source code, 2026-11-23). When a new
version of Thonny changes them, change the three pages.

## A hidden part of the book: `yr/NAME_SOMETHING.md`

A part of the book can be on the website before the students know that it exists, for example the pages of one
semester (a test with its answers). The part is in the book, but the website shows it only when the address of
a page ends with `?show=NAME`. The first hidden part was `fall2026` (the part "Fall 2026": the midterm of
fall 2026, one page for each version of the test).

**Not in use now.** On 2026-11-18 Prof. Rosenthal had the part `fall2026` taken out of the website and out of
the files of this repository. He saw the part on the live website without `?show=fall2026`, and he does not
trust this way of hiding. The cause was not found on that day. `YR_HIDDEN_PARTS` is empty, and the book has no
hidden part. Do not make a hidden part, and do not put the midterm pages back, until he decides how to hide a
part. The script that he keeps with the test writes the pages and their files again, when he wants them.
The steps below say how the part was made; they stay here for his decision.

**Make a hidden part.**

1. Name each page of the part `yr/NAME_SOMETHING.md` (`yr/fall2026_midterm.md`). The script finds the pages of
   the part by `NAME_` in their address, so no other page can have `NAME_` in its file name.
2. Start each page with these lines. They keep the page out of the search of the website, and they tell search
   engines not to list it:

   ```
   ---
   nosearch: true
   myst:
     html_meta:
       robots: noindex, nofollow
   ---
   ```
3. List the pages in `jb/_toc.yml` in a part of their own, at the end, with a comment that names this section.
4. Add `NAME` to `YR_HIDDEN_PARTS` at the top of `jb/_static/yr.js`.
5. Add each page (`yr/NAME_SOMETHING.html`) to `sitemap_excludes` in `jb/_config.yml`.
6. Pictures and files to download of the part go in `jb/_static/NAME/` (the build copies only the `.md` and
   `.ipynb` files of `yr/`). A page shows a picture with `![what it shows](../_static/NAME/file.png)` and offers
   a file with ``{download}`the words of the link <../_static/NAME/file.pdf>` ``. These files are not hidden: a
   person who knows the address of a file can open it.
7. Build with `--clean`, and test in a browser with a web server (`python3 -m http.server` in
   `jb/_build/html`; the script needs `http`, not a file): the three cases below.

**What a reader sees.**

- Without `?show=NAME`: the menu, the "next" and "previous" links, and the search do not show the part. A page
  of the part shows only "This page is not available."
- With `?show=NAME` at the end of the address of any page of the book (for example
  `https://y-rosenthal.github.io/yrThinkPython/?show=fall2026`): the part is in the menu, and its pages show. A
  line at the top of each of its pages says that the page is hidden. The browser tab keeps showing the part,
  and the links of the book carry `?show=NAME` to the next page. Several parts: `?show=NAME1,NAME2`.
- With `?show=none`: the tab hides the part again.

**What hiding does not do.** It does not protect the pages. Their text is in the HTML of the website (and in
`_sources/` there), the menu entries are in the HTML of every page, and the files are in this public
repository. A person who looks there can read them. Do not put anything in a hidden part that must stay secret.
After a publish, do not scan the book for subjexts (the `yrpublish` skill, step 5) while a part is hidden,
unless Prof. Rosenthal says so: the scan gives the pages and headings of the book to the subjexts platform.

**Make the part visible to everyone.** Remove `NAME` from `YR_HIDDEN_PARTS`, remove the lines of step 2 from the
pages, remove the pages from `sitemap_excludes`, and remove the comment in `jb/_toc.yml`. Build with `--clean`,
check that the menu shows the part without `?show=`, and publish.

**The pages of fall 2026.** A script that Prof. Rosenthal keeps with the test, outside this repository, writes
`yr/fall2026_midterm*.md` from the test and its answers: the intro page, one page for each version (questions,
answers, steps), and one answer key page for each version (`fall2026_midterm_key_versionN.md`: the answer sheet
with the right answers filled in, as pictures, with the same pages as a PDF file; these pictures and files are
in `jb/_static/fall2026/`, written by the same script). The pages do not name the small marks that were printed
on the test papers (his decision of 2026-11-16). If you change one of these pages by hand, tell him:
the next run of the script writes the page again.

## Additions pages: `yr/chapNN_additions.ipynb`

A chapter can have more than one additions page: one for each topic. The first is `yr/chapNN_additions.ipynb`;
the others are `yr/chapNN_additions_TOPIC.ipynb` (for example `chap09_additions_while.ipynb`). Each has its own
title, `# NN<letter>. Additions: TOPIC` ("The pages of a chapter"). A topic that needs material from a later
chapter goes on an additions page of that chapter: nested loops are on 9c, not 8b, so that their examples can use
lists.

An additions page explains what the chapter uses but does not explain (for example, `range` with two or three
arguments for chapter 3), or what a student needs to run the chapter's code on their own computer (for
example, file paths for chapter 7). It is written like one of Downey's chapters: text, code cells that show
each idea, and practice questions at the end. Unlike a review page, it is a normal notebook: there is no
`review.sh sync` for it, and no stored outputs. The website build runs its code cells, as it runs the chapters.
Reference examples: `yr/chap07_additions.ipynb` (sections, Diving deeper boxes, practice questions) and
`yr/chap03_additions.ipynb` (a short one).

### Layout of a page

1. **Title cell**: `# NNb. Additions: TOPIC` (for example `# 9c. Additions: Nested Loops`), a link to the chapter, one sentence on how to use the
   page, and the line `[Run this page on Colab](https://colab.research.google.com/github/y-rosenthal/yrThinkPython/blob/v3/yr/chapNN_additions.ipynb)`.
2. **Setup cell** (code), the same as the chapter's first cell: it downloads `thinkpython.py` (for
   `%%expect`) and the files that the page uses (for example `words.txt`), then `import thinkpython`.
3. **Sections** (`## ...`): text, and code cells that show each idea. Show an error with a cell that starts
   with `%%expect ERROR_NAME`, as the chapters do, so that Run all in Colab does not stop.
   Code that depends on the student's computer (a full path, `os.chdir`) goes in a ```` ```python ````
   block in the text, not in a code cell: the build cannot run it.
   - **Code that calls `input()`** is a code cell. In Colab, the student types the reply. The website
     cannot wait for a person, so give the replies of a pretend user in the cell's metadata:
     `"input_replies": ["mary smith"]`. The build (`jb/execute_notebooks.py`) shows each prompt with the
     next reply after it, as if a person typed it, and `input()` returns the reply. One reply for each
     `input()` call in the cell. Show a function that calls `input()` in one cell, and call it in
     other cells with different replies, so that the student sees that the result depends on what the user types.
     In Jupyter, edit the metadata with **Property Inspector** (the gear icon at the right).
     Exception: a function whose right replies depend on a random value (the guessing game in
     `yr/chap11_additions.ipynb`). No fixed list of replies fits it. Its definition is a code cell (the build
     runs it; it calls nothing). The call is a ```` ```python ```` block in the text, with one typed run after
     it. Before you publish, run the function with the random value fixed, and make sure that the typed run
     agrees with what it shows.
     Or give the cell a seed too: `"random_seed": 2` in its metadata makes the build call `random.seed(2)`
     just before the cell, so the cell makes the same random choices at each build, and one list of replies
     fits (the games of `yr/chap11_tictactoe.ipynb`). In Colab, the seed does nothing: the student plays a
     random game. To find replies that fit a seed, play the cell once with that seed.
   - **The website's own files:** `jb/_static/yr.js` and `jb/_static/yr.css` are loaded on every page
     of the website. They hold the method boxes and the collapsible sections below, and the update check
     (a page that is older than the website reloads, or shows a "Reload" bar: see the author guide,
     "Students see the new version without a reload").
   - **Method boxes** (as in `yr/chap08_additions.ipynb`): to separate the description of each method,
     give it a `### ` heading, and put its text in a box in the same markdown cell:
     ```
     ### [`upper()`](https://docs.python.org/3/library/stdtypes.html#str.upper)

     <div class="yr-method" style="border-left: 6px solid #3b82f6; background: rgba(59,130,246,0.08); padding: 0.5em 1em; margin: 0.5em 0;">

     The text (no headings in the box).

     </div>
     ```
     The example code cells follow the box. In Colab, the inline style draws the box around the text. On
     the website, `jb/_static/yr.css` draws the box around the whole section: the heading, the text and
     the example code cells, up to the next heading.
   - **A quick summary with hidden code** (as in `yr/chap08_additions.ipynb`): a code cell that only shows
     results. Start it with `# @title TITLE`, give it the metadata `"cellView": "form"` (Colab then shows
     the title and the output, and hides the code), and the tag `remove-input` (the website shows only
     the output). A hidden cell can also draw a picture with code that the chapter has not taught (for
     example matplotlib and lists): the pixel grid and the sound samples in `yr/chap07_additions_data.ipynb`.
   - **A state diagram** (as in 8b, 9b, 10b and 11d: `y = x` and a copy): a hidden code cell, as in
     "A quick summary with hidden code", titled `# @title State diagram: ...`. It runs the example code again
     and calls `draw_variables({'x': x, 'y': y, 'z': z})` from `yr/yrdiagram.py`, which draws the variables
     in the notation of the book's state and stack diagrams. It finds the shared objects with `is`, so the
     picture always agrees with the code. The setup cell downloads `diagram.py` (Downey's) and `yrdiagram.py`
     (from the website).
   - **A collapsible section:** a markdown cell that starts with a heading and has
     `<div class="yr-collapse">` with a short text in it. In Colab, the reader can collapse any heading
     with the arrow next to it. On the website, `jb/_static/yr.js` puts the heading and its section in a
     `<details>` block, open at the start; a click on the heading hides or shows the section. In
     `yr/chap08_additions.ipynb`, each method section has an introduction and a quick summary, then a
     collapsible "Details: ..." section (`###`) with one method box (`####`) for each method.
   - **All the sections collapsible, with "Collapse all" and "Expand all" buttons** (as in
     `yr/chap08_additions.ipynb`): put `<div class="yr-collapse-all"></div>` in the title cell. On the
     website, every section with a `##`, `###` or `####` heading is then collapsible, and each of these
     headings has three buttons: "Focus here" (show only this section: the other sections close, and the
     sections that contain it show only their headings and the path to it), "Collapse all" and "Expand all". The buttons change only the
     sections: the Answers and the Diving deeper boxes stay closed. In Colab, the reader collapses the headings with the arrows next to them.
4. **Diving deeper** boxes (optional): each is one markdown cell that is only a `<details>` block, with
   `<summary>Diving deeper: TOPIC</summary>` (or `Diving deeper (for Windows users): TOPIC` for material that
   only Windows users need), and a blank line after the `<summary>` line. It is closed in Colab and on the
   website. Put details that most students can skip in such a box.
5. **`## Practice questions`**: `### Question N (very easy|easy|medium|hard|very hard): KIND`, ordered very easy
   to very hard (a page does not need every level). Then each question has:
   - **what is displayed**: a prompt cell, then the question's code in a code cell tagged `hide-output`
     (the website shows the code, and the output only when the reader clicks), then the Answer;
   - **write code**: a prompt cell with the function header and examples, a `# Your code here` cell, then
     the Answer with the solution in a ```` ```python ```` block;
   - other kinds (which calls work, find the error, relative paths): a prompt cell, then the Answer.

   The Answer is one markdown cell that is only a `<details>` / `<summary>Answer</summary>` block (a blank
   line after `</summary>`, so that Colab shows the markdown in it):
   ```
   <details>
   <summary>Answer</summary>

   The text of the answer.

   </details>
   ```
6. **`## Credits`**: "*Additions by Prof. Y. Rosenthal, for* Think Python ..." and the text license (copy it
   from `yr/chap03_additions.ipynb`).

Cell conventions: nbformat 4.5, a unique 8-character `id` on each cell, `execution_count: null`, no outputs
(the `notebook-conventions` skill gives the details).

### Style rules

- Each fact once, in plain English, with an example for each fact. Show the general form with UPPERCASE
  placeholders, as on the review pages (`range(START, STOP, STEP)`).
- **The values in a list or a tuple must not look like indexes** (Prof. Rosenthal, 2026-11-25). In
  `[1, 2, 3]`, a student cannot tell the value `2` from the index `1`. Use values such as `[100, 200, 300]`,
  `[12, 24, 36, 48]` or strings (`['apple', 'pear', 'plum']`). This rule is for the questions of every page
  too. (The square numbers 1 to 9 of a tic-tac-toe board are names of squares, not list values.)
- Each code cell has all the data that it uses: it assigns each variable itself, and does not use a variable
  that an earlier cell assigns (write `text = 'the cAT in THE hat'` in each cell that uses `text`). A
  function can be defined in one cell and called in the cells right after it.
- Write file paths with forward slashes, also Windows paths (`C:/Users/YOUR_NAME/Downloads/words.txt`):
  Python accepts them on every system. Explain backslashes only in a "Diving deeper (for Windows users)" box.
- Use only what the book has taught up to this chapter, and what the page itself explains. For example,
  the chapter 7 page does not use lists or dictionaries.
- The questions are about the page's own material. The same rules as for review questions apply: they make
  sense without the book, write-code questions give the function header and at least two examples.
- **Never type an output by hand in a code cell.** The build runs the code cells
  (`jb/execute_notebooks.py`), so the website shows their real output. Text that states an output
  (an Answer, a sentence after an example) must agree with it: run the page
  (`.claude/skills/check-notebooks/run_notebooks.sh yr/chapNN_additions.ipynb`) and read each output.
  Run each Answer's code with its examples too.
- No stored outputs (`check_notebooks.py` fails on them), as in `chapters/`.

### Adding an additions page

1. Read every cell of `chapters/chapNN.ipynb`, and note what earlier chapters teach. Find what the chapter uses
   but does not explain. If the chapter already has an additions page on the same topic, add the new material to
   it; for a new topic, make another additions page (`yr/chapNN_additions_TOPIC.ipynb`).
2. Write the notebook (the layout and the style rules above).
3. Add the page to the site:
   - `jb/_toc.yml`: list the page in the unnumbered part after `chapNN`, after the other additions pages and
     before `yr/chapNN_review`. If the chapter has no such part yet, make one ("The pages of a chapter").
   - `jb/index.md`: under the chapter, add the Colab line of the additions page before the review line, and
     change the letters of the lines after it (`NNb.` to `NNc.`, ...).
   - The pages after it: `yr/tools/review.sh sync yr/chapNN_review.ipynb` writes the new letter in the title of
     the review page; type the new letter in the title of each other page after it (`check_notebooks.py` reports
     it). `yr/tools/review.sh check yr/chapNN_review.ipynb` must print `OK`.
   - A file that students must download from the website (as `words.txt` for chapter 7, or
     `yr/tiny_book.txt` for 9b): add it to `html_extra_path` in `jb/_config.yml`, and link to
     `https://y-rosenthal.github.io/yrThinkPython/FILE`. The page's setup cell downloads it from that address.
     A module that pages import (`yr/yrdiagram.py`) is served and copied in the same way.
     The website does not have the file before the first publish, so the build gives a copy of it to the
     page: add the file to `HELPERS` in `jb/execute_notebooks.py` and to the `cp` line of
     `.claude/skills/check-notebooks/run_notebooks.sh`.
4. Verify:
   ```bash
   .claude/skills/check-notebooks/run_notebooks.sh yr/chapNN_additions.ipynb   # must print ok
   python3 .claude/skills/check-notebooks/check_notebooks.py                    # must print OK
   .claude/skills/build-book/build_book.sh                                      # no new warnings
   ```
   Read the output of each code cell in the executed copy (the path is in the last line of `run_notebooks.sh`):
   each sentence that states an output must agree with it. Run the code of each Answer with the question's
   examples. Look at `jb/_build/html/yr/chapNN_additions.html`: the sidebar order (NN, NNb, NNc, NN+1), the
   outputs, the closed Answers and Diving deeper boxes, the hidden outputs of the "what is displayed" questions.

## Review pages: `yr/chapNN_review.ipynb`

One notebook per chapter, titled `NNb. Review: TOPIC` (e.g. `4b. Review: Functions and Interfaces`), or
`NNc. Review: TOPIC` when the chapter has an additions page (e.g. `10c. Review: Dictionaries`), or a later letter after
more additions pages (`7d. Review: Iteration and Search`; see "The pages of a chapter"). The topic is usually the chapter's title. It helps students review one chapter. It has **Concepts covered**, two lists of facts as a checklist,
and **Questions**, practice questions from very easy to very hard, each with an **Answer** that is closed until the
student opens it. `yr/chap04_review.ipynb` is the reference example.

### What a student sees

In Colab:

- Each Answer is closed. The student clicks the arrow next to **Answer** to open it.
- An Answer can show the real output of the question's code (printed text, an error, a drawing).
  The output is stored in the page, so the student sees it before running anything.
- The student can use **Runtime → Run all**. Run all runs the whole page, and it does not stop at
  the questions whose answer is an error. All Answers stay closed.
- The question's code is text, not a code cell. Thus, Colab's editor does not mark the mistakes in
  the code before the student makes a prediction.
- After Run all, the student can copy any code block from an Answer into a new cell, and run it.

On the website, each Answer is a closed box with the explanation and the stored outputs.

### Where it appears

- **Website:** right after its chapter (and after the chapter's additions pages, if there are any) in the
  sidebar, as "4b. Review: Functions and Interfaces". The previous/next buttons go 4 → 4b → 5 (or 7 → 7b → 7c → 7d → 7e → 8). The book's chapter and section numbers do not change.
- **Colab:** each page has a "Run this page on Colab" link at the top, and `jb/index.md` lists
  it under its chapter. (The links point at `v3`, so they work once the page is merged there.)

### Layout of a page

Sync writes the cells marked *(template)*; do not edit them.

1. **Title cell** *(template)*: `# NNb. Review: TOPIC` (or `NNc.`), a link to the chapter, how to use
   the page, and the Colab link. Sync keeps the topic that is in the title and the chapter title that is in the link.
   `review_cells.py new` uses the chapter's title as the topic; to change the topic, edit the title line, then run
   sync.
2. **`## Concepts covered`**, with two collapsible lists, written as `<details open>` (open in Colab; closed
   at the start on the website):
   - **Python Syntax and Semantics**: what the chapter teaches about Python itself.
   - **Definitions, etc.**: the definitions (each bullet starts with `DEFINITION:`), then
     "Other ideas" (programming practices and other concepts that are not syntax).
   Values in these lists can use markers too.
3. **`## Questions`**: a short introduction (e.g. what the turtle functions do). Then the help note
   *(template; not shown on the website)*, the setup code cell (tagged `setup`), and the helper cell
   "Helper for the Answers" *(template; tagged `setup`, code hidden; it defines `run_code`)*.
4. The questions, `### Question N (very easy|easy|medium|hard|very hard): <kind>`, ordered very easy → very hard. Each has its
   prompt, its run blocks or examples, its definition cells or `# Your code here` cell, and the
   `#### Answer` heading, saved closed. **Question numbers stay fixed during a semester**
   (homework is assigned by number): a question inserted between Questions 3 and 4 is numbered
   **3b** (then 3c, ...), and no other number changes. Renumber 1, 2, 3, ... only when starting a new
   semester ("Question numbers between semesters").
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
  (e.g. "`range(-4)` produces no values"). Complete: someone who ticks off every bullet has reviewed
  the whole chapter.
- Values in the lists are expressions with a marker (`` `-7 // 2` is <!--=-->`?` ``); sync computes them
  after the setup cell only.

**Questions**

- Focus on code, not definitions. Mostly two kinds:
  - **what is displayed / drawn / happens?**: code to predict, then the Answer shows its output;
  - **write code**: write a function, or refactor given code.
  A few other kinds are fine (find the bug, write a docstring, which call is wrong...).
- A page has about 15 to 20 questions: a mix of levels, ordered very easy → very hard. The levels are
  very easy, easy, medium, hard and very hard; a page does not need every level. The level is in the heading.
- **Each question must make sense to someone who never saw Think Python.** These questions may be
  reused in other materials. So: no references to the book, its sections or its examples
  ("like `circle` in the chapter"); give any helper function a question uses (a definition cell,
  or a pointer to the question that defines it); introduce any module the page uses (e.g.
  `jupyturtle`) at the top of the Questions section.
- Only use Python taught up to this chapter, or explain the extra bit in the question.
- The values in a list or a tuple must not look like indexes (Additions pages, "Style rules").
- **A question that reimplements a Python function, method or operator** (`my_count` for `count`, `my_find`
  for `find`, `my_contains` for `in`) says in the prompt what the function must do, so that a student who
  does not know the built-in can write it. Its Answers never use the built-in that the question
  reimplements (not even a close relative: no `in` in an Answer for `my_contains`, no `index` for
  `my_find`). The point is practice in writing what Python already provides. A later question may call
  the function that an earlier question wrote.
- **Write-code questions give the function header** of each function to write. Sync writes it ("Start from this header (replace `...` with the body):"). Exception: a question
  whose point is writing the header itself; tag its `# Your code here` cell `no-signature`.
- **Write-code questions show at least two examples**, each with its output (sync writes it).
- **Questions about wrong calls** (predict the error) first show the function being used
  correctly in at least two ways, each with its output ("Two correct ways to call it:"). These are
  ```` ```python ```` blocks in the prompt; sync writes their output.
- Put the main point about the *Python* first. Side remarks about the context of an example go
  last, in a paragraph that starts "**By the way:**".
- For the parts of a question write **Part a**, **Part b**, **Part c**: no `(c)`, `(r)`, `(tm)` or `+-` in
  the text (the website turns them into ©, ®, ™ and ±).

**Answers**

- Each question ends with an Answer that is closed until the student opens it. For "what is
  displayed" questions, the Answer shows the real output (written by sync), then a short
  explanation. For drawings, the picture.
- Give more than one approach when there is more than one reasonable one.
- **A student can copy any ```` ```python ```` block of an Answer into a new cell after Run all and
  run it.** The block has its own import lines (sync writes them), and uses the helpers that the
  questions define; it has no example calls, no example inputs and no provided helpers.

### Adding a question

For each kind of question, this section tells you what to type. The tools write everything else.

**The rule: type each fact once.** You type the question's code, the solutions, the example calls,
the fixes and the explanation. You do not type outputs, error names, values, function headers,
import lines or pictures. `review.sh sync` runs the code and writes them. `review.sh check` fails if
something that sync writes was typed or edited by hand.

| You type | The tools write |
|---|---|
| The question's code | The hidden cell that runs it, and its output |
| The explanation, with a marker for each error name | The error name |
| Each helper function, in one cell | "Run this cell to define ..." and "This question uses ... from Question N" |
| The task and the example calls | The "Start from this header" block, and the output of each example |
| The solutions (no imports, no example calls) | The import lines of each solution, and a "Then try:" line |
| Fixes and "what if" code | Their outputs and pictures |
| Each value in the text, as an expression | The value |

**The workflow, for every kind:**

1. Get the number: `python3 yr/tools/review_cells.py next yr/chapNN_review.ipynb --before 4` prints
   `3b` (a new question between Questions 3 and 4). At the end of the page, omit `--before`.
   Numbers stay fixed during a semester.
2. Write the cells in a spec file: a text file of cells, each starting with a line `%%% KIND`
   (`python3 yr/tools/review_cells.py --help` lists the kinds; the examples below show them). Then
   `python3 yr/tools/review_cells.py add yr/chapNN_review.ipynb SPEC --before 4`. The tool refuses a number
   that already exists and prints the free one.
   Or edit the notebook in Jupyter (not in Colab: see "If you edit a page in Colab").
3. `yr/tools/review.sh sync yr/chapNN_review.ipynb`. Read its report: it prints each new output and
   value. If an output that was already on the page changes, sync shows the difference and does not
   write it. Read the Answer's text again; if it is still right, run sync again with `--accept`
   ("Read the report of sync").
4. `yr/tools/review.sh check yr/chapNN_review.ipynb` must print OK. Fix the question or the answer until it
   passes; never weaken the check ("Format rules").
5. Look at new pictures (extract a PNG from the stored output or the `data:` URI, or build the site). If
   "Concepts covered" lacks a fact that a new question relies on, add it there, in the same style.
6. `python3 .claude/skills/check-notebooks/check_notebooks.py`, then
   `.claude/skills/build-book/build_book.sh` (no new warnings), and look at the page.

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

**Find the error, in parts** (syntax errors, NameError, wrong calls, a failing import, RecursionError). Use one
run block per part (`%%% run a`, `%%% run b`, ...) and one Answer cell per part (`%%% part a`). Name each error
with `<!--=error-->`:

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
Answer is a solution: check runs each one against every example, and all must give the same output. Mark a
block that is not a full solution (for example, a halfway version) with `<!-- not a solution -->` on the line
above it; sync then writes its output under it. If a solution has a helper function, the header shows it too;
to show only some functions, write `<!-- header: end_hour -->` on its own line in the prompt.

**Write code without a function.** The student writes code that uses variables that already have values. The
examples assign the input variables, and the `# Your code here` cell is tagged `no-signature`
(`%%% placeholder no-signature`). Make the first example a definition cell, so that Run all gives values to
the variables; sync writes its output in the text cell after it. The solution is only the computation; sync
runs each example's assignments, then the solution:

````
%%% markdown
### Question 11 (medium): write code

The variables `hours` and `minutes` have values. Write code that displays the total number of
minutes.

**Examples** (each example assigns the variables; your code comes after them)
%%% code
hours = 1
minutes = 2
%%% markdown
```python
hours = 0
minutes = 42
```
%%% placeholder no-signature
%%% answer
```python
print(hours * 60 + minutes)
```
````

**A helper the question provides.** Put it in a definition cell (`%%% code`): a code cell that only
defines or assigns (`def`, `class`, `import`, assignments) and displays nothing. Sync writes "Run this cell to
define `square`." above it. A later question that uses `square` gets "This question uses `square` from
Question 11." Type a helper only once, where it is first provided. In a write-code question, put the cell
before the `**Examples**` line (heading and first text, the cell, then a text cell with the task and the
examples): a definition cell after that line is an example, and sync writes "(nothing is displayed)" under it.

**Wrong calls (predict the error).** First show at least two correct calls in ```` ```python ```` blocks in the
prompt; sync writes their outputs. Then give the wrong calls as run blocks, in parts.

**A fix or a "what if".** In the Answer, write a short ```` ```python ```` block: only the changed
lines (they run after the question's code), or only the new `def` (the question's own calls run
after it). Sync writes its output or picture under it. A fix that uses a name that a later question
assigns keeps its own input line (`price = 4`), because after Run all the name has the later value
(check prints a note with the names that more than one question assigns).
To show the whole question's code with one change, write
`<!-- derive: from=Q14 replace="for letter in word:" with="for letter in word.lower():" -->` and an
empty ```` ```python ```` block under it; sync fills the block.

**After Run all, a student can copy any Answer block into a new cell and run it.** So Answer blocks
have no example calls, no example inputs and no provided helpers; sync writes their imports.

### Markers

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
| `<!-- derive: from=QN replace="OLD" with="NEW" -->` | the next ```` ```python ```` block: Question N's run block with OLD replaced by NEW (if OLD is not in the run block: its definition cells, then its run block); `from=solution`: this question's first solution. `\n` in OLD or NEW is a line break |

Values are computed after Run all and after the question's code (in Concepts: after the setup cell
only), with the value shown as a notebook shows it (`'abc'` with quotes, `4.0`).

- **A value marker never starts a line or a list item.** Colab then shows the line as raw HTML.
  Write "`-7 // 2` is <!--=-->`?`", not "<!--= -7 // 2 -->`?` is ...".
- A block marker (the last three) is alone on its line.

### What sync writes

- **Run cells**, one per run block, under the Answer heading (multi-part: after each part's
  explanation). The code is hidden; the title names the question ("Output of Question 8a"); the
  output is stored. A run cell whose code raises an error, or prints a line number, calls the
  page's `run_code` helper: it prints the traceback as text, so Run all does not stop and Colab
  shows no red marks.
- **Generated regions**, between `<!-- begin generated: KIND -->` and `<!-- end generated: KIND -->`
  lines: `header`, `example`, `output`, `then-try`, `uses`, `define`.
- **Import lines** at the top of Answer code blocks; the line `<!-- generated imports: N -->`
  above a block says that its first N lines are written by sync.
- **Values** in place of each `?`.
- **The template cells**: the title cell, the help note "Using this page in Colab or Jupyter", the helper cell
  "Helper for the Answers", and the credits.
- **The stamp** (notebook metadata `yr_review`): the stack that wrote the outputs, and checksums
  that let check find hand edits. The stamp records Python as `3.13`, without the patch number. Each computer
  makes its kernel with the newest Python 3.13 of that day, so the patch number differs between computers;
  without it, a page has the same stamp on every computer.

Never edit what sync writes. Sync runs the code only on the pinned Colab-like kernel (Python 3.13,
IPython 7.34.0, ipykernel 6.17.1, as Colab; `yr/tools/ensure_colab_venv.sh`, which `review.sh`
calls), so that the stored outputs look like what students see.

### Read the report of sync

| Message | What it means | What to do |
|---|---|---|
| `new ... output` or `value of ... is ...` | Sync wrote something new | Make sure that the text agrees with it |
| `NOT WRITTEN: these would change` | A stored output, region or value would change | Read the Answer again. If it is still correct, run `sync` again with `--accept` |
| `REFUSED, nothing written` (exit 2) | Sync cannot continue | Read the reasons, correct the page, run `sync` again |
| `the solutions disagree` | Two solutions give different outputs for an example | Correct a solution, or mark a draft `<!-- not a solution -->` |
| `the kernel ... runs ..., not the pinned Colab-like stack` | The wrong kernel | Run `yr/tools/ensure_colab_venv.sh`, or use `review.sh`, which does it |
| `derive marker: ... occurs N times` | The OLD text must occur exactly one time | Use a longer OLD text |
| `the expression has no value` | A value marker's expression displays nothing | Use an expression, not a statement |

### Format rules (`review.sh check` enforces them)

Check gives each problem its rule number.

1. Question headings are `### Question N (level): kind`; N is digits and an optional letter (`3b`),
   unique on the page; level is `very easy`, `easy`, `medium`, `hard` or `very hard`
   (`review_format.LEVELS`).
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
    (C4 in check's output: a student who copies the block into a new cell after Run all does not see what
    the page says.)
13. A "NameError" answer stays true: no other cell assigns that name.
14. The page ends with the credits, and no other cell is a credits cell; tags only `setup`, `no-signature`,
    and `remove-cell` (help note).
15. Do not edit what sync writes, and do not save a page from Colab back to GitHub. (A rule for you: check
    cannot test it directly. It finds the result through rules 9 and 11.)
16. No `TODO` left. No `(c)`, `(r)`, `(tm)` or `+-` in the text: the website turns them into
    ©, ®, ™ and ±. For parts of a question write **Part a**, **Part b**, **Part c**.
17. Every Answer has an explanation or a solution: text or a code block that you typed, not only what sync
    writes. (The tools know by its position which question a cell belongs to. A cell that was moved to
    another place leaves its Answer empty. Check cannot find an explanation that is under the wrong question:
    read the page after you move cells.)

Check also prints notes: names that more than one question assigns (a fix that uses one keeps its
own input line). `review.sh check --static` runs only the rules that need no kernel (fast).

### Change a question

1. Edit the cells that you typed (in Jupyter, with the NotebookEdit tool of Claude Code, or with a small `json`
   script). Keep the cell ids. Never `sed` the JSON.
2. Do not edit the run cells, the generated regions, or the values.
3. Run `sync`, then `check`, then the steps after them in "Adding a question".

If you change a question's code, sync makes its run cell again. If the output changes, sync asks
you to read the Answer again (`NOT WRITTEN`). Use `--accept` only if the Answer is still correct.

### Question numbers between semesters

During a semester, do not change a number. Use letters for new questions (3b, 3c). At the start of
a new semester, Prof. Rosenthal can number the questions 1, 2, 3, ... again:

```bash
python3 yr/tools/review_cells.py renumber yr/chap05_review.ipynb
yr/tools/review.sh sync yr/chap05_review.ipynb
```

`renumber` also changes "Question N" in the text, the `derive` markers and the run-cell titles, and records
the date, so that check knows that the page was renumbered. Read the changed text before you commit.

### If you edit a page in Colab

Colab adds metadata and outputs when it saves. Do not save to GitHub from Colab. If a page was saved
from Colab: `yr/tools/review.sh normalize NB` (removes what Colab added), then `review.sh sync NB`.
`check_notebooks.py` (also in CI) fails until the page is repaired.

### Turtle pictures

Sync draws them: the picture of a run cell's code, of an example, or of a fix. Example code should
start with `make_turtle()`. Pictures stay within the canvas: the turtle starts in the middle of a
300 × 150 canvas, facing east; use `jump(-x)` or `make_turtle(width=..., height=...)` to make room. Look at new
pictures on the built page.

### Tools

All run from the repository root.

```bash
python3 yr/tools/review_cells.py new 5 "Conditionals and Recursion"   # skeleton yr/chap05_review.ipynb
python3 yr/tools/review_cells.py new 9 "Palindromes" --kind palindromes  # another page in the review format
python3 yr/tools/review_cells.py list yr/chap04_review.ipynb
python3 yr/tools/review_cells.py next yr/chap04_review.ipynb [--before 7]  # the number for a new question
python3 yr/tools/review_cells.py add yr/chap04_review.ipynb spec.txt [--before 7]
python3 yr/tools/review_cells.py renumber yr/chap04_review.ipynb   # only between semesters
yr/tools/review.sh sync yr/chap04_review.ipynb [--accept]
yr/tools/review.sh check yr/chap04_review.ipynb [--static]
yr/tools/review.sh normalize yr/chap04_review.ipynb
yr/tools/review.sh pages                                   # the pages in the review format
yr/tools/review.sh check all                               # check (or sync) every one of them
yr/tools/review.sh selftest
python3 yr/tools/verify_site.py jb/_build/html/yr/chap04_review.html yr/chap04_review.ipynb [BEFORE.html]
```

Every tool takes `-h` or `--help`, which prints what it does and its options (`review.sh sync --help` also
shows the options of sync). `review_cells.py add` takes a small text file of cells; `review_cells.py --help`
shows the format.
`review.sh selftest` syncs `tools/selftest/fixture.ipynb` (a page with every kind of question), checks it, and
makes sure that check catches 30 kinds of broken page; run it after any change to the tools.

The first `review.sh sync` or `check` creates the Colab-like kernel in `~/.venvs/colablike` (it
needs `uv`, which `review.sh` installs into the book's venv, `~/.venvs/yrThinkPython`).

### Adding a review page for another chapter

Use the `yr-review-page` skill, or by hand:

1. Read every cell of `chapters/chapNN.ipynb`. List every fact taught: syntax, behavior, functions and
   modules used, definitions (the chapter's Glossary is a checklist for these), practices. Note what earlier
   chapters cover, so that questions only use material up to this chapter.
2. `python3 yr/tools/review_cells.py new NN "Chapter title"` makes the skeleton: the title cell,
   `## Concepts covered` with the two `<details open>` lists (TODO placeholders), `## Questions` with a setup
   cell tagged `setup`, and the credits. The first `review.sh sync` adds the help note and the helper cell.
3. Write the two Concepts lists and the questions ("Style rules", "Adding a question"). Adapt the setup cell
   to the chapter (downloads such as `jupyturtle.py` or `words.txt`, imports), and introduce any module the
   questions use at the top of the Questions section.
4. `jb/_toc.yml`: split the numbered "Chapters" list after `chapNN` and put the review page in
   its own unnumbered part between the two halves ("The pages of a chapter"; the comment above
   `yr/chap02_review` in the TOC explains why, keep it only once). If the chapter has additions pages, the
   review page goes in the same part, after them.
5. `jb/index.md`: add the Colab line under the chapter (and under its additions lines, if any), with the page's
   title (`NNb. Review: TOPIC`).
6. Verify:
   ```bash
   yr/tools/review.sh sync  yr/chapNN_review.ipynb       # writes outputs, pictures, values; read its report
   yr/tools/review.sh check yr/chapNN_review.ipynb       # must print OK
   python3 .claude/skills/check-notebooks/check_notebooks.py
   .claude/skills/build-book/build_book.sh               # must report no new warnings
   python3 yr/tools/verify_site.py jb/_build/html/yr/chapNN_review.html yr/chapNN_review.ipynb
   ```
   Look at `jb/_build/html/yr/chapNN_review.html` (or serve `jb/_build/html` with `python3 -m http.server`):
   sidebar position, numbering of the neighbouring chapters, the two concept lists and the answers
   collapsed, the buttons on their titles, outputs and pictures shown.

### How the build handles `yr/`

- `.github/workflows/deploy-book.yml` and `.claude/skills/build-book/build_book.sh` copy
  `yr/*.ipynb` and the markdown pages `yr/*.md` (not this README) into `jb/yr/` (gitignored) next to the
  chapter copies. `build_book.sh` empties `jb/yr/` first: a page that was removed from `yr/` must not be
  built from an old copy (the deploy starts with no `jb/yr/`). The pages in the review format are not run by the build: the website shows the outputs that
  sync stored. Every page in the additions format is run like the chapters (`jb/execute_notebooks.py`);
  `review_format.uses_review_format` decides which pages are in the review format.
- `jb/prep_notebooks.py` (`process_review`): each Answer (its text and its run cells' stored outputs,
  without their code) becomes one closed dropdown; the help note, the helper cell and the "Credits" heading
  are dropped; markers are removed (values stay); tracebacks are shortened; the concept lists become closed dropdowns;
  `# Your code here` cells are dropped. `process_additions`: each `<details>` cell (an Answer, a Diving deeper
  dive) becomes a closed dropdown, and `# Your code here` cells are dropped. The notebooks in `yr/` are never
  modified by the build.
- `jb/_static/yr.js` adds buttons to the title of each dropdown on these pages (Answers, concept lists,
  Diving deeper boxes): "Expand/Collapse" on every dropdown, and also "Expand all" and "Collapse all" (all
  the Answers of the page) on each Answer. `jb/_static/yr.css` styles them in the site's primary color:
  "Expand/Collapse" filled, the other two outlined. It also hides the hint "Click to show" of these dropdowns.
- `yr/tools/verify_site.py jb/_build/html/yr/chapNN_review.html yr/chapNN_review.ipynb [BEFORE.html]`
  checks a page on the built site (one closed Answer per question, no hidden code or markers on the page),
  and compares it with another build of the page (for example, before a big change).
- `check_notebooks.py` lints `yr/*.ipynb` (review pages: outputs only on run cells, the stamp, the markers;
  the other pages of a chapter: no outputs) and checks that each page in `yr/` is in the TOC, in the right order and with
  the right title, and that the workflow copies `yr/`. The deploy workflow runs it first, so a
  page with a problem is not published.

### Troubleshooting

- **`check` says rule 11 (sync would change the page).** Run `sync` and read its report.
- **`check` says rule 9 (stored outputs differ, or generated text was edited).** Somebody changed
  text that sync writes. Run `sync`, and read the differences before you use `--accept`.
- **`check` says rule 12 (an Answer block does not run).** The block uses a name that it does not
  import or define, or its output is not what the page says. Run `sync` (it writes the imports).
  If the problem stays, the block needs its own input line, or the solution is wrong.
- **`check` says rule 2 (a published number is gone).** You changed or removed a question number.
  Use its old number again, and give the new question a letter (3b).
- **`check` says rule 17 (an Answer has no explanation or solution).** The cell is missing, or it is in
  another place on the page (for example, at the end, under the last Answer). Move it back under its
  `#### Answer` heading, after the run cell.
- **`check` says rule 14 (a second credits cell).** Delete it: only the last cell of the page is the credits.
- **A value marker shows as raw HTML in Colab.** The marker starts a line. Put some text before it.
- **The build stops with "prep_notebooks: ... Answer dropdowns".** A page has a problem. Run
  `check` on the page.
- **Colab says "Too many sessions".** End old sessions: **Connect ▾ → Manage sessions**.

## Other course additions outside this folder

These came earlier and live elsewhere because the tooling expects them there:

- `solutions/`: suggested solutions to the book's own exercises, shown on
  the site behind "Suggested solution" dropdowns (the `notebook-conventions` skill).
- `.claude/skills/`: Claude Code skills for building, checking, deploying and syncing the book
  (they must stay in `.claude/`).
- Cells tagged `course` in `chapters/`: any course-specific edits made directly in a chapter
  (see the `notebook-conventions` skill). Prefer putting new material in `yr/` instead.
