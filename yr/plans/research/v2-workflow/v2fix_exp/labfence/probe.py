import sys
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args=['--no-sandbox'])
    pg = b.new_page(viewport={'width': 1200, 'height': 1200})
    pg.goto(sys.argv[1])
    pg.wait_for_selector('.jp-NotebookPanel:not(.lm-mod-hidden) .jp-Notebook .jp-Cell', timeout=90000)
    pg.wait_for_timeout(6000)
    r = pg.evaluate("""() => [...document.querySelectorAll('.jp-RenderedMarkdown')].map(m => ({
        first: m.innerText.slice(0, 22).replace(/\\n/g,' | '),
        codeClass: (m.querySelector('pre code')||{}).className,
        spans: m.querySelectorAll('pre span').length,
        html_comment_visible: m.innerText.includes('<!--') || m.innerText.includes('error:')}))""")
    for x in r: print(x)
    pg.screenshot(path=sys.argv[2], full_page=True)
    b.close()
