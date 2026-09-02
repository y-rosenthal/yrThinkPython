# Think Python, 3rd edition (course fork)

This is a fork of [AllenDowney/ThinkPython](https://github.com/AllenDowney/ThinkPython),
adapted for use in a Python course. The online version of this fork is at
<https://y-rosenthal.github.io/yrThinkPython/>.

The original book is *Think Python: How to Think Like a Computer Scientist*, 3rd edition,
by Allen B. Downey. The original online version is at
<https://allendowney.github.io/ThinkPython/>, and the home page for the book is at
[Green Tea Press](http://thinkpython.com).
You can order print and electronic versions of *Think Python 3e* from
[Bookshop.org](https://bookshop.org/a/98697/9781098155438) and
[Amazon](https://www.amazon.com/_/dp/1098155432?smid=ATVPDKIKX0DER&_encoding=UTF8&tag=oreilly20-20&_encoding=UTF8&tag=greenteapre01-20&linkCode=ur2&linkId=e2a529f94920295d27ec8a06e757dc7c&camp=1789&creative=9325).

Like the original, this work is licensed under a
[Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License](https://creativecommons.org/licenses/by-nc-sa/4.0/).

## Layout

- `chapters/` – the chapter notebooks (`chap00.ipynb` … `chap19.ipynb`). Edit these.
- `blank/` – "fill in the blanks" versions of each chapter with most code removed.
- `jb/` – Jupyter Book configuration (`_config.yml`, `_toc.yml`), the landing pages
  (`index.md`, `blank.md`) and `prep_notebooks.py`, which strips `%%expect` magics and
  adds section labels before the HTML build.
- `thinkpython.py`, `diagram.py`, `structshape.py`, `words.txt`, `photos.zip` – helper
  modules and data files used by the notebooks.

## Publishing the website

The site is built by the GitHub Actions workflow in `.github/workflows/deploy-book.yml`.
On every push to the `v3` branch it copies the notebooks from `chapters/` into `jb/`,
builds the HTML with Jupyter Book, and publishes the result to the `gh-pages` branch,
which GitHub Pages serves. The workflow can also be started by hand from the
repository's **Actions** tab.

To build locally:

```bash
pip install "jupyter-book<2"
cp chapters/chap[01][0-9].ipynb jb/
cd jb
python prep_notebooks.py
jb build .
# open _build/html/index.html
```

## Keeping up with the original

The `upstream` remote points at the original repository:

```bash
git fetch upstream
git merge upstream/v3
```
