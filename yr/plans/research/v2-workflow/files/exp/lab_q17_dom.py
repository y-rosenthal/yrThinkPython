import sys
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args=['--no-sandbox'])
    pg = b.new_page(viewport={'width': 1200, 'height': 1500})
    pg.goto(sys.argv[1])
    pg.wait_for_selector('.jp-NotebookPanel .jp-Notebook .jp-Cell', timeout=90000)
    pg.wait_for_timeout(5000)
    a = pg.locator('.jp-MarkdownCell', has_text='Question 17 (hard)').first.locator('xpath=following-sibling::*[contains(@class,"jp-MarkdownCell")][.//h4][1]')
    a.scroll_into_view_if_needed(); a.locator('.jp-showHiddenCellsButton').first.click(); pg.wait_for_timeout(1000)
    print(pg.evaluate("""() => { const cs=[...document.querySelectorAll('.jp-CodeCell')]; const c=cs[cs.length-1];
      const o=c.querySelector('.jp-OutputArea-output'); return o ? o.outerHTML.slice(0,600) : 'no output'; }"""))
    b.close()
