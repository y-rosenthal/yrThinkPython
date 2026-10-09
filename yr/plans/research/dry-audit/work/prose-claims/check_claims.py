"""Evaluate value claims quoted in the prose of yr/chapNN_review.ipynb.

Each claim is evaluated in a fresh namespace holding only the page's setup imports
(plus, where the prose depends on it, the question's own code, given as ctx).
Run from this directory:  python check_claims.py
"""
import contextlib, io, keyword, sys, traceback

SETUP = {
    'chap02': 'import math',
    'chap03': '',
    'chap04': 'import math',
    'chap05': '',
    'chap06': 'import math',
    'chap07': '',
}

CLAIMS = []   # (kind, page, where, text, a, b, ctx)

def V(page, where, expr, expected, ctx=''):           # `expr` is `expected` (same repr)
    CLAIMS.append(('value', page, where, f'`{expr}` is `{expected}`', expr, expected, ctx))
def T(page, where, expr, truth, ctx=''):              # `expr` is true / false
    CLAIMS.append(('truth', page, where, f'`{expr}` is {truth}', expr, truth, ctx))
def D(page, where, code, shown, ctx=''):              # `code` displays `shown`
    CLAIMS.append(('display', page, where, f'`{code}` displays `{shown!r}`', code, shown, ctx))
def E(page, where, code, err, ctx=''):                # `code` is a `err`
    CLAIMS.append(('error', page, where, f'`{code}` is a `{err}`', code, err, ctx))
def OK(page, where, code, ctx=''):                    # `code` runs without error
    CLAIMS.append(('runs', page, where, f'`{code}` runs', code, None, ctx))
def N(page, where, text, why):                        # cannot be evaluated automatically
    CLAIMS.append(('manual', page, where, text, why, None, ''))

# ---------------------------------------------------------------- chap02
p = 'chap02'
c = 'Concepts'
V(p, c, 'n', '17', 'n = 17')
E(p, c, '17 = n', 'SyntaxError')
V(p, c, 'n + 25', '42', 'n = 17')
D(p, c, 'print(n)', '17', 'n = 17')
V(p, c, 'y', '6', 'x = 5\ny = x + 1\nx = 10')
E(p, c, 'not_assigned_yet', 'NameError')
for good in ['your_name', 'score2']:
    OK(p, c, f'{good} = 1')
for bad in ['2nd_place', 'million!', 'my score']:
    E(p, c, f'{bad} = 1', 'SyntaxError')
T(p, c, 'Score != score', True, 'Score = 1\nscore = 2')
for kw in ['class', 'def', 'for', 'import', 'if', 'lambda', 'True', 'None']:
    T(p, c, f'keyword.iskeyword({kw!r})', True, 'import keyword')
E(p, c, "class = 'Python'", 'SyntaxError')
for nk in ['int', 'float', 'str']:
    T(p, c, f'keyword.iskeyword({nk!r})', False, 'import keyword')
V(p, c, 'math.pi', '3.141592653589793')
V(p, c, 'math.sqrt(25)', '5.0')
V(p, c, 'math.pow(5, 2)', '25.0')
V(p, c, '5 ** 2', '25')
E(p, c, 'import maath', 'ModuleNotFoundError')
CLAIMS.append(('error-noimport', p, c, '`math.pi` without `import math` is a `NameError`', 'math.pi', 'NameError', ''))
D(p, c, "print('The answer is', 42)", 'The answer is 42')
V(p, c, "int('101', 2)", '5')
V(p, c, 'round(3.14159, 3)', '3.142')
E(p, c, 'math.pow(2)', 'TypeError')
E(p, c, "math.sqrt('123')", 'TypeError')
D(p, c, "print('a # b')", 'a # b')
q = 'Q1 answer'
V(p, q, '8 / 2', '4.0'); V(p, q, '8 ** 2', '64')
D(p, 'Q2 answer', 'print(name)', 'Ada', "name = 'Ada'")
V(p, 'Q3 answer', 'word * 3', "'hahaha'", "word = 'ha'")
V(p, 'Q3 answer', 'len(word * 3)', '6', "word = 'ha'")
V(p, 'Q4 answer', 'price * 2', '8', 'price = 4')
V(p, 'Q4 answer', 'price * 3', '12', 'price = 4')   # "`12`, and nothing else"
V(p, 'Q5 answer', '5 + 1', '6')
V(p, 'Q7 answer', 'math.sqrt(16)', '4.0'); V(p, 'Q7 answer', 'math.pow(2, 3)', '8.0')
V(p, 'Q8 answer', "int('101', 2)", '5'); V(p, 'Q8 answer', "int('11', 2)", '3')
V(p, 'Q8 answer', "int('11')", '11'); V(p, 'Q8 answer', '3 + 11', '14')
OK(p, 'Q10 answer ("use instead")', 'math.pow(2, 3)'); OK(p, 'Q10 answer', '2 ** 3')
V(p, 'Q13 answer', '3 + 5', '8'); V(p, 'Q13 answer', '8 - 5', '3'); V(p, 'Q13 answer', '8 - 3', '5')
V(p, 'Q15 question', '(90 + 80 + 70) / 3', '80.0')
V(p, 'Q15 answer', 'score3 / 3', '23.333333333333332', 'score3 = 70')
E(p, 'Q16 answer', 'price * quantity', 'TypeError', "price = '19.99'\nquantity = '3'")
V(p, 'Q16 answer', 'price * 3', "'19.9919.9919.99'", "price = '19.99'")
V(p, 'Q16 answer', 'float(price) * int(quantity)', '0.30000000000000004', "price = '0.1'\nquantity = '3'")
V(p, 'Q16 answer', "float('1.5')", '1.5')
V(p, 'Q17 question', '7 // 2', '3')
V(p, 'Q17 answer', '3725 % 3600', '125')
N(p, 'Q9 answer c', 'Python reads `total-cost` as `total` minus `cost`', 'parse-tree claim (could be checked with ast.parse of the right side)')

# ---------------------------------------------------------------- chap03
p = 'chap03'
c = 'Concepts'
D(p, c, "def greet():\n    print('Hello')\n\ngreet()\ngreet()", 'Hello\nHello')
E(p, c, 'not_defined_yet()', 'NameError')
CLAIMS.append(('ipython-repr', p, c, "in a notebook `greet` displays `<function __main__.greet()>`",
               'greet', '<function __main__.greet()>', "def greet():\n    print('Hello')"))
V(p, c, "'a' + 'b'", "'ab'")
E(p, c, 'f(1)', 'TypeError', 'def f(a, b):\n    pass')
E(p, c, 'f(1, 2, 3)', 'TypeError', 'def f(a, b):\n    pass')
D(p, c, 'for i in range(3):\n    print(i)', '0\n1\n2')
V(p, c, 'list(range(3))', '[0, 1, 2]')
E(p, c, 'f()\nprint(t)', 'NameError', 'def f():\n    t = 1')
D(p, c, 'print()', '')
V(p, c, "'-' * 5", "'-----'")
V(p, c, "' ' * 3", "'   '")
V(p, 'Q3 answer', "'ab' * 3", "'ababab'")
V(p, 'Q4 answer', 'list(range(4))', '[0, 1, 2, 3]')
V(p, 'Q5 answer', "len('Python 3')", '8')
V(p, 'Q5 answer', "'-' * len('Hello')", "'-----'")
V(p, 'Q8 answer', '[i + 1 for i in range(4)]', '[1, 2, 3, 4]')
D(p, 'Q8 answer', 'print()', '')
D(p, 'Q11 answer', "print(' ' * 5, 'Monty')", '      Monty')   # extra space: claim "would not work exactly"
D(p, 'Q10 question', 'add_and_show(10, -4)', '10 + -4 = 6',
  "def add_and_show(a, b):\n    total = a + b\n    print(a, '+', b, '=', total)")
E(p, 'Q14 answer', "'hi' + 1", 'TypeError')
N(p, 'Q3 answer', "In the first call, `word` is `'ab'` and `n` is `3`", 'parameter values during a call (trace claim)')
N(p, 'Q13 answer', '`block(3, 2)` calls `line(3)` twice', 'call-trace claim')

# ---------------------------------------------------------------- chap04
p = 'chap04'
c = 'Concepts'
T(p, c, "str(math.pi).startswith('3.14159')", True)
CLAIMS.append(('signature', p, c, '`make_turtle` default `delay` is `0.2`; keywords delay, width, height, auto_render',
               'make_turtle', ('delay', 0.2, {'delay', 'width', 'height', 'auto_render'}), ''))
D(p, c, "for i in range(3):\n    print('hello')", 'hello\nhello\nhello')
V(p, c, 'list(range(4))', '[0, 1, 2, 3]')
E(p, c, 'range(4.5)', 'TypeError')
V(p, c, 'list(range(0))', '[]'); V(p, c, 'list(range(-4))', '[]')
POLY = 'def polygon(n, length):\n    pass'
OK(p, c, 'polygon(n=7, length=30)', POLY)
E(p, c, 'polygon(n=7, 30)', 'SyntaxError', POLY)
E(p, c, 'polygon(30, n=7)', 'TypeError', POLY)
E(p, c, 'polygon(7, size=30)', 'TypeError', POLY)
V(p, c, '360 / 4', '90.0')
E(p, c, '360 / 0', 'ZeroDivisionError')
E(p, c, 'jupyturtle', 'NameError', 'from jupyturtle import forward')   # does not define MODULE_NAME
V(p, 'Q1 answer', '360 / 4', '90.0')
V(p, 'Q2 answer', '3 * 120', '360')
V(p, 'Q8 answer', '90 / 2', '45.0')
V(p, 'Q10 question/answer', '720 / 5', '144.0')
V(p, 'Q13 answer', '[5 * 2 ** k for k in range(4)]', '[5, 10, 20, 40]')
V(p, 'Q14 answer a', '360 / 4.5', '80.0')
E(p, 'Q14 answer a', 'range(4.5)', 'TypeError')
E(p, 'Q14 answer b', '360 / 0', 'ZeroDivisionError')
V(p, 'Q14 answer c', '360 / -4', '-90.0')
V(p, 'Q14 answer c', 'list(range(-4))', '[]')
DESC = "def describe(shape, sides):\n    print('A', shape, 'has', sides, 'sides')"
for call in ["describe('square', 4)", "describe(shape='square', sides=4)",
             "describe(sides=4, shape='square')", "describe('square', sides=4)"]:
    OK(p, 'Q15 answer ("correct calls")', call, DESC)
V(p, 'Q19 question', 'int(2.7)', '2')
V(p, 'Q19 answer', 'round(2 * math.pi * 30)', '188')
V(p, 'Q19 answer', 'int(2 * math.pi * 30 / 3)', '62')
V(p, 'Q19 answer', 'int(2 * math.pi * 30 / 3) + 10', '72')
V(p, 'Q19 answer', 'int(2 * math.pi * 300 / 3)', '628')
V(p, 'Q19 answer', 'int(2 * math.pi * 300 / 3) + 10', '638')
V(p, 'Q19 answer', 'max(10, int(2 * math.pi * 1 / 3))', '10')
N(p, 'Q6 answer', 'With `left(90)` instead of `right(90)`, the same square would be drawn above the starting line', 'drawing claim')
N(p, 'Q10 answer', 'Turning `left(144)` instead also draws a star, flipped upside down', 'drawing claim')
N(p, 'Q11 answer', 'Using `forward(length)` instead of `jump(length)` draws the same picture', 'drawing claim (checkable by comparing SVGs)')
N(p, 'Q9 answer', "`b`'s `x` is still `4` and `a`'s is still `3`", 'local values after calls (trace claim)')

# ---------------------------------------------------------------- chap05
p = 'chap05'
c = 'Concepts'
V(p, c, '105 // 60', '1'); V(p, c, '-7 // 2', '-4'); V(p, c, '105 % 60', '45')
V(p, c, 'type(True)', 'bool')
D(p, c, "if x > 0:\n    print('x is positive')", 'x is positive', 'x = 3')
D(p, c, "if x > 0:\n    print('x is positive')", '', 'x = -3')
T(p, c, '0 < x < 10', True, 'x = 5')
CLAIMS.append(('kernel', p, c, "Python's limit on the number of frames (about 3000)", 'sys.getrecursionlimit()', 3000, ''))
E(p, c, "int('abc')", 'ValueError')
E(p, c, 'x = 5\n y = 6', 'IndentationError')
E(p, c, "if x > 0\n    print('positive')", 'SyntaxError', 'x = 5')
E(p, c, "if x = 5:\n    print('five')", 'SyntaxError', 'x = 5')
V(p, c, "len('\\n')", '1')
q = 'Q1 answer'
V(p, q, '135 // 60', '2'); V(p, q, '135 % 60', '15'); V(p, q, '20 % 5', '0')
V(p, q, '3 % 7', '3'); V(p, q, '-7 // 2', '-4')
XY = 'x = 5\ny = 7'
q = 'Q2 answer'
T(p, q, 'x < y and y < 10', True, XY); T(p, q, 'x > y or y == 7', True, XY)
T(p, q, 'y == 7', True, XY); T(p, q, 'x < y', True, XY); T(p, q, 'not x < y', False, XY)
V(p, q, 'type(False)', 'bool')
V(p, 'Q3 answer', '0 % 2', '0')
T(p, 'Q5 answer', 'score >= 60', True, 'score = 95')
D(p, 'Q6 answer (variant with elif)',
  "if x > 10:\n    print('big')\nelif x > 5:\n    print('medium')\nelif x > 0:\n    print('small')\nelse:\n    print('not positive')",
  'big', 'x = 15')
T(p, 'Q7 answer', '0 < x < 10', False, 'x = 10')
V(p, 'Q9 answer', '22 + 5', '27'); V(p, 'Q9 answer', '(22 + 5) % 24', '3')
V(p, 'Q9 answer', '20 + 28', '48'); V(p, 'Q9 answer', '(20 + 28) % 24', '0')
D(p, 'Q10 answer (variant: n % 3 first)',
  "if n % 3 == 0:\n    print('Fizz')\nelif n % 3 == 0 and n % 5 == 0:\n    print('FizzBuzz')", 'Fizz', 'n = 30')
T(p, 'Q10 answer', '(n % 15 == 0) == (n % 3 == 0 and n % 5 == 0)', True, 'n = 30')
D(p, 'Q11 answer (variant with >)',
  "def largest(a, b, c):\n    if a > b and a > c:\n        print(a)\n    elif b >= c:\n        print(b)\n    else:\n        print(c)\nlargest(5, 5, 1)",
  '5')
V(p, 'Q12 answer', '3 + 2 + 1', '6')
MYST = "def mystery(n, s):\n    if n == 0:\n        print('result:', s)\n    else:\n        mystery(n - 1, s + n)"
for n in [1, 4, 10]:
    D(p, 'Q12 answer (general: sum 1..n)', f'mystery({n}, 0)', f'result: {n * (n + 1) // 2}', MYST)
UPDOWN = "def up_down(n):\n    if n > 0:\n        print('*' * n)\n        up_down(n - 1)\n        print('*' * n)"
D(p, 'Q13 answer', 'up_down(0)', '', UPDOWN)
E(p, 'Q14 answer', 'countdown_by_two(5)', 'RecursionError',
  "def countdown_by_two(n):\n    if n == 0:\n        print('Blastoff!')\n    else:\n        countdown_by_two(n - 2)")
D(p, 'Q15 answer (variant: print after call)',
  "def stairs(n):\n    if n > 0:\n        stairs(n - 1)\n        print('#' * n)\nstairs(3)", '#\n##\n###')
V(p, 'Q16 question', '472 % 10', '2'); V(p, 'Q16 question', '472 // 10', '47')
V(p, 'Q17 answer', '70 * 0.6', '42.0'); V(p, 'Q17 answer', '70 * 0.6 * 0.6', '25.2')
V(p, 'Q17 answer', '70 * 0.6 * 0.6 * 0.6', '15.12'); V(p, 'Q17 answer', '70 * 0.6 * 0.6 * 0.6 * 0.6', '9.072')
V(p, 'Q17 answer ("four levels")', 'sum(1 for k in range(10) if 70 * 0.6 ** k > 10)', '4')
N(p, 'Q14 answer', 'The calls get `n` = 5, 3, 1, -1, -3, ...', 'call-trace claim')
N(p, 'Concepts', "`input('Your name?\\n')` lets the user type below the prompt", 'needs keyboard input')

# ---------------------------------------------------------------- chap06
p = 'chap06'
c = 'Concepts'
DOUBLE = 'def double(x):\n    return x * 2'
V(p, c, 'double(5)', '10', DOUBLE); V(p, c, 'y', '10', DOUBLE + '\ny = double(5)')
V(p, c, 'double(5) + 1', '11', DOUBLE)
V(p, c, 'f()', 'None', 'def f():\n    x = 1')
D(p, c, 'print(None)', 'None')
CLAIMS.append(('ipython-none', p, c, 'a cell whose last expression is `None` displays nothing', 'None', '', ''))
E(p, c, 'f()\nprint(result)', 'NameError', 'def f():\n    result = 1\n    return result')
FACT = 'def factorial(n):\n    if n == 0:\n        return 1\n    else:\n        return n * factorial(n - 1)'
E(p, c, 'factorial(1.5)', 'RecursionError', FACT)
V(p, c, 'isinstance(3, int)', 'True'); V(p, c, 'isinstance(1.5, int)', 'False')
V(p, c, 'type(math.sqrt(4))', 'float')
V(p, 'Concepts (Other ideas)', 'math.hypot(3, 4)', '5.0')
V(p, 'Concepts (Other ideas)', 'factorial(0)', '1', FACT)
N(p, c, '`if is_divisible(6, 2):`', 'is_divisible is not defined on the page')
V(p, 'Q1 answer', 'double(5)', '10', DOUBLE); V(p, 'Q1 answer', 'double(10)', '20', DOUBLE)
V(p, 'Q1 answer', "'ab' * 2", "'abab'")
V(p, 'Q2 answer', 'result', 'None', "def shout(word):\n    print(word + '!')\nresult = shout('hi')")
V(p, 'Q3 answer', 'add_one(1)', '2', "def add_one(x):\n    print('start')\n    return x + 1")
T(p, 'Q4 answer', 'a + b / 2 == a + (b / 2) != (a + b) / 2', True, 'a = 3\nb = 5')
V(p, 'Q5 answer', 'absolute_value_wrong(0)', 'None',
  'def absolute_value_wrong(x):\n    if x < 0:\n        return -x\n    if x > 0:\n        return x')
EVEN = 'def is_even(n):\n    return n % 2 == 0'
V(p, 'Q6 answer', 'is_even(5)', 'False', EVEN); V(p, 'Q6 answer', 'is_even(6)', 'True', EVEN)
V(p, 'Q6 answer', 'False or True', 'True')
SQ = 'def square(x):\n    return x * x\ndef sum_of_squares(a, b):\n    return square(a) + square(b)'
V(p, 'Q7 answer', 'square(2)', '4', SQ); V(p, 'Q7 answer', 'square(square(2))', '16', SQ)
V(p, 'Q7 answer', 'sum_of_squares(1, 1)', '2', SQ); V(p, 'Q7 answer', 'square(sum_of_squares(1, 1))', '4', SQ)
TIP = 'def add_tip(bill):\n    return bill + bill // 5'
V(p, 'Q8 question', '50 + 50 * 20 // 100', '60')
V(p, 'Q8 answer', 'add_tip(50)', '60', TIP)
D(p, 'Q8 answer', 'print(add_tip(50))', '60', TIP)
HALF = "def half(n):\n    if not isinstance(n, int):\n        print('half needs an integer')\n        return None\n    return n // 2"
V(p, 'Q9 answer', 'isinstance(9, int)', 'True'); V(p, 'Q9 answer', '9 // 2', '4')
V(p, 'Q9 answer', 'half(9)', '4', HALF); V(p, 'Q9 answer', 'half(9.0)', 'None', HALF)
V(p, 'Q9 answer', 'isinstance(9.0, int)', 'False')
POW = "def power(b, e):\n    if e == 0:\n        return 1\n    return b * power(b, e - 1)"
V(p, 'Q13 answer', 'power(2, 0)', '1', POW)
V(p, 'Q13 answer', '2 * 1', '2'); V(p, 'Q13 answer', '2 * 2', '4'); V(p, 'Q13 answer', '2 * 4', '8')
MY = 'def mystery(n):\n    if n < 10:\n        return n\n    return n % 10 + mystery(n // 10)'
V(p, 'Q14 answer', 'mystery(12)', '1 + 2', MY); V(p, 'Q14 answer', 'mystery(123)', '3 + mystery(12)', MY)
V(p, 'Q14 answer', 'mystery(123)', '6', MY)
T(p, 'Q14 answer (general: digit sum)', 'all(mystery(k) == sum(int(d) for d in str(k)) for k in range(5000))', True, MY)
E(p, 'Q15 answer', 'factorial(-2)', 'RecursionError', FACT)
V(p, 'Q16 question/answer', '6 * 7', '42')
V(p, 'Q17 answer', '(3 + 4 + 5) / 2', '6.0')
V(p, 'Q17 answer', '3 * 4 / 2', '6.0')
N(p, 'Q15 answer', 'The calls get `n` = 1.5, 0.5, -0.5, -1.5, ...', 'call-trace claim')

# ---------------------------------------------------------------- chap07
p = 'chap07'
c = 'Concepts'
D(p, c, "for letter in 'Gad':\n    print(letter)", 'G\na\nd')
D(p, c, "print(1, end=' ')\nprint(2)", '1 2')
E(p, c, 'z = z + 1', 'NameError')
V(p, c, "'e' in 'Gadsby'", 'False'); V(p, c, "'ads' in 'Gadsby'", 'True'); V(p, c, "'g' in 'Gadsby'", 'False')
V(p, c, "'Gadsby'.lower()", "'gadsby'")
V(p, c, "'  hi \\n'.strip()", "'hi'")
V(p, c, "open('words.txt').readline()", "'aa\\n'")
HASE = "def has_e(word):\n    for letter in word:\n        if letter == 'e':\n            return True\n    return False"
V(p, c, "has_e('tree')", 'True', HASE); V(p, c, "has_e('sky')", 'False', HASE)
D(p, c, 'run_docstring_examples(f, globals(), name=f.__name__)', '',
  'from doctest import run_docstring_examples\ndef f(x):\n    """\n    >>> f(2)\n    4\n    """\n    return x * 2')
V(p, 'Questions intro', "sum(1 for line in open('words.txt'))", '113783')
V(p, 'Questions intro', "[open('words.txt').readlines()[k].strip() for k in (0, 1)]", "['aa', 'aah']")
L = open('words.txt').readlines() if __name__ == '__main__' else []
T(p, 'Questions intro ("alphabetical order")', "lines == sorted(lines)", True, "lines = open('words.txt').read().split()")
D(p, 'Q1 answer', "for letter in 'code':\n    print(letter, end=' ')", 'c o d e ')
V(p, 'Q2 answer', '[5, 5 + 1, 6 + 2, 8 * 3, 24 - 4]', '[5, 6, 8, 24, 20]')
V(p, 'Q3 answer', "'g' in 'Gadsby'", 'False'); V(p, 'Q3 answer', "'ads' in 'Gadsby'", 'True')
D(p, 'Q4 answer', "print('h', '!')", 'h !')
V(p, 'Q5 answer', "len('Mississippi')", '11'); V(p, 'Q5 answer', "'Mississippi'.count('s')", '4')
V(p, 'Q6 answer', "'Hello'.lower()", "'hello'")
V(p, 'Q7 answer', "len('hello world')", '11'); V(p, 'Q7 answer', "len('  hello world \\n')", '15')
V(p, 'Q7 answer', "len('\\n')", '1')
D(p, 'Q8 answer', "num_letters = 0\nfor letter in 'abc':\n    num_letters = num_letters + 1\nprint(num_letters)", '3')
F = "f = open('words.txt')\nfirst = f.readline()\nsecond = f.readline()"
V(p, 'Q9 answer', 'first', "'aa\\n'", F); V(p, 'Q9 answer', 'len(first)', '3', F)
V(p, 'Q9 answer', 'second', "'aah\\n'", F); V(p, 'Q9 answer', 'second.strip()', "'aah'", F)
V(p, 'Q9 answer', 'len(second.strip())', '3', F)
V(p, 'Q12 answer', "'n' in 'n'", 'True'); V(p, 'Q12 answer', "'b' in 'n'", 'False')
V(p, 'Q12 answer', "'n' in 'banana'", 'True')
V(p, 'Q13 answer', '2 * 3', '6')
V(p, 'Q13 answer', "line + 'a' + 'x'", "'ax'", "line = ''")
CE = "def count_e(word):\n    count = 0\n    for letter in word:\n        if letter == 'e':\n            count += 1\n    return count"
V(p, 'Q14 answer', "count_e('Eerie')", '2', CE)
V(p, 'Q14 answer (fixed)', "count_e('Eerie'.lower())", '3', CE)
QU = "sum(1 for line in open('words.txt') if 'q' in line.strip() and 'u' not in line.strip())"
V(p, 'Q15 answer', QU, '10')
V(p, 'Q15 answer ("would not change the result")',
  "sum(1 for line in open('words.txt') if 'q' in line and 'u' not in line)", '10')
T(p, 'Q15 answer', "all(('u' not in w) == (not 'u' in w) for w in ['qat', 'quit', ''])", True)
V(p, 'Q15 answer ("but it would for word == \'qat\'")', "'qat\\n' == 'qat'", 'False')
V(p, 'Q15 answer (qat is hypothetical)', "'qat' in open('words.txt').read().split()", 'False')
V(p, 'Q16 question', "'a' < 'b'", 'True'); V(p, 'Q16 question', "'h' < 'e'", 'False')
T(p, 'Q16 answer', "all(not (ch < 'a') for ch in 'abcdefghijklmnopqrstuvwxyz')", True)
V(p, 'Q17 answer', "'' == 'a'", 'False')
V(p, 'Q17 answer', "sum(1 for k in range(2) if 'aaa'[k] == 'aaa'[k + 1])", '2')

# ---------------------------------------------------------------- evaluation
def ns_for(page, ctx):
    ns = {'__name__': '__main__'}
    exec(SETUP[page], ns)
    if ctx:
        with contextlib.redirect_stdout(io.StringIO()):
            exec(ctx, ns)
    return ns

def run(kind, page, a, b, ctx):
    if kind == 'value':
        ns = ns_for(page, ctx)
        got, want = eval(a, ns), eval(b, ns)
        return repr(got) == repr(want), repr(got)
    if kind == 'truth':
        ns = ns_for(page, ctx)
        got = bool(eval(a, ns))
        return got == b, str(got)
    if kind == 'display':
        ns = ns_for(page, ctx)
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            exec(compile(a, '<claim>', 'exec'), ns)
        got = out.getvalue()
        return got.rstrip('\n') == b.rstrip('\n') if not b.endswith(' ') else got == b, repr(got)
    if kind in ('error', 'error-noimport'):
        ns = {'__name__': '__main__'} if kind == 'error-noimport' else ns_for(page, ctx)
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                exec(compile(a, '<claim>', 'exec'), ns)
        except BaseException as e:
            return type(e).__name__ == b, type(e).__name__
        return False, 'no error'
    if kind == 'runs':
        ns = ns_for(page, ctx)
        with contextlib.redirect_stdout(io.StringIO()):
            exec(compile(a, '<claim>', 'exec'), ns)
        return True, 'ran'
    if kind == 'ipython-repr':
        from IPython.lib.pretty import pretty
        ns = ns_for(page, ctx)
        got = pretty(eval(a, ns))
        return got == b, got
    if kind == 'ipython-none':
        from IPython.core.interactiveshell import InteractiveShell
        sh = InteractiveShell.instance()
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            sh.run_cell('None')
        return out.getvalue() == '', repr(out.getvalue())
    if kind == 'signature':
        import inspect, jupyturtle
        sig = inspect.signature(getattr(jupyturtle, a))
        name, default, kws = b
        eff = sig.parameters[name].default
        if eff is None:
            eff = jupyturtle.TURTLE_DELAY      # None means the module default
        ok = eff == default and kws <= set(sig.parameters)
        return ok, f'{sig}; TURTLE_DELAY={jupyturtle.TURTLE_DELAY}'
    if kind == 'kernel':
        return None, 'checked separately in a real kernel'
    raise ValueError(kind)

if __name__ == '__main__':
    rows = []
    for kind, page, where, text, a, b, ctx in CLAIMS:
        if kind == 'manual':
            rows.append(('MANUAL', page, where, text, a))
            continue
        try:
            ok, got = run(kind, page, a, b, ctx)
        except BaseException as e:
            ok, got = False, f'raised {type(e).__name__}: {e}'
        status = 'OK' if ok else ('SKIP' if ok is None else 'WRONG')
        rows.append((status, page, where, text, got))
    from collections import Counter
    for r in rows:
        if r[0] != 'OK':
            print(' | '.join(map(str, r)))
    print(Counter(r[0] for r in rows))
    for pg in sorted(SETUP):
        print(pg, Counter(r[0] for r in rows if r[1] == pg))
