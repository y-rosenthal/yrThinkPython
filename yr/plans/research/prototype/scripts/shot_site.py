import sys
from playwright.sync_api import sync_playwright
url, outdir = sys.argv[1], sys.argv[2]
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args=['--no-sandbox'])
    pg = b.new_page(viewport={'width': 1280, 'height': 900})
    pg.goto(url)
    pg.wait_for_timeout(800)
    for q, sec in [('8', 'question-8-medium-find-the-error'), ('14', 'question-14-hard-infinite-recursion'), ('17', 'question-17-hard-what-is-drawn')]:
        el = pg.locator(f'section#{sec}')
        el.scroll_into_view_if_needed()
        el.screenshot(path=f'{outdir}/site_q{q}_collapsed.png')
        # open its Answer dropdown
        el.locator('.admonition.dropdown .admonition-title, details.dropdown summary').first.click()
        pg.wait_for_timeout(400)
        el.screenshot(path=f'{outdir}/site_q{q}_open.png')
    # top of the questions section, plus right-hand TOC
    pg.locator('section#question-1-easy-what-is-displayed').scroll_into_view_if_needed()
    pg.screenshot(path=f'{outdir}/site_viewport_q1.png')
    b.close()
