"""Check a converted review page on the built website, and compare it with a build of the page before conversion.

    python verify_site.py jb/_build/html/yr/chapNN_review.html yr/chapNN_review.ipynb [BEFORE.html]

Run after build_book.sh (needs bs4, which jupyter-book installs). Checks that:
  - there is one "Answer" dropdown per question, and every one is closed (the concept lists stay open);
  - no h4 headings, and no "Answer" or "Credits" entries in the page's contents;
  - none of the notebook machinery reaches the page: run_code, @title, the help note, markers, region
    delimiters, traceback paths and banners, ANSI codes, unrendered fences;
  - each run cell's stored output appears in its Answer (a note if a fix in the Answer shows it again).
With BEFORE.html (the page built from the old format), prints each Answer's lines that changed (E20 diff gate:
only intended changes may appear). Exit status 1 if a check fails.
"""
import difflib
import json
import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).resolve().parent))
import review_format as rf  # noqa: E402

ok = True


def check(cond, msg):
    global ok
    ok &= bool(cond)
    print(('PASS ' if cond else 'FAIL ') + msg)


def answers(path):
    soup = BeautifulSoup(Path(path).read_text(encoding='utf-8'), 'html.parser')
    drops = [d for d in soup.select('details.dropdown, div.dropdown')
             if (d.select_one('summary, .admonition-title') or d).get_text(' ', strip=True).startswith('Answer')]
    return soup, drops


def lines(el):
    return [x.strip() for x in el.get_text('\n').split('\n') if x.strip()]


def main(argv):
    if len(argv) < 2:
        sys.exit(__doc__)
    html_path, nb_path = argv[0], argv[1]
    nb = json.loads(Path(nb_path).read_text(encoding='utf-8'))
    qs = [q for q in rf.parse_page(nb) if q['answer'] is not None]
    soup, drops = answers(html_path)
    main_el = soup.select_one('main') or soup
    text, html = main_el.get_text('\n'), str(main_el)
    check(len(drops) == len(qs), f'{len(drops)} "Answer" dropdowns for {len(qs)} questions with an Answer')
    check(all('toggle-shown' not in d.get('class', []) and not d.has_attr('open') for d in drops),
          'every Answer dropdown starts closed')
    check(not main_el.select('h4'), f'no h4 headings ({len(main_el.select("h4"))})')
    toc = [a.get_text(strip=True) for a in soup.select('.bd-toc a, .page-toc a, #bd-toc-nav a')]
    check(not [t for t in toc if t in ('Answer', 'Credits') or t.startswith('Output')],
          'no Answer, Credits or Output entries in the page contents')
    check('run_code' not in text and 'get_ipython' not in text, 'no run_code text on the page')
    check('Using this page in Colab' not in text, 'no help note on the page')
    check('@title' not in html, 'no @title (hidden code) on the page')
    check(not re.search(r'&lt;!--|<!--=|<!-- (begin|end) generated|generated imports', html),
          'no markers or region delimiters in the HTML')
    check(not re.search(r'ipykernel_\d|<cell line|Traceback \(most recent call last\)|-{30}', text),
          'no traceback paths, "<cell line: 0>", banner or dashed line')
    check('```' not in text and '~~~' not in text, 'no unrendered fences')
    check(not re.search(r'\x1b\[|\[0;3\dm', html), 'no ANSI escape codes')
    missing = []
    for q, d in zip(qs, drops):
        for ri in q['run_cells']:
            outs = nb['cells'][ri].get('outputs', [])
            if any(o.get('metadata', {}).get('review_drawing') for o in outs):
                good = len(d.select('img[alt="Turtle drawing"]')) >= 1
            else:
                want = [rf.ANSI.sub('', rf.stream_text(outs, 'stdout')).strip()]
                want = [w for w in want if w]
                got = '\n'.join(pre.get_text() for pre in d.select('pre'))
                good = all(got.count(w) >= 1 for w in want)
                if any(got.count(w) > 1 for w in want):
                    print(f'note: {q["title"][:30]}: a run cell\'s output appears more than once (a fix or variant in '
                          f'the Answer shows the same output)')
            if not good:
                missing.append(f'{q["title"][:14]} ({nb["cells"][ri]["id"]})')
    check(not missing, f'each run cell\'s stored output appears in its Answer {missing}')
    if len(argv) > 2:
        _, before = answers(argv[2])
        print('\nAnswer text, before vs after conversion (lines only in one of them):')
        for q, a, b in zip(qs, before, drops):
            d = [x for x in difflib.unified_diff(lines(a), lines(b), lineterm='', n=0)
                 if x[:1] in '+-' and not x.startswith(('+++', '---'))]
            print(f'{q["title"][:30]}: ' + ('identical' if not d else f'{len(d)} changed line(s)'))
            for x in d[:20]:
                print('     ' + x[:150])
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
