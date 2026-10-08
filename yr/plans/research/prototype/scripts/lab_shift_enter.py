import json
from playwright.sync_api import sync_playwright
JS = """() => { const p = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden)');
  const cells = [...p.querySelectorAll('.jp-Notebook .jp-Cell')];
  const act = cells.findIndex(c => c.classList.contains('jp-mod-active'));
  return {active: act, activeText: cells[act] ? cells[act].innerText.slice(0, 50) : null,
          visible: cells.filter(c => c.offsetParent !== null).length,
          visibleOutputs: [...p.querySelectorAll('.jp-OutputArea-output')].filter(o => o.offsetParent !== null).length}; }"""
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args=['--no-sandbox'])
    pg = b.new_page(viewport={'width': 1280, 'height': 1000})
    pg.goto('http://127.0.0.1:8931/lab/workspaces/se/tree/chap05_review.ipynb?reset')
    pg.wait_for_selector('.jp-NotebookPanel:not(.lm-mod-hidden) .jp-Notebook .jp-Cell', timeout=60000); pg.wait_for_timeout(3000)
    # restart kernel & clear outputs state: use the reloaded file (no outputs saved); click the Question 1 cell
    pg.locator('.jp-NotebookPanel:not(.lm-mod-hidden) .jp-MarkdownCell', has_text='Question 1 (easy)').first.click()
    pg.keyboard.press('Escape')
    print('start:', pg.evaluate(JS))
    for k in range(8):
        pg.keyboard.press('Shift+Enter'); pg.wait_for_timeout(1200)
        print(f'after Shift+Enter #{k+1}:', json.dumps(pg.evaluate(JS)))
    pg.screenshot(path='out/lab_shift_enter.png')
    b.close()
