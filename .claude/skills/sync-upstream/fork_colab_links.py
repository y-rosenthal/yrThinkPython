#!/usr/bin/env python3
"""Point every Colab link in the book's notebooks and landing pages at this fork. Stdlib only.

    fork_colab_links.py            rewrite the links (safe to run again: it changes only what is still wrong)
    fork_colab_links.py --check    change nothing; exit 1 and list the links that are not the fork's

Upstream (AllenDowney/ThinkPython) puts Colab links in its notebooks: "Run this notebook on Colab" at the top of
each chapter, and links to the Jupyter introduction. After a merge they point at his repository, so a student who
clicks one opens Downey's notebook, not the fork's (no course edits, no review pages). This script rewrites

    https://colab.research.google.com/github/AllenDowney/ThinkPython/blob/v3/PATH
 -> https://colab.research.google.com/github/y-rosenthal/yrThinkPython/blob/v3/PATH

in chapters/*.ipynb, blank/*.ipynb, jb/index.md and jb/blank.md, when PATH exists in the fork. In blank/, the
"Run this notebook on Colab" link opens the blank notebook itself (blank/chapNN.ipynb), as jb/blank.md does.
Links to files the fork does not have are reported, not changed.

Called by: sync-upstream (after a merge), make_blank.py (on each notebook it writes), check_notebooks.py (--check).
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
UPSTREAM = 'https://colab.research.google.com/github/AllenDowney/ThinkPython/blob/v3/'
FORK = 'https://colab.research.google.com/github/y-rosenthal/yrThinkPython/blob/v3/'
LINK = re.compile(r'https://colab\.research\.google\.com/github/AllenDowney/ThinkPython/blob/v3/([^)\s"\\]+)')
RUN_IN_BLANK = re.compile(r'(\[Run this notebook on Colab\]\(https://colab\.research\.google\.com/github/'
                          r'y-rosenthal/yrThinkPython/blob/v3/)chapters/(chap\d\d\.ipynb\))')


REPO_NAME = re.compile(r'(AllenDowney/ThinkPython|y-rosenthal/yrThinkPython)(Solutions)?')
RUN_LINK = re.compile(r'(\[Run this notebook on Colab\]\(\S*?/blob/v3/)(?:blank|chapters)/')


def same_repo(text):
    """Text with the two repositories' names made the same: compare with this so that a link rewritten to the fork
    is not a difference (used by check_sync.py, upstream_diff.py and issue_body.py)."""
    return RUN_LINK.sub(r'\1', REPO_NAME.sub(r'REPO\2', text))


def fix_text(text, in_blank=False, missing=None):
    """The text with its Colab links pointed at the fork (missing: a list that gets the targets the fork lacks)."""
    def repl(m):
        path = m.group(1)
        if (ROOT / path).exists():
            return FORK + path
        if missing is not None:
            missing.append(path)
        return m.group(0)
    text = LINK.sub(repl, text)
    if in_blank:
        text = RUN_IN_BLANK.sub(r'\1blank/\2', text)
    return text


def fix_notebook(nb, in_blank=False, missing=None):
    """Rewrite the links in a notebook dict, in place (markdown cells only). Returns the number of cells changed."""
    n = 0
    for c in nb.get('cells', []):
        if c.get('cell_type') != 'markdown':
            continue
        src = ''.join(c['source']) if isinstance(c['source'], list) else c['source']
        new = fix_text(src, in_blank, missing)
        if new != src:
            parts = new.split('\n')
            c['source'] = [p + '\n' for p in parts[:-1]] + [parts[-1]] if isinstance(c['source'], list) else new
            n += 1
    return n


def files():
    return (sorted((ROOT / 'chapters').glob('*.ipynb')) + sorted((ROOT / 'blank').glob('*.ipynb'))
            + [ROOT / 'jb' / 'index.md', ROOT / 'jb' / 'blank.md'])


def run(check=False):
    """Returns (changed files, problems)."""
    changed, problems = [], []
    for p in files():
        if not p.exists():
            continue
        rel = p.relative_to(ROOT).as_posix()
        text = p.read_text(encoding='utf-8')
        missing = []
        in_blank = rel.startswith('blank/') or rel == 'jb/blank.md'
        if p.suffix == '.ipynb':
            nb = json.loads(text)
            if fix_notebook(nb, in_blank, missing):
                changed.append(rel)
                if not check:
                    p.write_text(json.dumps(nb, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
        else:
            new = fix_text(text, False, missing)
            if new != text:
                changed.append(rel)
                if not check:
                    p.write_text(new, encoding='utf-8')
        problems.extend(f'{rel}: Colab link to {path}, which the fork does not have' for path in sorted(set(missing)))
    return changed, problems


def main(argv):
    if '-h' in argv or '--help' in argv:
        print(__doc__)
        return 0
    check = '--check' in argv
    changed, problems = run(check)
    for p in problems:
        print('  !', p)
    if check:
        for rel in changed:
            print(f'  - {rel}: has Colab links to AllenDowney/ThinkPython (run fork_colab_links.py)')
        print('OK: every Colab link is the fork\'s' if not changed else f'{len(changed)} file(s) need fork_colab_links.py')
        return 1 if changed else 0
    print(f'rewrote Colab links in {len(changed)} file(s)' + (': ' + ', '.join(changed) if changed else ''))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
