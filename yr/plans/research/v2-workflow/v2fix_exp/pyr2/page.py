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

# @title Output
minutes = 135
print(minutes // 60, minutes % 60)
print(17 % 5, 20 % 5, 3 % 7)
print(7 // 2, -7 // 2)

# @title Output
x = 5
y = 7
print(x == y, x != y)
print(x < y and y < 10)
print(x > y or y == 7)
print(not x < y)
print(type(True))

# @title Output
def check(n):
    if n % 2 == 0:
        print(n, 'is even')
    else:
        print(n, 'is odd')

check(4)
check(7)
check(0)

# Your code here

# @title Output
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

# @title Output
x = 15
if x > 10:
    print('big')
if x > 5:
    print('medium')
if x > 0:
    print('small')
else:
    print('not positive')

# @title Output
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

# @title Output of part a
__import__('IPython').get_ipython().run_cell(
r"""
x = 5
if x = 5:
    print('five')
""");

# @title Output of part b
__import__('IPython').get_ipython().run_cell(
r"""
x = 5
if x > 0
    print('positive')
""");

# @title Output of part c
__import__('IPython').get_ipython().run_cell(
r"""
x = 5
 y = 6
""");

# Your code here

# Your code here

# Your code here

# @title Output
def mystery(n, s):
    print('n =', n, 's =', s)
    if n == 0:
        print('result:', s)
    else:
        mystery(n - 1, s + n)

mystery(3, 0)

# @title Output
def up_down(n):
    if n > 0:
        print('*' * n)
        up_down(n - 1)
        print('*' * n)

up_down(3)

def countdown_by_two(n):
    if n == 0:
        print('Blastoff!')
    else:
        countdown_by_two(n - 2)

# @title Output
__import__('IPython').get_ipython().run_cell(
r"""
countdown_by_two(5)
""");

# Your code here

# Your code here

# @title Output
def branch(length):
    if length > 10:
        forward(length)
        left(30)
        branch(length * 0.6)
        right(60)
        branch(length * 0.6)
        left(30)
        forward(-length)

make_turtle(delay=0, height=220)
left(90)            # face up
penup()
forward(-100)       # move down without drawing
pendown()
branch(70)
