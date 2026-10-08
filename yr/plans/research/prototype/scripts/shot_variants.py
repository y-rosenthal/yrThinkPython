import sys
from playwright.sync_api import sync_playwright
P = sys.argv[1]
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args=['--no-sandbox'])
    pg = b.new_page(viewport={'width': 1280, 'height': 1000})
    for k in 'BC':
        pg.goto(f'file://{P}/out/jb{k}/_build/html/yr/chap05_review.html'); pg.wait_for_timeout(600)
        el = pg.locator('section#question-8-medium-find-the-error'); el.scroll_into_view_if_needed()
        el.screenshot(path=f'{P}/out/site_dry_{k}_q8.png')
        pg = b.new_page(viewport={'width': 1280, 'height': 1000}); pg.goto(f'http://127.0.0.1:8931/lab/workspaces/w{k}/tree/dry_{k}.ipynb?reset'); pg.wait_for_selector('.jp-NotebookPanel:not(.lm-mod-hidden) .jp-Notebook .jp-Cell', timeout=60000); pg.wait_for_timeout(3000)
        q = pg.locator('.jp-NotebookPanel:not(.lm-mod-hidden) .jp-MarkdownCell', has_text='Question 8 (medium): find the error').first
        q.scroll_into_view_if_needed(); pg.wait_for_timeout(300)
        pg.mouse.wheel(0, 0)
        q.evaluate('e => e.scrollIntoView({block: "start"})'); pg.wait_for_timeout(500)
        pg.screenshot(path=f'{P}/out/lab_dry_{k}_q8.png')
    b.close()
