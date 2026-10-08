"""Assertions on the built review page (v2 chapter 5) and a text diff of its Answer dropdowns against the
baseline build of today's page. Needs bs4 and playwright (run with the venv-lab python).

    python verify_site.py NEW.html BASE.html NB
"""
import difflib
import json
import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).resolve().parent))
from review_v2 import ANSI, parse_page, semantic, site_traceback, text_of

new, base, nbpath = sys.argv[1:4]
nb = json.load(open(nbpath))
qs = parse_page(nb)
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
html = str(main)
check(len(drops) == len(qs), f'{len(drops)} "Answer" dropdowns for {len(qs)} questions')
check(all('toggle-shown' not in d.get('class', []) and not d.has_attr('open') for d in drops),
      'every Answer dropdown starts closed (class "dropdown" without "toggle-shown"; the concept lists keep toggle-shown)')
check(len(soup.select('div.dropdown.toggle-shown')) == 2, f'the two concept-list dropdowns are still shown open ({len(soup.select("div.dropdown.toggle-shown"))})')
check(not main.select('h4'), f'no h4 headings ({len(main.select("h4"))})')
toc = soup.select('.bd-toc a, nav.bd-links a, .page-toc a, #bd-toc-nav a')
toc_text = [a.get_text(strip=True) for a in toc]
check(not [t for t in toc_text if t in ('Answer', 'Credits', 'Output', 'Output of part a')], f'no Answer/Credits/Output entries in the right-hand contents ({len(toc_text)} entries)')
check('run_code' not in text and 'run_cell' not in text and 'get_ipython' not in text, 'no run_code / run_cell text on the page')
check('Using this page in Colab' not in text, 'no help note on the page')
check('@title' not in html and 'display-mode' not in html, 'no @title / display-mode text (hidden code) on the page')
check('<!-- error' not in html and 'error: SyntaxError' not in html, 'no <!-- error: --> records in the HTML')
check(not re.search(r'ipykernel_\d|<cell line|Traceback \(most recent call last\)|-{30}', text),
      'no traceback paths, "<cell line: 0>", banner or dashed line in the page text')
check('```' not in text and '~~~' not in text, 'no unrendered fences')
check(not re.search(r'\x1b\[|\[0;3\dm', html), 'no ANSI escape codes')
# every Answer of a question with run blocks shows each run cell's stored output, exactly once
missing = []
for k, q in enumerate(qs):
    for ri in q['run_cells']:
        outs = nb['cells'][ri]['outputs']
        if any(s[0] == 'drawing' for s in semantic(outs)):
            good = len(drops[k].select('img[alt="Turtle drawing"]')) == 1
        else:
            want = [ANSI.sub('', text_of(o['text'])).strip() for o in outs if o['output_type'] == 'stream'] + \
                   [site_traceback(o).strip() for o in outs if o['output_type'] == 'error']
            got = [pre.get_text().strip() for pre in drops[k].select('pre')]
            good = all(got.count(w) == 1 for w in want)
        if not good:
            missing.append(f'{q["title"][:12]} {nb["cells"][ri]["id"]}')
n_run = sum(len(q['run_cells']) for q in qs)
check(not missing, f'every run-block Answer shows each stored output exactly once ({n_run} run cells) {missing}')
q8 = drops[7].get_text('\n')
order = [q8.find(s) for s in ['Part a:', 'invalid syntax. Maybe', 'Part b:', "expected ':'", 'Part c:', 'unexpected indent',
                              'Python finds each']]
check(order == sorted(order) and -1 not in order, f'Q8 Answer interleaves Part a/b/c explanations with their outputs, summary last {order}')
check(q8.count('SyntaxError') == 2 and q8.count('IndentationError') == 1, 'Q8 names each error once (in the output only)')
imgs = drops[16].select('img')
check(len(imgs) == 1 and imgs[0]['src'].startswith('data:image/png') and imgs[0].get('alt') == 'Turtle drawing'
      and imgs[0].get('width') == '300', f'Q17 Answer shows exactly one picture: the stored drawing at width 300 ({len(imgs)} img)')
q14 = drops[13].get_text('\n')
check('RecursionError: maximum recursion depth exceeded' in q14 and q14.count('RecursionError') == 1,
      'Q14 Answer shows the RecursionError once (prose unchanged, no banner)')
# no output block wider than its box at desktop width, except where today's page already overflows as much
from playwright.sync_api import sync_playwright


def overflowing(page):
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path='/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args=['--no-sandbox'])
        pg = b.new_page(viewport={'width': 1300, 'height': 1000})
        pg.goto(Path(page).resolve().as_uri())
        pg.wait_for_timeout(1200)
        pg.evaluate("() => document.querySelectorAll('.dropdown .admonition-title').forEach(t => t.click())")
        pg.wait_for_timeout(400)
        wide = pg.evaluate("""() => [...document.querySelectorAll('.dropdown pre')].filter(p => p.scrollWidth > p.clientWidth + 2)
            .map(p => [(p.closest('section') || {id: '?'}).id.slice(0, 14), p.scrollWidth, p.clientWidth])""")
        b.close()
    return wide


wide_new, wide_base = overflowing(new), overflowing(base)
worse = [w for w in wide_new if not any(b[0] == w[0] and b[1] >= w[1] for b in wide_base)]
check(not worse, f'at 1300px no <pre> inside an Answer overflows more than on today\'s page (new {wide_new}, today {wide_base})')
# compare with the baseline page
_, bdrops = answers(base)
print('\nDropdown text, baseline (today) vs v2, per question (lines only in one of them):')
for k, (a, b) in enumerate(zip(bdrops, drops), 1):
    la = [l.strip() for l in a.get_text('\n').split('\n') if l.strip()]
    lb = [l.strip() for l in b.get_text('\n').split('\n') if l.strip()]
    d = [x for x in difflib.unified_diff(la, lb, lineterm='', n=0) if x[:1] in '+-' and not x.startswith(('+++', '---'))]
    print(f'Q{k}: ' + ('identical' if not d else f'{len(d)} changed line(s)'))
    for x in d[:16]:
        print('     ' + x[:150])
sys.exit(0 if ok else 1)
