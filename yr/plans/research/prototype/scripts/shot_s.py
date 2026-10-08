import sys
from playwright.sync_api import sync_playwright
P = sys.argv[1]
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args=['--no-sandbox'])
    pg = b.new_page(viewport={'width': 1280, 'height': 1000})
    pg.goto(f'file://{P}/out/jbS/_build/html/yr/chap05_review.html'); pg.wait_for_timeout(600)
    el = pg.locator('section#question-14-hard-infinite-recursion'); el.scroll_into_view_if_needed()
    el.locator('.admonition.dropdown .admonition-title').first.click(); pg.wait_for_timeout(400)
    el.screenshot(path=f'{P}/out/site_showrun_q14_open.png')
    b.close()
