"""Self-test of the v2 tools: each mutation of the synced page must make check_v2 fail with the expected rule;
each repair scenario must end with a page that passes; sync must refuse what it should refuse.

    python selftest_v2.py NB
"""
import copy
import json
import re
import sys
from pathlib import Path

import nbformat as nbf

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from check_v2 import check
from review_v2 import make_stamp, normalize_text, parse_page, render_run_cell, semantic, source
import sync_v2

NOISE = {}


def q(nb, n):
    return next(x for x in parse_page(nb) if x['title'].startswith(f'Question {n} '))


def run_cell(nb, n, part=None):
    x = q(nb, n)
    return nb.cells[next(i for i in x['run_cells'] if part is None or x['run_part'][i] == part)]


def run_block(nb, n, k=0):
    return nb.cells[q(nb, n)['run_blocks'][k][0]]


def answer_md(nb, n, k=0):
    return nb.cells[q(nb, n)['answer_md'][k]]


def restamp(nb):
    """What a careful tamperer would do: recompute the sync stamp after editing."""
    nb.metadata['yr_review'] = make_stamp(nb, nb.metadata['yr_review']['stack'])


def md(text):
    return nbf.v4.new_markdown_cell(text)


def insert_question(nb, n, title, block, explanation, before=None, extra=()):
    """A new question (heading, run block(s), Answer heading, explanation) before question `before` (default:
    before the credits). No run cell: sync must create it."""
    pos = q(nb, before)['start'] if before else len(nb.cells) - 1
    blocks = [block] if isinstance(block, str) else block
    cells = [md(f'### Question {n} (hard): {title}\n\nPredict, then open the Answer to check.')]
    for k, b in enumerate(blocks):
        label = f'**Part {chr(97 + k)}**\n\n' if len(blocks) > 1 else ''
        cells.append(md(f'{label}~~~python\n{b}\n~~~'))
    cells += list(extra) + [md('#### Answer'), md(explanation)]
    nb.cells[pos:pos] = cells


def sync(nb, accept=True):
    report, refused, not_accepted, bad = sync_v2.sync(nb, 'colablike', accept=accept)
    assert not refused and not bad, (refused, bad)
    return report, not_accepted


DOCTEST = '''def count_e(word):
    """Count the letter e.

    >>> count_e('hello')
    1
    >>> count_e('eel')
    3
    """
    return word.count('e')

import doctest
doctest.run_docstring_examples(count_e, globals())'''

# ---------------------------------------------------------------- mutations: check must fail with a rule


def m_block_edited(nb):
    c = run_block(nb, 8, 0)
    c.source = c.source.replace('if x = 5:', 'if x == 5:')


def m_block_edited_and_synced(nb):
    m_block_edited(nb)
    sync(nb)                                    # accepted; the '<!-- error: SyntaxError -->' record now contradicts it


def m_static_normalize_stale(nb):
    c = run_block(nb, 1)
    c.source = c.source.replace('minutes = 135', 'minutes = 150')
    sync_v2.static_normalize(nb)                # regenerates the run cell, clears its outputs, no run


def m_output_tampered(nb):
    o = run_cell(nb, 1).outputs[0]
    o['text'] = o['text'].replace('2 15', '2 16')


def m_output_tampered_restamped(nb):
    m_output_tampered(nb)
    restamp(nb)


def m_plain_outputs_cleared(nb):
    run_cell(nb, 1).outputs = []


def m_outputs_missing(nb):
    run_cell(nb, 17).outputs = []


def m_wrong_stack(nb):
    nb.metadata['yr_review']['stack'] = {'python': '3.13.16', 'ipython': '9.17.1', 'ipykernel': '7.4.0'}


def m_never_synced(nb):
    del nb.metadata['yr_review']


def m_corrupt_png(nb):
    o = run_cell(nb, 17).outputs[0]
    o['data']['image/png'] = 'iVBORw0KGgo' + o['data']['image/png'][40:]
    restamp(nb)


def m_png_size(nb):
    run_cell(nb, 17).outputs[0]['metadata']['image/png']['width'] = 30
    restamp(nb)


def m_line_ref_plain(nb):
    o = run_cell(nb, 2).outputs[0]
    o['text'] += 'File "__main__", line 3\n'
    restamp(nb)


def m_heading_in_answer(nb):
    answer_md(nb, 5).source += '\n\n#### Note\n\nmore'


def m_setext_in_answer(nb):
    answer_md(nb, 6).source += '\n\nNote\n----'


def m_html_heading_in_answer(nb):
    answer_md(nb, 7).source += '\n\n<h4>Note</h4>'


def m_duplicate_text_block(nb):
    answer_md(nb, 1).source = '```text\n2 15\n2 0 3\n3 -4\n```\n\n' + answer_md(nb, 1).source


def m_near_duplicate_plain_fence(nb):
    answer_md(nb, 1).source += '\n\n```\n2 15\n2 0 3\n```'


def m_contradicting_block(nb):
    answer_md(nb, 1).source += '\n\nThe last line is:\n\n```text\n3 -3\n```'


def m_output_fence(nb):
    answer_md(nb, 3).source += '\n\n```output\n4 is even\n```'


def m_indented_block(nb):
    answer_md(nb, 3).source += '\n\nIt displays:\n\n    4 is even\n    7 is odd'


def m_duplicate_error_block(nb):
    c = next(nb.cells[i] for i in q(nb, 14)['answer_md'] if 'frames on the stack' in source(nb.cells[i]))
    c.source += "\n\n```text\nRecursionError: maximum recursion depth exceeded\n```"


def m_short_error_line_in_python_fence(nb):
    c = nb.cells[q(nb, 8)['part_cells']['b']]
    c.source += "\n\n```text\nSyntaxError: expected ':'\n```"


def m_duplicate_picture(nb):
    answer_md(nb, 17).source += ('\n\n<img data-turtle alt="Turtle drawing" width="300" src="data:image/png;base64,AAAA">'
                                 '\n\nThe same tree drawn with a loop:\n\n```python\nprint(1)\n```')


def m_pair_wrong_text(nb):
    answer_md(nb, 7, -1).source += "\n\nFor example:\n\n```python\nprint(7 // 2)\n```\n```text\n4\n```"


def m_unwrapped_raising(nb):
    run_cell(nb, 8, 'a').source = render_run_cell("x = 5\nif x = 5:\n    print('five')", False, 'a')


def m_wrapped_not_raising(nb):
    c = run_cell(nb, 1)
    c.source = render_run_cell(source(c).split('\n', 1)[1], True, None)


def m_collapsed_sections_missing(nb):
    nb.metadata['colab']['collapsed_sections'].pop(3)


def m_heading_not_collapsed(nb):
    del nb.cells[q(nb, 2)['answer']].metadata['jp-MarkdownHeadingCollapsed']


def m_code_not_hidden(nb):
    del run_cell(nb, 3).metadata['jupyter']


def m_colab_title(nb):
    c = run_cell(nb, 1)
    c.source = c.source.replace('# @title Output\n', '#@title Output { display-mode: "both" }\n')


def m_colab_metadata(nb):
    run_cell(nb, 2).metadata.update({'executionInfo': {'status': 'ok'}, 'outputId': 'abc'})


def m_error_name_wrong(nb):
    c = next(nb.cells[i] for i in q(nb, 14)['answer_md'] if 'RecursionError' in source(nb.cells[i]))
    c.source = c.source.replace('RecursionError', 'ValueError')


def m_error_name_missing(nb):
    c = nb.cells[q(nb, 8)['part_cells']['b']]
    c.source = re.sub(r'\n*<!-- error: SyntaxError -->', '', c.source)


def m_error_named_only_in_summary_wrongly(nb):
    nb.cells[max(q(nb, 8)['run_cells']) + 1].source += ' Part c is a `TypeError`.'


def m_output_on_setup(nb):
    setup = next(c for c in nb.cells if c.cell_type == 'code' and c.metadata.get('tags') == ['setup'])
    setup.outputs = [nbf.v4.new_output('stream', name='stdout', text='Downloaded jupyturtle.py\n')]


def m_execution_count(nb):
    run_cell(nb, 2).execution_count = 5


def m_run_cells_swapped(nb):
    b, c = run_cell(nb, 8, 'b'), run_cell(nb, 8, 'c')
    b.source, c.source = c.source, b.source
    b.outputs, c.outputs = c.outputs, b.outputs


def m_summary_moved(nb):
    x = q(nb, 8)
    summary = nb.cells.pop(max(x['run_cells']) + 1)
    nb.cells.insert(max(x['run_cells']), summary)


def m_tag_left(nb):
    run_cell(nb, 14).metadata['tags'] = ['raises-exception']


def m_old_marker(nb):
    c = run_block(nb, 2)
    c.source = c.source.replace('~~~python', '```python run').replace('\n~~~', '\n```')


def m_tilde_elsewhere(nb):
    answer_md(nb, 7, -1).source += '\n\n~~~python\nprint(1)\n~~~'


def m_param_in_block(nb):
    c = run_block(nb, 1)
    c.source = c.source.replace('minutes = 135', 'minutes = 135  # @param {type: "integer"}')


def m_cell_magic_in_block(nb):
    c = run_block(nb, 1)
    c.source = c.source.replace('~~~python\n', '~~~python\n%%time\n')


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


def m_part_added_without_text(nb):
    c = run_block(nb, 8, 2)
    nb.cells.insert(nb.cells.index(c) + 1, md('**Part d**\n\n~~~python\nx = 5\nprint(x +)\n~~~'))
    sync(nb)


def m_nameerror_bound_elsewhere(nb):
    insert_question(nb, 2, 'what is displayed?', 'print(total)', 'The name was never assigned.\n\n'
                    '<!-- error: NameError -->', before=2)
    c = next(nb.cells[i] for i in q(nb, 14)['other_code'])
    c.source += '\n\ntotal = 0'
    sync(nb)


MUTATIONS = [   # (function, rule that must report it, static only?)
    (m_block_edited, 'S4', True), (m_block_edited_and_synced, 'S10', True), (m_static_normalize_stale, 'S14', True),
    (m_output_tampered, 'S14', True), (m_output_tampered_restamped, 'R3', False), (m_plain_outputs_cleared, 'S14', True),
    (m_outputs_missing, 'S14', True), (m_wrong_stack, 'S14', True), (m_never_synced, 'S14', True),
    (m_corrupt_png, 'S17', True), (m_png_size, 'S17', True), (m_line_ref_plain, 'S11', True),
    (m_heading_in_answer, 'S2', True), (m_setext_in_answer, 'S2', True), (m_html_heading_in_answer, 'S2', True),
    (m_duplicate_text_block, 'S9', True), (m_near_duplicate_plain_fence, 'S9', True), (m_contradicting_block, 'S9', True),
    (m_output_fence, 'S9', True), (m_indented_block, 'S9', True), (m_duplicate_error_block, 'S9', True),
    (m_short_error_line_in_python_fence, 'S9', True), (m_duplicate_picture, 'S9', True), (m_pair_wrong_text, 'S13', False),
    (m_unwrapped_raising, 'R1', False), (m_wrapped_not_raising, 'S11', True),
    (m_collapsed_sections_missing, 'S1', True), (m_heading_not_collapsed, 'S1', True), (m_code_not_hidden, 'S5', True),
    (m_colab_title, 'S5', True), (m_colab_metadata, 'S5', True),
    (m_error_name_wrong, 'S10', True), (m_error_name_missing, 'S10', True), (m_error_named_only_in_summary_wrongly, 'S10', True),
    (m_output_on_setup, 'S8', True), (m_execution_count, 'S8', True), (m_run_cells_swapped, 'S6', True),
    (m_summary_moved, 'S6', True), (m_tag_left, 'S12', True), (m_old_marker, 'S19', True), (m_tilde_elsewhere, 'S19', True),
    (m_param_in_block, 'S16', True), (m_cell_magic_in_block, 'S16', True), (m_code_before_answer, 'S7', True),
    (m_no_credits, 'S12', True), (m_label_on_single_block, 'S3', True), (m_definition_prints, 'R4', False),
    (m_part_added_without_text, 'S20', True), (m_nameerror_bound_elsewhere, 'S18', True),
]

# ---------------------------------------------------------------- scenarios: a custom assertion each


def s_unit_tmpdir_path():
    t = normalize_text('File "/home/u/x/tmpx/ipykernel_11834/12.py", line 2; \x1b[0;32m/tmp/ipykernel_77/9.py\x1b[0m; '
                       'C:\\Users\\u\\AppData\\Local\\Temp\\ipykernel_5\\3.py')
    ok = t.count('/tmp/ipykernel_0/') == 3 and 'tmpx' not in t and '11834' not in t
    return ok, t[:120]


def s_unit_stream_coalesced(nb):
    from review_v2 import normalize_outputs
    outs = [{'output_type': 'stream', 'name': 'stdout', 'text': 'a\n'}, {'output_type': 'stream', 'name': 'stdout', 'text': 'b\n'}]
    n = normalize_outputs(outs)
    return len(n) == 1 and n[0]['text'] == 'a\nb\n', str(n)


def s_sync_refuses_unaccepted_change(nb):
    c = run_block(nb, 1)
    c.source = c.source.replace('minutes = 135', 'minutes = 150')
    before = json.dumps(nb, sort_keys=True)
    report, not_accepted = sync(nb, accept=False)
    return bool(not_accepted) and json.dumps(nb, sort_keys=True) == before, \
        (not_accepted[0].splitlines()[0][:110] if not_accepted else 'accepted silently')


def s_static_normalize_repairs_colab_save(nb):
    m_colab_title(nb)
    m_colab_metadata(nb)
    nb.cells[q(nb, 3)['answer']].metadata['colab'] = {'base_uri': 'https://localhost:8080/'}
    changes, errors = sync_v2.static_normalize(nb)
    p = check(nb, static_only=True)
    return not p and not errors, f'{len(changes)} repairs; remaining: {p[:2]}'


def s_new_questions(nb):
    """A new 'what is displayed' question whose output is split by timing, and a doctest question (line number in
    its output -> wrapped; the opening quote on its own line keeps IPython 9 from emptying the doctest)."""
    insert_question(nb, 18, 'what is displayed?', "import time\nprint('a')\ntime.sleep(0.6)\nprint('b')",
                    'Both lines are displayed, one after the other.')
    insert_question(nb, 19, 'what is displayed?', DOCTEST, 'The second example fails: `eel` has two letters e.')
    report, _ = sync(nb, accept=False)
    p = check(nb) + check(nb, 'bookvenv', semantic_ok=True)
    x18, x19 = q(nb, 18), q(nb, 19)
    r18, r19 = nb.cells[x18['run_cells'][0]], nb.cells[x19['run_cells'][0]]
    placed = x18['run_cells'][0] == x18['answer'] + 1
    one_stream = len(r18.outputs) == 1 and r18.outputs[0]['text'] == 'a\nb\n'
    wrapped = 'run_cell(' in source(r19) and 'line 6' in r19.outputs[0]['text']
    return not p and placed and one_stream and wrapped, \
        f'placed={placed} one_stream={one_stream} doctest wrapped & "line 6"={wrapped} problems={p[:2]}'


def s_part_added_and_removed(nb):
    c = run_block(nb, 8, 2)
    nb.cells.insert(nb.cells.index(c) + 1, md('**Part d**\n\n~~~python\nx = 5\nprint(x +)\n~~~'))
    rc = run_cell(nb, 8, 'c')
    nb.cells.insert(nb.cells.index(rc) + 1, md('**Part d:** An operator needs two operands:\n\n<!-- error: SyntaxError -->'))
    sync(nb, accept=False)
    x = q(nb, 8)
    added = len(x['run_cells']) == 4 and x['run_cells'][3] == x['part_cells']['d'] + 1
    p1 = check(nb)
    for idx in sorted([x['run_blocks'][3][0], x['part_cells']['d']], reverse=True):
        del nb.cells[idx]
    sync(nb, accept=False)
    removed = len(q(nb, 8)['run_cells']) == 3
    p2 = check(nb)
    return added and removed and not p1 and not p2, f'added={added} removed={removed} problems={(p1 + p2)[:2]}'


def s_sync_refuses_lost_value(nb):
    insert_question(nb, 18, 'what is displayed?', DOCTEST + "\ncount_e('eel')", 'Two letters e.')
    report, refused, _, _ = sync_v2.sync(nb, 'colablike')
    return any('not displayed when wrapped' in r for r in refused), (refused or ['not refused'])[0][-110:]


def s_sync_refuses_memory_address(nb):
    insert_question(nb, 18, 'what is displayed?', 'def f():\n    pass\n\nprint(f)', 'A function object.')
    report, refused, _, _ = sync_v2.sync(nb, 'colablike')
    return refused and all('memory address' in r for r in refused), (refused or ['not refused'])[0][-110:]


def s_sync_refuses_wrong_stack(nb):
    report, refused, _, _ = sync_v2.sync(nb, 'bookvenv')
    return any('pinned' in r for r in refused), (refused or ['not refused'])[0][:110]


SCENARIOS = [s_sync_refuses_unaccepted_change, s_static_normalize_repairs_colab_save, s_new_questions,
             s_part_added_and_removed, s_sync_refuses_lost_value, s_sync_refuses_memory_address,
             s_sync_refuses_wrong_stack, s_unit_stream_coalesced]


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
        fails += not hit
        rules = sorted({p.split(':')[0] for p in problems})
        print(f'{"caught" if hit else "MISSED"}  {fn.__name__:38} expect {rule:4} got {rules}  | {(hit or problems or ["-"])[0][:105]}')
    ok, msg = s_unit_tmpdir_path()
    fails += not ok
    print(f'{"ok    " if ok else "FAILED"}  {"s_unit_tmpdir_path":38} | {msg}')
    for fn in SCENARIOS:
        ok, msg = fn(copy.deepcopy(base))
        fails += not ok
        print(f'{"ok    " if ok else "FAILED"}  {fn.__name__:38} | {msg}')
    total = len(MUTATIONS) + len(SCENARIOS) + 2
    print(f'{total - fails}/{total} self-tests OK ({len(MUTATIONS)} mutations, {len(SCENARIOS) + 1} scenarios, unmutated page)')
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1]))
