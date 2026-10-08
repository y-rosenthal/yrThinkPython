"""Mutation self-test for check_v2.py: each mutation of the converted page must make the check fail with
the expected rule(s); the unmutated page must pass.

    python selftest_v2.py NB
"""
import copy
import re
import sys
from pathlib import Path

import nbformat as nbf

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from check_v2 import check
from review_v2 import parse_page, render_run_cell, source
import sync_v2


def cell_by_id(nb, cid):
    return next(c for c in nb.cells if c.id == cid)


def q(nb, n):
    return next(x for x in parse_page(nb) if x['title'].startswith(f'Question {n} '))


def run_cell(nb, n, k=0):
    return nb.cells[q(nb, n)['run_cells'][k]]


def run_block(nb, n, k=0):
    return nb.cells[q(nb, n)['run_blocks'][k][0]]


def answer_md(nb, n, k=0):
    return nb.cells[q(nb, n)['answer_md'][k]]


def m_block_edited(nb):
    c = run_block(nb, 8, 0)
    c.source = c.source.replace('if x = 5:', 'if x == 5:')


def m_block_edited_and_synced(nb):
    m_block_edited(nb)
    sync_v2.sync(nb, 'colablike')


def m_output_tampered(nb):
    o = run_cell(nb, 1).outputs[0]
    o['text'] = ''.join(o['text']).replace('2 15', '2 16')


def m_heading_in_answer(nb):
    answer_md(nb, 5).source += '\n\n#### Note\n\nmore'


def m_setext_in_answer(nb):
    answer_md(nb, 6).source += '\n\nNote\n----'


def m_html_heading_in_answer(nb):
    answer_md(nb, 7).source += '\n\n<h4>Note</h4>'


def m_duplicate_text_block(nb):
    answer_md(nb, 1).source = '```text\n2 15\n2 0 3\n3 -4\n```\n\n' + answer_md(nb, 1).source


def m_duplicate_error_block(nb):
    answer_md(nb, 14).source += "\n\n```text\nRecursionError: maximum recursion depth exceeded\n```"


def m_duplicate_picture(nb):
    answer_md(nb, 17).source += '\n\n<img data-turtle alt="Turtle drawing" width="300" src="data:image/png;base64,AAAA">'


def m_unwrapped_raising(nb):
    c = run_cell(nb, 8, 0)
    c.source = render_run_cell("x = 5\nif x = 5:\n    print('five')", False, 'a')


def m_wrapped_not_raising(nb):
    c = run_cell(nb, 1)
    code = source(c).split('\n', 1)[1]
    c.source = render_run_cell(code, True, None)


def m_collapsed_sections_missing(nb):
    nb.metadata['colab']['collapsed_sections'].pop(3)


def m_heading_not_collapsed(nb):
    h = nb.cells[q(nb, 2)['answer']]
    del h.metadata['jp-MarkdownHeadingCollapsed']


def m_code_not_hidden(nb):
    del run_cell(nb, 3).metadata['jupyter']


def m_error_name_wrong(nb):
    c = next(nb.cells[i] for i in q(nb, 14)['answer_md'] if 'RecursionError' in source(nb.cells[i]))
    c.source = c.source.replace('RecursionError', 'ValueError')


def m_error_name_missing(nb):
    c = nb.cells[q(nb, 8)['part_cells']['b']]
    c.source = c.source.replace(', so this is a `SyntaxError`', '')


def m_output_on_setup(nb):
    setup = next(c for c in nb.cells if c.cell_type == 'code' and c.metadata.get('tags') == ['setup'])
    setup.outputs = [nbf.v4.new_output('stream', name='stdout', text='Downloaded jupyturtle.py\n')]


def m_execution_count(nb):
    run_cell(nb, 2).execution_count = 5


def m_outputs_missing(nb):
    run_cell(nb, 17).outputs = []


def m_run_cells_swapped(nb):
    b, c = run_cell(nb, 8, 1), run_cell(nb, 8, 2)
    b.source, c.source = c.source, b.source
    b.outputs, c.outputs = c.outputs, b.outputs


def m_summary_moved(nb):
    x = q(nb, 8)
    summary = nb.cells.pop(x['run_cells'][-1] + 1)
    nb.cells.insert(x['run_cells'][-1], summary)


def m_tag_left(nb):
    run_cell(nb, 14).metadata['tags'] = ['raises-exception']


def m_run_code_edited(nb):
    c = next(c for c in nb.cells if source(c).startswith('def run_code('))
    c.source = c.source.replace("code = code.removeprefix('\\n')", 'pass')


def m_code_before_answer(nb):
    x = q(nb, 1)
    nb.cells.insert(x['answer'], nbf.v4.new_code_cell("print('2 15')"))


def m_no_credits(nb):
    nb.cells[-1].source = nb.cells[-1].source.replace('## Credits\n\n', '')


def m_label_on_single_block(nb):
    c = run_block(nb, 2)
    c.source = '**Part a**\n\n' + c.source


def m_definition_prints(nb):
    c = next(nb.cells[i] for i in q(nb, 14)['other_code'])
    c.source += "\n\nprint('defined')"


MUTATIONS = [
    (m_block_edited, 'S4', True), (m_block_edited_and_synced, 'S10', True), (m_output_tampered, 'R3', False),
    (m_heading_in_answer, 'S2', True), (m_setext_in_answer, 'S2', True), (m_html_heading_in_answer, 'S2', True),
    (m_duplicate_text_block, 'S9', True), (m_duplicate_error_block, 'S9', True), (m_duplicate_picture, 'S9', True),
    (m_unwrapped_raising, 'R1', False), (m_wrapped_not_raising, 'S11', True),
    (m_collapsed_sections_missing, 'S1', True), (m_heading_not_collapsed, 'S1', True), (m_code_not_hidden, 'S5', True),
    (m_error_name_wrong, 'S10', True), (m_error_name_missing, 'S10', True), (m_output_on_setup, 'S8', True),
    (m_execution_count, 'S8', True), (m_outputs_missing, 'R3', False), (m_run_cells_swapped, 'S4', True),
    (m_summary_moved, 'S6', True), (m_tag_left, 'S12', True), (m_run_code_edited, 'S12', True),
    (m_code_before_answer, 'S7', True), (m_no_credits, 'S12', True), (m_label_on_single_block, 'S3', True),
    (m_definition_prints, 'R4', False),
]


def main(path):
    base = nbf.read(path, as_version=4)
    fails = 0
    problems = check(copy.deepcopy(base), 'colablike')
    print(f'unmutated page: {"PASS" if not problems else "FAIL " + str(problems)}')
    fails += bool(problems)
    for fn, rule, static in MUTATIONS:
        nb = copy.deepcopy(base)
        fn(nb)
        problems = check(nb, 'colablike', static_only=static)
        hit = [p for p in problems if p.startswith(rule)]
        ok = bool(hit)
        fails += not ok
        rules = sorted({p.split(':')[0] for p in problems})
        print(f'{"caught" if ok else "MISSED"}  {fn.__name__:30} expect {rule:4} got {rules}  | {(hit or problems or ["-"])[0][:110]}')
    print(f'{len(MUTATIONS) - fails + (0 if fails else 0)} checks OK, {fails} failure(s)')
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1]))
