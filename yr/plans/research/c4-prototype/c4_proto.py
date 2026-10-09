"""Prototype of check C4 (plan section 4.4) on the 11 fix blocks, 2026-10-09.

C4: after Run all, each Answer code block (trimmed: no example calls, example inputs or provided
helpers) runs in the page's namespace with the setup cell's imported names removed, and must print
what the Answer says. Run from the repo root with the book venv:
    python ../yrThinkPython-research/yr/plans/research/c4-prototype/c4_proto.py
"""
import ast, json, re, sys
from jupyter_client.manager import start_new_kernel

# Trimmed Answer blocks as the v3 design writes them, with the output each must print.
# 'then' = the question's own call lines, run after the block (a block that only redefines a function).
CASES = [
    ('02', '4',  'fix, keeps its input line (E10)', 'price = 4\nprint(price * 2)\nprint(price * 3)', '', '8\n12'),
    ('02', '15', 'fix, changed lines only',         'average = (score1 + score2 + score3) / 3\nprint(average)', '', '80.0'),
    ('05', '7',  'alternative, def only',           "def describe(x):\n    if 0 < x < 10:\n        print(x, 'is a positive single digit')\n    elif x <= 0:\n        print(x, 'is not positive')\n    else:\n        print(x, 'is 10 or more')",
     'describe(5)\ndescribe(-3)\ndescribe(10)', '5 is a positive single digit\n-3 is not positive\n10 is 10 or more'),
    ('05', '10', 'second solution, def only (E3)', "def fizzbuzz(n):\n    if n % 15 == 0:\n        print('FizzBuzz')\n    elif n % 3 == 0:\n        print('Fizz')\n    elif n % 5 == 0:\n        print('Buzz')\n    else:\n        print(n)",
     'fizzbuzz(9)\nfizzbuzz(10)\nfizzbuzz(30)\nfizzbuzz(7)', 'Fizz\nBuzz\nFizzBuzz\n7'),
    ('05', '14', 'fix, def only',                   "def countdown_by_two(n):\n    if n <= 0:\n        print('Blastoff!')\n    else:\n        countdown_by_two(n - 2)", 'countdown_by_two(5)', 'Blastoff!'),
    ('06', '5',  'fix with a new name, keeps its call', 'def absolute_value(x):\n    if x < 0:\n        return -x\n    else:\n        return x\n\nprint(absolute_value(-3), absolute_value(4), absolute_value(0))', '', '3 4 0'),
    ('06', '8',  'fix, changed lines only',         'bill = add_tip(bill)\nprint(bill)', '', '60'),
    ('06', '15', 'fix, def only',                   "def factorial(n):\n    if not isinstance(n, int):\n        print('factorial is only defined for integers.')\n        return None\n    elif n < 0:\n        print('factorial is not defined for negative numbers.')\n        return None\n    elif n == 0:\n        return 1\n    else:\n        return n * factorial(n - 1)",
     'print(factorial(1.5))\nprint(factorial(-2))\nprint(factorial(3))', 'factorial is only defined for integers.\nNone\nfactorial is not defined for negative numbers.\nNone\n6'),
    ('07', '8',  'fix, whole loop (the change comes first)', "num_letters = 0\nfor letter in 'abc':\n    num_letters = num_letters + 1\nprint(num_letters)", '', '3'),
    ('07', '12', 'fix with a new name, keeps its call', "def uses_any(word, letters):\n    for letter in word:\n        if letter in letters:\n            return True\n    return False\n\nprint(uses_any('nab', 'n'), uses_any('banana', 'n'))", '', 'True True'),
    ('07', '14', 'derived fix (E9), uses the provided run_doctests (E6)', '''def count_e(word):
    """Count the letter e (or E) in word.

    >>> count_e('Eerie')
    3
    >>> count_e('sky')
    0
    """
    count = 0
    for letter in word.lower():
        if letter == 'e':
            count += 1
    return count

run_doctests(count_e)''', '', ''),
]
# Negative tests: C4 must FAIL these.
NEGATIVE = [
    ('02', '4',  'trimmed too far: no input line (name reuse, E10)', 'print(price * 2)\nprint(price * 3)', '', '8\n12'),
    ('05', '17', 'missing import (setup imports removed)', 'forward(10)', '', ''),
    ('07', '14', 'failing doctest must not pass silently', '''def count_e(word):
    """
    >>> count_e('Eerie')
    3
    """
    return word.count('e')

run_doctests(count_e)''', '', ''),
]


# Definition cells that v3 adds after the converted questions (E6, "write code without a function"):
# Example 1's inputs become a runnable cell. They run during Run all, after ch02 Q4 and Q15.
V3_DEFINITIONS = {'02': "hours = 1\nminutes = 2\nseconds = 3\nkm = 10\nprice = '19.99'\nquantity = '3'\ntotal = 3725"}


def code_cells(nb):
    return [''.join(c['source']) for c in nb['cells'] if c['cell_type'] == 'code']


def setup_imports(nb):
    names = set()
    for c in nb['cells']:
        if c['cell_type'] == 'code' and 'setup' in c.get('metadata', {}).get('tags', []):
            for node in ast.walk(ast.parse(''.join(c['source']))):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    names |= {(a.asname or a.name).split('.')[0] for a in node.names}
    return names


def run(kc, code):
    out = []
    def hook(msg):
        t, c = msg['msg_type'], msg['content']
        if t == 'stream':
            out.append(c['text'])
        elif t in ('execute_result', 'display_data'):
            out.append(c['data'].get('text/plain', '') + '\n')
        elif t == 'error':
            out.append('ERROR ' + c['ename'] + ': ' + c['evalue'] + '\n')
    kc.execute_interactive(code, output_hook=hook, timeout=120)
    return ''.join(out)


def page_kernel(ch):
    nb = json.load(open(f'yr/chap{ch}_review.ipynb'))
    km, kc = start_new_kernel(kernel_name='python3')
    for src in code_cells(nb):                      # Run all
        run(kc, src)
    run(kc, V3_DEFINITIONS.get(ch, ''))
    gone = sorted(setup_imports(nb))
    run(kc, '\n'.join(f'globals().pop({n!r}, None)' for n in gone))
    return km, kc, gone


def check(kc, block, then, expected):
    got = run(kc, block + ('\n' + then if then else '')).rstrip('\n')
    problems = []
    if 'ERROR ' in got:
        problems.append('raised')
    if got != expected:
        problems.append(f'printed {got!r}, expected {expected!r}')
    return problems


kernels = {}
ok = True
for label, cases, want_fail in (('C4', CASES, False), ('negative', NEGATIVE, True)):
    print(f'--- {label} ---')
    for ch, q, kind, block, then, expected in cases:
        km, kc, gone = page_kernel(ch)              # each block gets its own end-of-Run-all namespace
        kernels[ch] = (None, None, gone)
        problems = check(kc, block, then, expected)
        kc.stop_channels(); km.shutdown_kernel(now=True)
        passed = not problems
        good = passed != want_fail
        ok &= good
        print(f"{'OK  ' if good else 'BAD '} ch{ch} Q{q:<3} {kind}: {'pass' if passed else '; '.join(problems)}")
print('setup imports removed:', {ch: k[2] for ch, k in kernels.items()})
sys.exit(0 if ok else 1)
