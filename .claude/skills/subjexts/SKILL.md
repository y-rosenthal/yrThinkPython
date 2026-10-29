---
name: subjexts
description: The subjexts teaching overlay in this book (labels on passages, a table of contents by label, in-place edits, the AI tutor) - what the two subjexts files are, how to switch the overlay on and off, and where the subjexts procedures are (apply a note packet of the author's notes and edits to the source, mark the book from a list, register the book). Use when the user mentions subjexts, labels, the overlay, "Table of contents by label", a note packet ("apply the notes in ..."), or asks to switch it on or off or to plug the book in.
---

<!-- Installed by yrProject v0.6.0 (https://github.com/y-rosenthal/yrProject): the templates
     and the tool that give a project one base for AI-assisted work (rules for AI agents, skills, hooks, GitHub
     issues for work to do later, project docs). This file belongs to the tool: do not edit it by hand, and do
     not change it without the tool. "yrProject.sh update" replaces it with each new version (if you change it,
     update leaves it alone, and it gets no newer versions); "yrProject.sh remove" removes it.
     .yrProject/README.md lists every file that yrProject installed, and tells who changes each one. -->

# subjexts in this book

[subjexts](https://subjexts.github.io/) adds a teaching layer to this published book without changing its
source: instructors label passages ("Covered in class", "Read before the midterm"), students see thin colored
lines in the margin and a "Table of contents by label" page, teachers can edit a paragraph in place as a
proposal, and an AI tutor can answer questions about a passage. The platform (the `yrS4` repository,
`~/Dropbox/_yrAiCoding/yrS4`) holds the data; this book only carries one script line.

## The two files that belong to subjexts

| File | What it is | Who changes it |
|---|---|---|
| `subjexts-v001.html` | One `<script>` line that loads the overlay from `https://subjexts.github.io/overlay/v1/yrS4.js` with `data-package="OWNER/NAME"`, the book's package name on the platform | Only the package name, if the book is registered under another name |
| `subjexts-labels-v001.qmd` | The "Table of contents by label" page: an empty container the overlay fills when the book is viewed; hidden from the book's menu until a label exists | Nobody: the overlay owns its content |

They are wired in `_quarto.yml`: `subjexts-labels-v001.qmd` right after `index.qmd` in `book: chapters:`, and
`- file: subjexts-v001.html` under `format: html: include-after-body:`. A new book from `yrProject.sh new --type
book` has both; an existing book gets the files from `yrProject.sh update --with-subjexts` and the two lines
by hand (print them to the user; do not edit `_quarto.yml` without asking).

A Jupyter Book instead of Quarto: the script line goes into `jb/_config.yml` under `sphinx: config:
html_js_files:` as `["https://subjexts.github.io/overlay/v1/yrS4.js", {"data-package": "OWNER/NAME", "defer":
"defer"}]`, and the page is `jb/subjexts-labels.md` (a `<div id="yrS4-toc" data-yrs4-toc=""></div>`), listed
first in `_toc.yml`. The `subjexts-plug-in-book` skill in yrS4 (`scripts/plug-in-book.sh --jupyter-book`) writes
them.

## Switching it on and off

- **Off for everyone, from the source:** comment out the `- file: subjexts-v001.html` line and re-render. The
  page keeps working; the script fails silently when absent.
- **Off without a re-render:** the instructor's Teach bar in the panel has "Students see subjexts" per
  section and for the whole book, and "subjexts for me". These need no change to the book.
- The line is safe to leave in place: the script holds no key and does nothing if the package is disabled on
  the platform.

## Registering the book on the platform (once)

Done from the yrS4 repository, which has the platform's keys; this book repo never holds them:

```bash
cd ~/Dropbox/_yrAiCoding/yrS4
scripts/plug-in-book.sh --help            # writes the manifest packages/NAME.yml for a book that has none
node cli/bin/yrS4.mjs packages push NAME  # register the package (owner handle must have a profile)
node cli/bin/yrS4.mjs scan OWNER/NAME     # after the book is published: learn its pages and headings
```

The platform's `subjexts-plug-in-book` skill has the full procedure (sections, the manifest's options). Local
previews (`quarto preview`) show the overlay before the book is published.

## The subjexts procedures live in yrS4, not here

The platform repository (`yrS4`) holds one copy of each subjexts skill; this book carries none, so nothing can
go out of date here. To follow one, find it and read it:

```bash
bash .claude/skills/subjexts/scripts/yrS4-skill.sh                 # list the skills yrS4 has
bash .claude/skills/subjexts/scripts/yrS4-skill.sh apply-notes     # the path of that skill's SKILL.md
bash .claude/skills/subjexts/scripts/yrS4-skill.sh --cat apply-notes
```

| When the user asks to… | Read and follow |
|---|---|
| "apply the notes in …", a file whose front matter says `yrS4-packet: author-notes` (the author's private notes and in-place edits, exported from the platform) | `apply-notes` |
| label or mark many passages of the book from a list | `mark-book` (run from yrS4, which has the platform's keys) |
| plug the book in, register it, scan it | `plug-in-book` |

The script finds yrS4 through `$YRS4_DIR`, else the Dropbox tree this project is in (`…/_yrAiCoding/yrS4`),
else `~/Dropbox/_yrAiCoding/yrS4`. If it says yrS4 is not on this computer, tell the user: the procedure needs
that repository (clone it and set `YRS4_DIR`); do not improvise the procedure from memory.

## Rules

- Never edit the content of `subjexts-labels-v001.qmd` or add text to `subjexts-v001.html`; the overlay and the
  platform own what they show.
- The package name in `data-package` must match the platform's package (`packages/NAME.yml` in yrS4); a wrong
  name makes the overlay do nothing.
- Publishing the book is the book's own procedure; subjexts never requires a re-render except to add or remove
  its line.
- Using it: the platform's user guide, `docs/20-using.qmd` in yrS4 (sign in, Teach, checkboxes, labels, the
  switches).
