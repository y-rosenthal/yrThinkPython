import sys, json
from playwright.sync_api import sync_playwright
out = sys.argv[1]
JS_STATE = """() => {
  const cells = [...document.querySelectorAll('.jp-NotebookPanel:not(.lm-mod-hidden) .jp-Notebook .jp-Cell')];
  const vis = c => c.offsetParent !== null && !c.classList.contains('lm-mod-hidden');
  const outs = [...document.querySelectorAll('.jp-Notebook .jp-OutputArea-output')];
  return {cells: cells.length, visibleCells: cells.filter(vis).length,
          outputs: outs.length, visibleOutputs: outs.filter(o => o.offsetParent !== null).map(o => o.innerText.slice(0, 60)),
          hiddenButtons: [...document.querySelectorAll('.jp-showHiddenCellsButton')].filter(b => b.offsetParent !== null).map(b => b.innerText.trim()).slice(0, 5),
          nHiddenButtons: [...document.querySelectorAll('.jp-showHiddenCellsButton')].filter(b => b.offsetParent !== null).length,
          execCounts: [...document.querySelectorAll('.jp-Notebook .jp-CodeCell .jp-InputPrompt')].map(p => p.innerText.trim()).join(' ')};
}"""
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args=['--no-sandbox'])
    pg = b.new_page(viewport={'width': 1280, 'height': 1000})
    pg.goto('http://127.0.0.1:8931/lab/workspaces/final/tree/chap05_review.ipynb?reset')
    pg.wait_for_selector('.jp-NotebookPanel:not(.lm-mod-hidden) .jp-Notebook .jp-Cell', timeout=60000)
    pg.wait_for_timeout(4000)
    print('ON OPEN:', json.dumps(pg.evaluate(JS_STATE), indent=1))
    q = pg.locator('.jp-MarkdownCell', has_text='Question 8 (medium): find the error').first
    q.scroll_into_view_if_needed(); pg.wait_for_timeout(500)
    pg.screenshot(path=f'{out}/lab_open_q8.png')
    # Run > Run All Cells
    pg.locator('.lm-MenuBar-itemLabel', has_text='Run').first.click()
    pg.locator('.lm-Menu-itemLabel', has_text='Run All Cells').first.click()
    for _ in range(120):
        pg.wait_for_timeout(1000)
        st = pg.evaluate(JS_STATE)
        if '[*]' not in st['execCounts'] and '[ ]' not in st['execCounts'] and st['outputs'] >= 13:
            break
    pg.wait_for_timeout(2000)
    st = pg.evaluate(JS_STATE)
    print('AFTER RUN ALL:', json.dumps(st, indent=1))
    q.scroll_into_view_if_needed(); pg.wait_for_timeout(500)
    pg.screenshot(path=f'{out}/lab_runall_q8.png')
    # expand Question 8's Answer
    ans = pg.locator('.jp-MarkdownCell', has_text='Question 8 (medium)').locator('xpath=following-sibling::*[contains(@class,"jp-MarkdownCell")][1]')
    print('hidden-cells button:', ans.locator('.jp-showHiddenCellsButton').first.evaluate('b => b.outerHTML.slice(0, 300) + " | text=" + b.textContent'))
    ans.locator('.jp-showHiddenCellsButton').first.click()
    pg.wait_for_timeout(800)
    q.scroll_into_view_if_needed(); pg.wait_for_timeout(300)
    pg.screenshot(path=f'{out}/lab_runall_q8_expanded.png', full_page=False)
    print('AFTER EXPANDING Q8 ANSWER:', json.dumps(pg.evaluate(JS_STATE)['visibleOutputs'], indent=1))
    b.close()
