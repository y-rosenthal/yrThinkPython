from os.path import basename, exists

def download(url):
    filename = basename(url)
    if not exists(filename):
        from urllib.request import urlretrieve

        local, _ = urlretrieve(url, filename)
        print("Downloaded " + str(local))
    return filename

download('https://github.com/ramalho/jupyturtle/releases/download/2024-03/jupyturtle.py');

from jupyturtle import make_turtle, forward, left, right, penup, pendown

def run_code(code):
    """Run the Python code in the string code, exactly as if it were in a cell of its own.

    The answers run the question's code with run_code when its result is an error: the
    error is shown, but it does not stop "Run all", so the rest of the page still runs.
    """
    get_ipython().run_cell(code)

from IPython.core.magic import register_cell_magic

@register_cell_magic
def question(line, cell):
    """%%question NAME: store the cell's code in the variable NAME, without running it.
    The Answer runs it with run_code(NAME)."""
    get_ipython().user_ns[line.strip()] = cell

# The question's code: run it to see its output
minutes = 135
print(minutes // 60, minutes % 60)
print(17 % 5, 20 % 5, 3 % 7)
print(7 // 2, -7 // 2)

# The question's code: run it to see its output
x = 5
y = 7
print(x == y, x != y)
print(x < y and y < 10)
print(x > y or y == 7)
print(not x < y)
print(type(True))

# The question's code: run it to see its output
def check(n):
    if n % 2 == 0:
        print(n, 'is even')
    else:
        print(n, 'is odd')

check(4)
check(7)
check(0)

# The question's code: run it to see its output
def grade(score):
    if score >= 60:
        print('pass')
    elif score >= 90:
        print('excellent')
    else:
        print('fail')

grade(95)
grade(70)
grade(30)

# The question's code: run it to see its output
x = 15
if x > 10:
    print('big')
if x > 5:
    print('medium')
if x > 0:
    print('small')
else:
    print('not positive')

# The question's code: run it to see its output
def describe(x):
    if 0 < x < 10:
        print(x, 'is a positive single digit')
    else:
        if x <= 0:
            print(x, 'is not positive')
        else:
            print(x, 'is 10 or more')

describe(5)
describe(-3)
describe(10)

%%question q8a
x = 5
if x = 5:
    print('five')

%%question q8b
x = 5
if x > 0
    print('positive')

%%question q8c
x = 5
 y = 6

# Part a: the question's code
run_code(q8a)

# Part b: the question's code
run_code(q8b)

# Part c: the question's code
run_code(q8c)
