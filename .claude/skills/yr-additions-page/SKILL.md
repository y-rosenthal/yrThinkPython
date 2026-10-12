---
name: yr-additions-page
description: Create or change a "NNb. Prof. Rosenthal's Additions" page (yr/chapNN_additions.ipynb) - material that a Think Python chapter uses but does not explain, with examples and practice questions on the page - and put it before the chapter's review page (which becomes NNc). Use when asked to add missing material, extra explanations, "additions", or a topic the book does not cover, for a chapter, without changing Downey's chapter.
user-invocable: true
argument-hint: [chapter number] [topics]
---

# Create an additions page

Read `yr/README.md` first: "The pages of a chapter" and "Additions pages". `yr/chap07_additions.ipynb` is the
reference example (sections, a Deeper dive, practice questions); `yr/chap03_additions.ipynb` is a short one.

Do not change Downey's chapter (`chapters/chapNN.ipynb`). Work on a topic branch, not `v3`. Leave committing
and pushing to the user unless asked.

If the chapter already has an additions page, add the new material to it. A chapter has one additions page.

## 1. Study the chapter

Read every cell of `chapters/chapNN.ipynb`
(`python3 .claude/skills/notebook-conventions/nb_cells.py chapters/chapNN.ipynb`, then `--full`).
Find what the chapter uses but does not explain, and note what earlier chapters teach. The page may use only
that, and what the page itself explains. For example, do not use lists before chapter 9, or dictionaries before
chapter 10.

## 2. Write the page

Make the notebook with a small `json` script (never `sed` on the JSON): nbformat 4.5, a unique 8-character `id`
on each cell, no outputs, `execution_count: null`. Follow the layout in `yr/README.md`:

1. Title cell: `# NNb. Prof. Rosenthal's Additions`, the link to the chapter, how to use the page, the Colab
   link to `yr/chapNN_additions.ipynb`.
2. Setup cell: a copy of the chapter's first code cell (the `download` function, `thinkpython.py`, the files
   that the page uses, `import thinkpython`).
3. Sections: one idea at a time, the general form with UPPERCASE placeholders, a code cell for each example.
   Errors: a code cell that starts with `%%expect ERROR_NAME`. Code that depends on the student's computer
   (a full path, `os.chdir`) goes in a ```` ```python ```` block in the text.
4. An optional Deeper dive: one markdown cell that is only a `<details>` block, with
   `<summary>Deeper dive: TOPIC</summary>` and a blank line after it.
5. `## Practice questions`, easy to hard: what is displayed (code cell tagged `hide-output`), write code
   (header, two examples, a `# Your code here` cell), and other kinds. Each question ends with an Answer cell
   that is only a `<details>` block with `<summary>Answer</summary>`.
6. `## Credits`: copy it from `yr/chap03_additions.ipynb`.

## 3. Add the page to the site

- `jb/_toc.yml`: list `yr/chapNN_additions` in the unnumbered part after `chapNN`, before
  `yr/chapNN_review`. If the chapter has no yr/ part yet, make one (see `yr/README.md`, "The pages of a
  chapter").
- `jb/index.md`: under the chapter, add
  `* [Click here to run NNb. Prof. Rosenthal's Additions on Colab](https://colab.research.google.com/github/y-rosenthal/yrThinkPython/blob/v3/yr/chapNN_additions.ipynb)`
  before the review line, and change the review line from `NNb.` to `NNc.`.
- The review page: `yr/tools/review.sh sync yr/chapNN_review.ipynb` writes `NNc.` in its title, and
  `yr/tools/review.sh check yr/chapNN_review.ipynb` must print `OK`.
- `yr/README.md`: update "so far: chapters ..." for `chapNN_additions.ipynb` in the folder listing.
- A file that students must download from the website (as `words.txt` for chapter 7): add it to
  `html_extra_path` in `jb/_config.yml`, and link to `https://y-rosenthal.github.io/yrThinkPython/FILE`.

## 4. Verify

```bash
.claude/skills/check-notebooks/run_notebooks.sh yr/chapNN_additions.ipynb   # must print ok
python3 .claude/skills/check-notebooks/check_notebooks.py                    # must print OK
.claude/skills/build-book/build_book.sh                                      # no new warnings
```

- Read the output of each code cell in the executed copy (the path is in the last line of `run_notebooks.sh`).
  Each sentence that states an output must agree with it.
- Run the code of each Answer with the question's examples, and compare with what the question says.
- Look at `jb/_build/html/yr/chapNN_additions.html`: the sidebar order (NN, NNb, NNc, NN+1), the outputs, the
  closed Answers and Deeper dive, the hidden outputs of the "what is displayed" questions.

Report to the user what was added, what was verified, and what was not verified (for example, how the page
looks in Colab, which needs the notebook on GitHub).
