"""JupyterLab 4 view of the v2 page (what Colab should show, approximately): screenshots of Q1, Q8 and Q17
with their Answers expanded, on open (stored outputs) and after Run All Cells; lists visible outputs.

    python shot_lab.py URL OUTDIR
"""
import json
import sys
from playwright.sync_api import sync_playwright

url, out = sys.argv[1], sys.argv[2]
JS_STATE = """() => {
  const nb = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden) .jp-Notebook');
  const cells = [...nb.querySelectorAll('.jp-Cell')];
  const shown = el => { for (let e = el; e && e !== nb; e = e.parentElement) {
      if (e.classList.contains('lm-mod-hidden') || e.classList.contains('jp-mod-hidden') ||
          getComputedStyle(e).display === 'none') return false; } return true; };
  const outs = cells.filter(c => c.classList.contains('jp-CodeCell')).flatMap(c =>
      [...c.querySelectorAll('.jp-OutputArea-output')].map(o => ({cell: cells.indexOf(c), shown: shown(o),
        text: o.innerText.slice(0, 50)})));
  return {cells: cells.length, shownCells: cells.filter(shown).length,
          outputs: outs.length, shownOutputs: outs.filter(o => o.shown),
          hiddenButtons: [...nb.querySelectorAll('.jp-showHiddenCellsButton')].filter(shown).map(b => b.innerText.trim()),
          prompts: [...nb.querySelectorAll('.jp-CodeCell .jp-InputPrompt')].map(p => p.innerText.trim()).join(' ')};
}"""


def heading_cell(pg, text):
    return pg.locator('.jp-MarkdownCell', has_text=text).first


def answer_of(pg, qtext):
    """The '#### Answer' heading cell that follows the question's heading cell."""
    return heading_cell(pg, qtext).locator(
        'xpath=following-sibling::*[contains(@class,"jp-MarkdownCell")][.//h4][1]')


def shot_region(pg, first, last_text_or_none, path, height=None):
    first.scroll_into_view_if_needed()
    pg.evaluate("el => el.scrollIntoView({block: 'start'})", first.element_handle())
    pg.wait_for_timeout(700)
    box = first.bounding_box()
    vh = pg.viewport_size['height']
    h = height or (vh - box['y'] - 5)
    pg.screenshot(path=path, clip={'x': box['x'] - 60, 'y': max(box['y'] - 5, 0), 'width': box['width'] + 70,
                                   'height': min(h, vh - box['y'])})
    print('saved', path)


def expand(pg, qtext):
    a = answer_of(pg, qtext)
    a.scroll_into_view_if_needed()
    btn = a.locator('.jp-showHiddenCellsButton')
    label = btn.first.inner_text().strip() if btn.count() else '(no button)'
    btn.first.click()
    pg.wait_for_timeout(800)
    return label


with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args=['--no-sandbox'])
    pg = b.new_page(viewport={'width': 1200, 'height': 1500})
    pg.goto(url)
    pg.wait_for_selector('.jp-NotebookPanel:not(.lm-mod-hidden) .jp-Notebook .jp-Cell', timeout=90000)
    pg.wait_for_timeout(5000)
    st = pg.evaluate(JS_STATE)
    print('ON OPEN:', json.dumps({k: v for k, v in st.items() if k != 'prompts'}, indent=1)[:1500])
    q1 = heading_cell(pg, 'Question 1 (easy)')
    shot_region(pg, q1, None, f'{out}/lab_open_q1_collapsed.png', 520)
    print('Q1 hidden-cells button:', expand(pg, 'Question 1 (easy)'))
    shot_region(pg, q1, None, f'{out}/lab_open_q1_expanded.png', 620)
    print('Q8 hidden-cells button:', expand(pg, 'Question 8 (medium)'))
    shot_region(pg, heading_cell(pg, 'Question 8 (medium)'), None, f'{out}/lab_open_q8_expanded.png', 1250)
    print('Q17 hidden-cells button:', expand(pg, 'Question 17 (hard)'))
    shot_region(pg, heading_cell(pg, 'Question 17 (hard)'), None, f'{out}/lab_open_q17_expanded.png', 1100)

    # fresh load, Run All Cells, then look
    pg.goto(url)
    pg.wait_for_selector('.jp-NotebookPanel:not(.lm-mod-hidden) .jp-Notebook .jp-Cell', timeout=90000)
    pg.wait_for_timeout(5000)
    pg.locator('.lm-MenuBar-itemLabel', has_text='Run').first.click()
    pg.locator('.lm-Menu-itemLabel', has_text='Run All Cells').first.click()
    for _ in range(180):
        pg.wait_for_timeout(1000)
        st = pg.evaluate(JS_STATE)
        if '[*]' not in st['prompts'] and '[ ]' not in st['prompts'] and '[ ]:' not in st['prompts']:
            break
    pg.wait_for_timeout(2000)
    st = pg.evaluate(JS_STATE)
    print('AFTER RUN ALL: prompts', st['prompts'])
    print('AFTER RUN ALL: shown outputs (outside collapsed Answers):', json.dumps(st['shownOutputs'], indent=1))
    print('Q8 hidden-cells button after Run All:', expand(pg, 'Question 8 (medium)'))
    shot_region(pg, heading_cell(pg, 'Question 8 (medium)'), None, f'{out}/lab_runall_q8_expanded.png', 1250)
    print('Q1 hidden-cells button after Run All:', expand(pg, 'Question 1 (easy)'))
    shot_region(pg, heading_cell(pg, 'Question 1 (easy)'), None, f'{out}/lab_runall_q1_expanded.png', 620)
    print('Q17 hidden-cells button after Run All:', expand(pg, 'Question 17 (hard)'))
    shot_region(pg, heading_cell(pg, 'Question 17 (hard)'), None, f'{out}/lab_runall_q17_expanded.png', 1100)
    b.close()
