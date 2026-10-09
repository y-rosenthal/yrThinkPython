#!/usr/bin/env python3
"""Check the live site after a deploy. Stdlib only.

Usage: verify_live.py [--base URL] [--wait SECONDS]

Reads jb/_toc.yml for the pages, then checks on the live site that:
  - the home page and every page in the TOC load (HTTP 200);
  - chapter pages with code show outputs (chapter 5 must also show the stack diagram image in
    section 5.9, a page that only had outputs since the build started executing chapters);
  - yr/ review pages have both concept lists, Answer boxes and their turtle pictures, and show none of the
    notebook machinery (@title, run_code, markers).
Retries until --wait seconds have passed (GitHub Pages lags a minute or two behind the deploy).
Exit status 1 if anything is still wrong.
"""
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
args = sys.argv[1:]
BASE = args[args.index('--base') + 1] if '--base' in args else 'https://y-rosenthal.github.io/yrThinkPython/'
WAIT = int(args[args.index('--wait') + 1]) if '--wait' in args else 300


def fetch(url):
    req = urllib.request.Request(url, headers={'Cache-Control': 'no-cache'})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode('utf-8', 'replace')


def check():
    toc = (ROOT / 'jb' / '_toc.yml').read_text()
    pages = ['index'] + [f for f in re.findall(r'^\s*-\s*file:\s*(\S+)', toc, re.M) if f != 'index']
    problems, summary = [], []
    for page in pages:
        url = f'{BASE}{page}.html'
        try:
            html = fetch(url + f'?nocache={int(time.time())}')
        except urllib.error.URLError as e:
            problems.append(f'{page}: {e}')
            continue
        if re.fullmatch(r'chap(0[1-9]|1[0-8])', page):
            outputs = html.count('class="cell_output')
            summary.append(f'{page}:{outputs}')
            if outputs == 0:
                problems.append(f'{page}: no code outputs on the page')
            anchor = 'id="stack-diagrams-for-recursive-functions"'
            if page == 'chap05' and anchor in html:
                part = html.split(anchor, 1)[1][:6000]
                if '<img' not in part:
                    problems.append('chap05: no stack diagram image in section 5.9')
        if page.startswith('yr/'):
            for needed in ('Python Syntax and Semantics', 'Definitions, etc.', 'Answer'):
                if needed not in html:
                    problems.append(f'{page}: "{needed}" not found')
            src = (ROOT / f'{page}.ipynb').read_text()
            expected = src.count('<img data-turtle') + src.count('"review_drawing"')   # examples + stored drawings
            found = html.count('alt="Turtle drawing"')
            for bad in ('@title', 'run_code', '&lt;!--', '<!--=', 'generated imports', 'Using this page in Colab'):
                if bad in html:
                    problems.append(f'{page}: "{bad}" appears on the page')
            summary.append(f'{page}: {found}/{expected} pictures')
            if found < expected:
                problems.append(f'{page}: {found} turtle pictures on the page, {expected} in the notebook')
    return problems, summary


deadline = time.time() + WAIT
while True:
    problems, summary = check()
    if not problems or time.time() > deadline:
        break
    print(f'.. {len(problems)} problem(s), retrying in 30s (Pages may still be updating)')
    time.sleep(30)

print('outputs per chapter page:', ' '.join(s for s in summary if not s.startswith('yr/')))
for s in summary:
    if s.startswith('yr/'):
        print(s)
if problems:
    print(f'{len(problems)} problem(s):')
    for p in problems:
        print('  -', p)
    sys.exit(1)
print(f'OK: live site at {BASE} looks right')
