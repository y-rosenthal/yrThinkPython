"""`review.sh selftest`: prove that sync and check work, on selftest/fixture.ipynb (every kind of question).

1. sync a copy of the fixture: it must succeed, and a second sync must change nothing;
2. check the synced copy: it must pass;
3. break the synced copy in many ways (one at a time): check must fail each time, naming the rule that the
   break violates;
4. small unit tests of the format module (run-cell round trip, error lines after Colab's NOTE, markers).
Exit status 1 if anything is not as expected.
"""
import copy
import io
import json
import re
import sys
import tempfile
from contextlib import redirect_stdout
from pathlib import Path

import nbformat as nbf

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import check_review as cr  # noqa: E402
import review_format as rf  # noqa: E402
import sync_review as sr  # noqa: E402

FIXTURE = HERE / 'selftest' / 'fixture.ipynb'
failures = []


def cell(nb, cid):
    return next(c for c in nb.cells if c.id == cid)


def run_cell_of(nb, number, part=None):
    title = '# @title ' + rf.title_for(number, part)
    return next(c for c in nb.cells if c.cell_type == 'code' and rf.source(c).startswith(title + '\n'))


def restamp(nb):
    nb.metadata[rf.STAMP_KEY] = rf.make_stamp(nb, nb.metadata[rf.STAMP_KEY]['stack'])


def edit(nb, cid, old, new):
    c = cell(nb, cid)
    assert old in rf.source(c), (cid, old)
    c.source = rf.source(c).replace(old, new, 1)


# Each mutation: (name, rule that must fail, static only?, function that breaks a copy of the synced page)
def m_output(nb):
    run_cell_of(nb, '1').outputs[0]['text'] = '2 16\n'


def m_output_restamped(nb):
    m_output(nb)
    restamp(nb)


def m_run_block(nb):
    edit(nb, 'q1run000', 'minutes = 135', 'minutes = 136')


def m_region(nb):
    edit(nb, 'q3head00', '```text\n12\n3\n```', '```text\n12\n4\n```')


def m_region_restamped(nb):
    m_region(nb)
    restamp(nb)


def m_value(nb):
    edit(nb, 'q1expl00', '<!--=-->`2`', '<!--=-->`3`')


def m_value_restamped(nb):
    m_value(nb)
    restamp(nb)


def m_collapse(nb):
    cell(nb, 'q1answer').metadata.pop('jp-MarkdownHeadingCollapsed')
    nb.metadata['colab']['collapsed_sections'].remove('q1answer')


def m_marker_starts_line(nb):
    edit(nb, 'q1expl00', '135 minutes is 2 hours', '<!--= 1 + 1 -->`2` hours, then 135 minutes is 2 hours')


def m_text_block(nb):
    edit(nb, 'q1expl00', '135 minutes', '```text\n2 15\n```\n\n135 minutes')


def m_error_marker(nb):
    edit(nb, 'q2partb0', 'then a <!--=error-->`NameError`', 'then an error')


def m_error_wrong_name(nb):
    edit(nb, 'q2parta0', 'so this is a', 'not a TypeError, so this is a')


def m_todo(nb):
    edit(nb, 'q3expl00', 'Use `%`', 'TODO Use `%`')


def m_tag(nb):
    run_cell_of(nb, '1').metadata['tags'] = ['raises-exception']


def m_duplicate_number(nb):
    edit(nb, 'q3bhead0', 'Question 3b', 'Question 3')


def m_letter_clash(nb):
    edit(nb, 'q3bhead0', 'Question 3b', 'Question 2b')


def m_missing_import(nb):
    edit(nb, 'q4expl00', '<!-- generated imports: 1 -->\n```python\nfrom jupyturtle import left\n\n', '```python\n')
    restamp(nb)


def m_definition_prints(nb):
    cell(nb, 'q4def000').source = rf.source(cell(nb, 'q4def000')) + "\nprint('defined')"


def m_code_in_answer(nb):
    i = nb.cells.index(cell(nb, 'q1expl00'))
    nb.cells.insert(i + 1, nbf.v4.new_code_cell("print('extra')"))
    nb.cells[i + 1].id = 'extra000'


def m_nameerror_false(nb):
    cell(nb, 'q4def000').source = rf.source(cell(nb, 'q4def000')) + '\nundefined_name = 1'


def m_drawing(nb):
    o = run_cell_of(nb, '5').outputs[0]
    o['data']['image/png'] = o['data']['image/png'][:-8] + 'AAAAAAA='


def m_hazard(nb):
    edit(nb, 'q1expl00', '135 minutes', '(c) 135 minutes')


def m_credits(nb):
    nb.cells[-1].source = rf.source(nb.cells[-1]).replace('Downey', 'Downy')


def m_wrong_example(nb):
    m_region_restamped(nb)


def m_fix_needs_input(nb):
    edit(nb, 'q6expl00', 'price = 4\nprint(price * 2)', 'print(price * 2)')
    restamp(nb)


def m_unwrapped_error(nb):
    c = run_cell_of(nb, '7')
    c.source = '# @title Output of Question 7\n' + rf.parse_run_cell(rf.source(c))['code']
    restamp(nb)


def m_help_note(nb):
    c = next(c for c in nb.cells if rf.is_help_note(c))
    c.source = rf.source(c).replace('Run anyway', 'Run')


MUTATIONS = [
    ('stored output edited', '9', True, m_output),
    ('stored output edited and stamp recomputed', '11', False, m_output_restamped),
    ('run block edited without sync', '9', True, m_run_block),
    ('example output edited', '9', True, m_region),
    ('example output edited and stamp recomputed', '11', False, m_region_restamped),
    ('example output edited: the solution does not reproduce it (C4)', '12', False, m_wrong_example),
    ('value edited', '9', True, m_value),
    ('value edited and stamp recomputed', '11', False, m_value_restamped),
    ('Answer not saved collapsed', '3', True, m_collapse),
    ('value marker starts a line', '10', True, m_marker_starts_line),
    ('output typed by hand in an Answer', '7', True, m_text_block),
    ('error not named with <!--=error-->', '8', True, m_error_marker),
    ('Answer names an error its part does not raise', '8', True, m_error_wrong_name),
    ('TODO left', '16', True, m_todo),
    ('tag not allowed', '14', True, m_tag),
    ('duplicate question number', '1', True, m_duplicate_number),
    ('Question 2b while Question 2 has a part b', '2', True, m_letter_clash),
    ('Answer block lost its import line', '12', True, m_missing_import),
    ('definition cell displays something', '5', True, m_definition_prints),
    ('code cell inside an Answer', '6', True, m_code_in_answer),
    ('a NameError answer made false', '13', True, m_nameerror_false),
    ('drawing PNG edited', '9', True, m_drawing),
    ('(c) in prose', '16', True, m_hazard),
    ('credits edited', '14', True, m_credits),
    ('help note edited', '14', True, m_help_note),
    ('fix lost its input line (E10)', '12', False, m_fix_needs_input),
    ('error run cell not wrapped', '11', False, m_unwrapped_error),
]


def unit_tests():
    code = "x = 5\nif x = 5:\n    print('five')"
    for wrapped in (False, True):
        src = rf.render_run_cell(code, wrapped, '8', 'a')
        info = rf.parse_run_cell(src)
        if (info['code'], info['wrapped'], info['title']) != (code, wrapped, 'Output of Question 8a'):
            failures.append(f'unit: run cell round trip (wrapped={wrapped}): {info}')
    if rf.title_for('3b', 'a') != 'Output of Question 3b, part a':
        failures.append('unit: title of a lettered question with parts')
    if rf.run_cell_part({'title': 'Output of Question 3b, part a'}, '3b') != 'a' or \
            rf.run_cell_part({'title': 'Output of Question 8a'}, '8') != 'a' or \
            rf.run_cell_part({'title': 'Output of Question 8a'}, '8a') is not None:
        failures.append('unit: run_cell_part')
    note = ("\x1b[0;31mModuleNotFoundError\x1b[0m: No module named 'nope'\n\n"
            "---------------------------------------------------------------------------\n"
            "NOTE: If your import is failing due to a missing package, you can\nmanually install dependencies using "
            "either !pip or !apt.\n\nTo view examples of installing some common dependencies, click the\n"
            "\"Open Examples\" button below.\n---------------------------------------------------------------------------\n")
    if rf.raised([{'output_type': 'stream', 'name': 'stderr', 'text': note}]) != ['ModuleNotFoundError']:
        failures.append("unit: the error line after Colab's NOTE")
    if rf.raised([{'output_type': 'stream', 'name': 'stdout', 'text': 'TypeError: printed, not raised\n'}]):
        failures.append('unit: stdout text taken for an error')
    if not rf.marker_problems('- <!--= 1 + 1 -->`2` is two'):
        failures.append('unit: a value marker that starts a list item')
    if rf.marker_problems('`1 + 1` is <!--=-->`2`, and <!--= 2 * 2 -->`4`.\n<!-- not a solution -->'):
        failures.append('unit: well-formed markers reported')
    if not rf.marker_problems('Some <!-- remark --> text'):
        failures.append('unit: unknown comment not reported')


def run_check(path, static):
    buf = io.StringIO()
    with redirect_stdout(buf):
        problems = cr.check(path, static_only=static)
    return problems


def main():
    unit_tests()
    with tempfile.TemporaryDirectory() as tmp:
        page = Path(tmp) / 'chap99_review.ipynb'
        page.write_bytes(FIXTURE.read_bytes())
        print('>> sync the fixture')
        r = sr.sync(nbf.read(page, as_version=4), page)
        if r.refused or r.not_accepted or r.nb is None:
            print('\n'.join(r.refused + r.not_accepted))
            sys.exit('selftest: sync of the fixture failed')
        nbf.write(r.nb, page)
        synced = page.read_text()
        r2 = sr.sync(nbf.read(page, as_version=4), page)
        if r2.report or r2.nb is None or nbf.writes(r2.nb) + '\n' != synced and nbf.writes(r2.nb) != synced:
            failures.append(f'a second sync changes the page: {r2.report[:5]} {r2.refused[:3]}')
        print('>> check the synced fixture')
        problems = run_check(page, False)
        if problems:
            failures.append('check fails on the synced fixture:\n    ' + '\n    '.join(problems))
        base = nbf.read(page, as_version=4)
        for name, rule, static, mutate in MUTATIONS:
            nb = copy.deepcopy(base)
            mutate(nb)
            bad = Path(tmp) / 'chap99_review.ipynb'
            nbf.write(nb, bad)
            problems = run_check(bad, static)
            hit = [p for p in problems if p.startswith(f'{rule}:')]
            print(f'   {"ok  " if hit else "MISS"} {name} (rule {rule}){"" if hit else ": " + "; ".join(problems)[:300]}')
            if not hit:
                failures.append(f'mutation "{name}" was not reported as rule {rule}: {problems[:3]}')
            page.write_text(synced)
    if failures:
        print(f'SELFTEST FAILED ({len(failures)}):\n  - ' + '\n  - '.join(failures))
        return 1
    print(f'SELFTEST OK: sync is stable, check passes, and {len(MUTATIONS)} mutations are caught')
    return 0


if __name__ == '__main__':
    sys.exit(main())
