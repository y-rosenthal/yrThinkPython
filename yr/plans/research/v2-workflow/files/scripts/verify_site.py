"""Assertions on the built review page (v2 chapter 5) and a text diff of its Answer dropdowns against the
baseline build of today's page.

    python verify_site.py NEW.html BASE.html NB
"""
import json, re, sys, html as H
from bs4 import BeautifulSoup

new, base, nbpath = sys.argv[1:4]
nb = json.load(open(nbpath))
nq = sum(1 for c in nb['cells'] if c['cell_type'] == 'markdown' and ''.join(c['source']).startswith('### Question'))
ok = True


def check(cond, msg):
    global ok
    ok &= bool(cond)
    print(('PASS ' if cond else 'FAIL ') + msg)


def answers(path):
    soup = BeautifulSoup(open(path).read(), 'html.parser')
    drops = [d for d in soup.select('details.dropdown, div.dropdown')
             if (d.select_one('summary, .admonition-title') or d).get_text(' ', strip=True).startswith('Answer')]
    return soup, drops


soup, drops = answers(new)
main = soup.select_one('main') or soup
text = main.get_text('\n')
check(len(drops) == nq, f'{len(drops)} "Answer" dropdowns for {nq} questions')
check(all('toggle-shown' not in d.get('class', []) and not d.has_attr('open') for d in drops),
      'every Answer dropdown starts closed (class "dropdown" without "toggle-shown"; the concept lists keep toggle-shown)')
check(len(soup.select('div.dropdown.toggle-shown')) == 2, f'the two concept-list dropdowns are still shown open ({len(soup.select("div.dropdown.toggle-shown"))})')
check(not main.select('h4'), f'no h4 headings ({len(main.select("h4"))})')
toc = soup.select('.bd-toc a, nav.bd-links a, .page-toc a, #bd-toc-nav a')
toc_text = [a.get_text(strip=True) for a in toc]
check(not [t for t in toc_text if t in ('Answer', 'Credits', 'Output', 'Output of part a')], f'no Answer/Credits/Output entries in the right-hand contents ({len(toc_text)} entries)')
check('def run_code' not in text and 'run_code(' not in text, 'no run_code text on the page')
check('Using this page in Colab' not in text, 'no help note on the page')
check('@title' not in text and 'display-mode' not in text, 'no @title / display-mode text (hidden code) on the page')
check('```' not in text, 'no unrendered fences')
q8 = drops[7].get_text('\n')
check(q8.count('SyntaxError: invalid syntax. Maybe you meant') == 1 and q8.count("SyntaxError: expected ':'") == 1
      and q8.count('IndentationError: unexpected indent') == 1, 'Q8 Answer shows each of the three errors exactly once')
order = [q8.find(s) for s in ['Part a:', 'invalid syntax. Maybe', 'Part b:', "expected ':'", 'Part c:', 'unexpected indent', 'Each is found']]
check(order == sorted(order) and -1 not in order, f'Q8 Answer interleaves Part a/b/c explanations with their outputs, summary last {order}')
check(drops[0].get_text('\n').count('2 15') == 1, 'Q1 Answer shows the output once')
check(drops[16].select('svg line'), f'Q17 Answer contains the stored drawing ({len(drops[16].select("svg line"))} <line> elements)')
check(not drops[16].select('img'), 'Q17 Answer has no PNG picture any more')
check('RecursionError: maximum recursion depth exceeded' in drops[13].get_text('\n'), 'Q14 Answer shows the RecursionError traceback')
check(not re.search(r'\x1b\[|\[0;3\dm', str(main)), 'no ANSI escape codes')
# compare with the baseline page
_, bdrops = answers(base)
print('\nDropdown text, baseline (today) vs v2, per question (lines only in one of them):')
import difflib
for k, (a, b) in enumerate(zip(bdrops, drops), 1):
    la = [l.strip() for l in a.get_text('\n').split('\n') if l.strip()]
    lb = [l.strip() for l in b.get_text('\n').split('\n') if l.strip()]
    d = [x for x in difflib.unified_diff(la, lb, lineterm='', n=0) if x[:1] in '+-' and not x.startswith(('+++', '---'))]
    print(f'Q{k}: ' + ('identical' if not d else f'{len(d)} changed line(s)'))
    for x in d[:14]:
        print('     ' + x[:150])
sys.exit(0 if ok else 1)
