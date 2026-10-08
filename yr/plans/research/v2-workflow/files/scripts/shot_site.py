"""Screenshot review-page questions on the built website with their Answer dropdowns OPENED.

    python shot_site.py PAGE.html OUTDIR PREFIX Q [Q ...]
"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

page, outdir, prefix, qs = sys.argv[1], Path(sys.argv[2]), sys.argv[3], sys.argv[4:]
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args=['--no-sandbox'])
    pg = b.new_page(viewport={'width': 1300, 'height': 1000}, device_scale_factor=1)
    pg.goto(Path(page).resolve().as_uri())
    pg.wait_for_timeout(1500)
    # the sticky header would cover part of an element screenshot
    pg.add_style_tag(content='.skip-link{display:none!important} header, .bd-header, .bd-header-article'
                             '{position:static!important}')
    for q in qs:
        sec = pg.locator(f'section[id^="question-{q}-"]').first
        sec.scroll_into_view_if_needed()
        title = sec.locator('.dropdown .admonition-title', has_text='Answer').first
        title.click()
        pg.wait_for_timeout(600)
        sec.screenshot(path=str(outdir / f'{prefix}_q{q}_open.png'))
        print('saved', outdir / f'{prefix}_q{q}_open.png')
    b.close()
