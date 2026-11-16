---
nosearch: true
myst:
  html_meta:
    robots: noindex, nofollow
---

# Fall 2026 midterm, version 1

This is **version 1** of the midterm: its pages have the small mark **K4**, and question 1 starts with `a = 7`. The other version is on the page [Fall 2026 midterm, version 2](fall2026_midterm_version2.md). The page [Fall 2026 midterm](fall2026_midterm.md) tells you how to find your version.

Under each part is the right answer, and then the steps that lead to it. A full answer needs every one of its steps.

## Part I: what does the code display?

These were the instructions: write all answers on the answer sheet. If a part displays nothing, write the word `nothing`.

### Question 1

```python
a = 7
b = 2
print(a / b)              # part a
print(a // b, a % b)      # part b
print(a + b * 3 ** 2)     # part c
s = '12'
print(s * b, int(s) * b)  # part d
print(s + str(b))         # part e
```

**Part a.** Answer: `3.5`

1. `/` is true division and keeps the fraction: `7 / 2 = 3.5` (a float)

**Part b.** Answer: `3 1`

1. `//` is floor division: `7 // 2 = 3`, a whole number (the fraction is dropped, not rounded up; displayed 3, not 3.0)
2. `%` is the remainder: `7 % 2 = 1`

**Part c.** Answer: `25`

1. `**` is a power: `3 ** 2 = 9`
2. `**` is done before `*`: `2 * 9 = 18`
3. `*` is done before `+`: `7 + 18 = 25`

**Part d.** Answer: `1212 24`

1. `s` is a string, so `s * b` repeats it; it is not arithmetic
2. The result is one string, `'12'` twice with nothing between: 1212
3. `int(s)` is the number 12, so `int(s) * b` is arithmetic: 24

**Part e.** Answer: `122`

1. `str(b)` turns the number 2 into the string `'2'`
2. `+` between two strings joins them; it does not add
3. The result is one string with nothing between the pieces: 122

### Question 2

```python
def f(n):
    print(n + 1)

def g(n):
    return n + 1

def h(n):
    return g(n) * 2

a = f(5)        # part a
b = g(5)        # part b
print(a)        # part c
print(b)        # part d
print(h(g(b)))  # part e
```

**Part a.** Answer: `6`

1. The call `f(5)` runs when the line `a = f(5)` runs, although it is on the right of `=`
2. `f` displays `n + 1` with print: 6

**Part b.** Answer: `nothing` (this line displays nothing, so the answer is the word `nothing`)

1. `g(5)` computes `5 + 1 = 6`
2. `g` returns it and does not print: the line displays nothing

**Part c.** Answer: `None`

1. `f` has no return, so the call gave `None` and a is `None`
2. `print(a)` displays the value of a: `None`

**Part d.** Answer: `6`

1. `g(5)` returned 6, and b holds it
2. `print(b)` displays the value: 6

**Part e.** Answer: `16`

1. `b` is 6
2. The inner call first: `g(6) = 7`
3. `h(7)` calls g again: `g(7) = 8`
4. And doubles it: 16

### Question 3

```python
def f(x, y):
    x = x + y
    y = x * 2
    return y

x = 3
y = 4
z = f(x, y)
print(x, y, z)  # part a
x = f(x, x)
print(x)        # part b
```

**Part a.** Answer: `3 4 14`

1. The x inside f is local: the x outside is still 3
2. The same for y: still 4
3. Inside f, `x = x + y = 7`
4. `y = x * 2` uses the new x: 14, which f returns to z

**Part b.** Answer: `12`

1. Both parameters get the outer x, 3 (by position: the y inside f is 3, not the outer 4)
2. `x = x + y = 6`
3. `y = x * 2 = 12` is returned
4. The returned value is assigned to the outer x and displayed

### Question 4

Draw what the turtle draws. Write the length next to each line.

```python
from jupyturtle import *

make_turtle()
forward(40)
left(90)
forward(20)
penup()
forward(20)
pendown()
right(90)
forward(40)
```

**Answer:**

<div class="yr-turtle-answer">
<svg xmlns="http://www.w3.org/2000/svg" width="308" height="188" viewBox="0 0 308 188" role="img" aria-label="The drawing of the turtle" style="max-width: 100%; color: inherit">
<line x1="34" y1="154" x2="154" y2="154" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
<text x="94" y="174" text-anchor="middle" font-size="15" fill="currentColor">40</text>
<line x1="154" y1="154" x2="154" y2="94" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
<text x="162" y="129" text-anchor="start" font-size="15" fill="currentColor">20</text>
<line x1="154" y1="94" x2="154" y2="34" stroke="currentColor" stroke-width="1.5" stroke-dasharray="2 5" opacity="0.6" stroke-linecap="round"/>
<text x="162" y="69" text-anchor="start" font-size="15" fill="currentColor" opacity="0.6">20</text>
<line x1="154" y1="34" x2="274" y2="34" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
<text x="214" y="26" text-anchor="middle" font-size="15" fill="currentColor">40</text>
<path d="M 20 148 L 32 154 L 20 160 Z" fill="currentColor"/>
</svg>
</div>

The turtle starts at the arrow and faces right. It draws a line of 40 to the right, then a line of 20 up, then a gap of 20 (the pen is up, so no line is drawn), still going up, then a line of 40 to the right. The dotted piece is the gap.

1. `forward(40)`: a line of 40 to the right (a new turtle faces right)
2. `left(90)`, `forward(20)`: a line of 20 up
3. `penup`, `forward(20)`: a gap of 20, still going up
4. `pendown`, `right(90)`, `forward(40)`: a line of 40 to the right

### Question 5

Write everything that the code displays.

```python
def f(n):
    return n % 2 == 0

n = 15
if n > 10:
    print('one')
if n > 5:
    print('two')
elif n > 0:
    print('three')
else:
    print('four')
if f(n):
    print('five')
elif n % 10 == 5:
    print('six')
print('seven')
```

**Answer:**

```text
one
two
six
seven
```

1. First if: `15 > 10`, so one
2. The second if starts a new chain; its first true branch only: `15 > 5`, so two (not three)
3. Third chain: `f(15)` is `False` (15 is odd), so the `elif` is tested: `15 % 10 == 5`, so six
4. `print('seven')` is outside every if: always displayed

### Question 6

```python
def f(a, b):
    if a > b:
        if a % 2 == 0:
            print('P', end=' ')
        else:
            print('Q', end=' ')
        print('R', end=' ')
    else:
        if b > 10:
            print('S', end=' ')
        elif a == b:
            print('T', end=' ')
    print('U')

f(6, 3)    # part a
f(3, 3)    # part b
f(1, 5)    # part c
f(12, 12)  # part d
```

**Part a.** Answer: `P R U`

1. `6 > 3` is `True`: the if branch
2. `6 % 2 == 0`: P (not Q)
3. R is printed after the inner if/else, in the same branch
4. U is outside every branch: printed on every call

**Part b.** Answer: `T U`

1. `3 > 3` is `False`: the else branch
2. `3 > 10` is `False`: no S
3. `a == b` is `True`: T
4. U is outside every branch: printed on every call

**Part c.** Answer: `U`

1. `1 > 5` is `False`: the else branch
2. `5 > 10` is `False`: no S
3. `1 == 5` is `False`, and the chain has no else: nothing
4. U is outside every branch: printed on every call

**Part d.** Answer: `S U`

1. `12 > 12` is `False`: the else branch
2. `12 > 10` is `True`: S
3. The `elif` after a true if is skipped: no T
4. U is outside every branch: printed on every call

### Question 7

```python
x = 4
y = 9
print(x > 3 and y > 3)             # part a
print(x < 5 and (y < 5 or x > 8))  # part b
print(not (x < 5 or y > 5))        # part c
if not (x == 4 and y == 4):        # part d
    print('yes')
else:
    print('no')
```

**Part a.** Answer: `True`

1. `4 > 3` is `True`
2. `9 > 3` is `True`
3. `True` and `True` is `True`

**Part b.** Answer: `False`

1. `4 < 5` is `True`
2. The parentheses: `9 < 5` or `4 > 8` is `False`
3. `True` and `False` is `False`

**Part c.** Answer: `False`

1. `4 < 5` is `True`, `9 > 5` is `True`
2. `True` or `True` is `True`
3. Not `True` is `False`

**Part d.** Answer: `yes`

1. `x == 4` is `True`, `y == 4` is `False`
2. `True` and `False` is `False`
3. Not `False` is `True`: the if branch displays yes

### Question 8

Write everything that the code displays.

```python
for i in range(2, 11, 3):
    print(i, end='-')
print()
for i in range(5, 0, -2):
    print(i, end=' ')
print()
for i in range(3, 3):
    print(i, end=' ')
```

**Answer:**

```text
2-5-8-
5 3 1
```

1. The first loop's values: `range(2, 11, 3)` is 2, 5, 8
2. `end='-'` puts a `-` after every value, also the last one
3. The values of a loop stay on one line (`end=` replaces the line break)
4. `print()` ends the line: the second loop is on a new line
5. The second loop's values: `range(5, 0, -2)` is 5, 3, 1, with a space after each
6. `range(3, 3)` is empty: the third loop displays nothing

### Question 9

The file nums.txt has four lines: 1, 2, 3, 4 (one number on each line).

```python
total = 0
for line in open('nums.txt'):
    n = int(line.strip())
    if n % 2 == 0:
        total += n
    else:
        total -= 1
    print(total)  # parts a, b, c, d
```

**Part a.** Answer: `-1`

1. The loop takes the lines one at a time, and `print(total)` is inside it, so each pass displays one value. This is the first pass: `n` is `1`.
2. The test picks the branch for this `n`: `1 % 2 == 0` is `False`, so the `else` branch runs.
3. The update of that branch: `total -= 1`.
4. `total` starts at `0`: `0 - 1` is `-1`.

**Part b.** Answer: `1`

1. The loop takes the lines one at a time, and `print(total)` is inside it, so each pass displays one value. This is the second pass: `n` is `2`.
2. The test picks the branch for this `n`: `2 % 2 == 0` is `True`, so the `if` branch runs.
3. The update of that branch: `total += n`.
4. `total` keeps its value from the pass before, `-1`: `-1 + 2` is `1`.

**Part c.** Answer: `0`

1. The loop takes the lines one at a time, and `print(total)` is inside it, so each pass displays one value. This is the third pass: `n` is `3`.
2. The test picks the branch for this `n`: `3 % 2 == 0` is `False`, so the `else` branch runs.
3. The update of that branch: `total -= 1`.
4. `total` keeps its value from the pass before, `1`: `1 - 1` is `0`.

**Part d.** Answer: `4`

1. The loop takes the lines one at a time, and `print(total)` is inside it, so each pass displays one value. This is the fourth pass: `n` is `4`.
2. The test picks the branch for this `n`: `4 % 2 == 0` is `True`, so the `if` branch runs.
3. The update of that branch: `total += n`.
4. `total` keeps its value from the pass before, `0`: `0 + 4` is `4`.

### Question 10

```python
s = 'Python'
print(s[1], s[-1], s[len(s) - 2])  # part a
print(s[2:4])                      # part b
print(s[:2] + s[4:])               # part c
print(s[3:3] == '', s > 'apple')   # part d
t = s
t = t.upper()
print(s, t)                        # part e
```

**Part a.** Answer: `y n o`

1. `s[1]` is the second character (indexes start at 0): y
2. `s[-1]` is the last character: n
3. `len(s) - 2` is 4, and `s[4]` is o

**Part b.** Answer: `th`

1. The slice starts at index 2 (the third character)
2. And stops before index 4: two characters

**Part c.** Answer: `Pyon`

1. `s[:2]` is the first two characters: Py
2. `s[4:]` is from index 4 to the end: on
3. `+` joins the two pieces

**Part d.** Answer: `True False`

1. `s[3:3]` is an empty slice, so `== ''` is `True`
2. Strings are compared by character codes, and capitals come before small letters: `'Python' > 'apple'` is `False`

**Part e.** Answer: `Python PYTHON`

1. `t.upper()` makes a new string, and `t = t.upper()` gives it to `t`: `PYTHON`
2. `s` is not changed (a string never changes): Python, displayed first

### Question 11

```python
s = '  Banana Bread  '
t = s.strip()
print(len(s), len(t))                # part a
print(t.lower().count('b'))          # part b
print(t.replace('a', 'o'))           # part c
print(t.find('Bread'), t.find('x'))  # part d
print(t.startswith('Ban'))           # part e
```

**Part a.** Answer: `16 12`

1. `len(s)` counts every character, also the spaces at the ends and inside: 16
2. `strip` removes the spaces at the two ends only
3. The space inside stays and is counted: `len(t)` is 12

`14 12` is also right: during the test the class was told that several spaces in a row inside a string may be read as one space.

**Part b.** Answer: `2`

1. `lower()` makes every letter small, so the capital B counts too
2. `count` gives the number of b: 2, and only that number is displayed

**Part c.** Answer: `Bonono Breod`

1. `replace` changes every a, not only the first
2. The result is one string (displayed without brackets)
3. Everything else stays: the capitals, the space

**Part d.** Answer: `7 -1`

1. `find` gives the index where the match starts, counting from 0 and counting the space: 7
2. It gives -1 when there is no match

**Part e.** Answer: `True`

1. `startswith` tests the beginning of t
2. The comparison is case-sensitive: `'Ban'` matches, `True`

### Question 12

```python
def f(s, t):
    for ch in s:
        if ch in t:
            return ch
    return '?'

def g(s):
    for ch in s:
        if ch == 'a':
            return True
        else:
            return False

print(f('hello', 'lo'))                # part a
print(f('Hello', 'h'))                 # part b
print(g('banana'), g('apple'), g(''))  # part c
for ch in 'abcdef':                    # part d
    if ch == 'd':
        break
    print(ch, end='')
print()
print(ch)                              # part e
```

**Part a.** Answer: `l`

1. The loop goes through s, `'hello'`, one character at a time
2. Ch in t tests whether that character is in `'lo'`
3. `return` ends the function at the first match: one character, l

**Part b.** Answer: `?`

1. The test is case-sensitive: `'H'` is not `'h'`, so no character of s matches
2. The loop ends, and the line after it returns `'?'`

**Part c.** Answer: `False True None`

1. `g` returns in the first pass, so only the first character counts: `g('banana')` is `False`
2. `g('apple')` is `True`
3. `g('')`: the loop body never runs, there is no return: `None`

**Part d.** Answer: `abc`

1. The loop displays the characters before d
2. `break` ends the loop when ch is d, before d is displayed
3. `end=''` keeps them together on one line: abc

**Part e.** Answer: `d`

1. The loop variable still exists after the loop
2. It holds the character where break happened: d

### Question 13

```python
def f(t):
    t.append(0)

a = [1, 2, 3]
b = a
c = a[:]
b[0] = 9
c.extend([4, 5])
c.remove(2)
print(a)               # part a
print(c)               # part b
print(a is b, a == c)  # part c
f(a)
print(b)               # part d
d = a.pop(1)
print(d, a)            # part e
```

**Part a.** Answer: `[9, 2, 3]`

1. `b = a` gives the same list a second name, so `b[0] = 9` changes a
2. `c` is a copy: what is done to c does not change a

**Part b.** Answer: `[1, 3, 4, 5]`

1. `c` is a copy made before `b[0] = 9`: it starts as `[1, 2, 3]`
2. `extend` adds 4 and 5 as two elements (not as a list inside)
3. `remove(2)` takes out the value 2 (not the element at index 2)

**Part c.** Answer: `True False`

1. `a is b`: the two names are one list, `True`
2. `a == c`: the contents differ now, `False`

**Part d.** Answer: `[9, 2, 3, 0]`

1. `f`'s parameter is the caller's own list, so `append(0)` changes it
2. `a` and b are one list, so b shows the 0
3. The 9 from before is still in it

**Part e.** Answer: `2 [9, 3, 0]`

1. `pop(1)` returns the element at index 1: d is 2
2. That element is gone from a
3. `a` still has the 9
4. `a` still has the 0 that f appended

### Question 14

```python
words = 'the quick brown fox'.split()
print(len(words), words[1][0])     # part a
u = '-'.join(words[2:])
print(u, u.split('-')[1])          # part b
print(sorted(words)[0], words[0])  # part c
t = ['a', ['b', 'c'], 'd']
print(len(t), 'b' in t, 'd' in t)  # part d
```

**Part a.** Answer: `4 q`

1. `split()` gives a list of the four words: `len` is 4
2. `words[1]` is the second word, quick
3. `[0]` is its first letter: q

**Part b.** Answer: `brown-fox fox`

1. `words[2:]` is the list of the last two words
2. `join` puts `-` between them: one string, brown-fox
3. `u.split('-')` gives the two words back, and `[1]` is the second: fox

**Part c.** Answer: `brown the`

1. `sorted` gives a new list in alphabetical order; its `[0]` is brown
2. `words` itself is not changed: `words[0]` is still the

**Part d.** Answer: `3 False True`

1. `len` counts the top-level elements; the list inside is one element: 3
2. `in` does not look inside the nested list: `'b'` in t is `False`
3. `'d'` is an element of t: `True`

### Question 15

```python
count = 0
for i in range(1, 3):
    row = ''
    for j in range(i):
        row = row + str(i * j)
        count += 1
    print(row, count)  # parts a, b
```

**Part a.** Answer: `0 1`

1. `range(1, 3)` starts at 1: the first pass has `i = 1`
2. `range(1)` is only 0: one inner pass, `j = 0`
3. `row` is a string: `'' + str(1 * 0)` is `'0'`
4. `count` is 1

**Part b.** Answer: `02 3`

1. `i = 2`: `range(2)` is 0, 1: two inner passes
2. `row` starts again as `''` for each i
3. The pieces are joined as strings: `'0' + '2'` is 02
4. `count` is not started again: `1 + 2 = 3`

### Question 16

```python
def f(n):
    if n == 0:
        return 1
    return 2 * f(n - 1)

print(f(0))  # part a
print(f(3))  # part b
```

**Part a.** Answer: `1`

1. `n == 0` is the base case: `f(0)` returns 1

**Part b.** Answer: `8`

1. `f(3)` calls `f(2)`, which calls `f(1)`, which calls `f(0)`: three calls deep
2. The base case gives 1
3. Each call doubles what comes back: 2, 4, 8

## Part II: write 2 of these 3 functions

These were the instructions: answer only 2 of these 3 questions. The function must return the result, not display it.

### Question 17

`sum_multiples(n, limit)`: `n` and `limit` are positive integers. Return the sum of all the multiples of `n` (`n`, `2*n`, `3*n`, ...) that are less than or equal to `limit`. If there are none, return `0`.

Examples:

```text
>>> sum_multiples(3, 10)
18

>>> sum_multiples(5, 4)
0
```

**Answer** (one correct function):

```python
def sum_multiples(n, limit):
    total = 0
    for i in range(n, limit + 1, n):
        total += i
    return total
```

A correct function has all of these:

1. The header: `def sum_multiples(n, limit):` (the name and the two parameters).
2. A total that is set to `0` before the loop.
3. A `for` loop that goes through the multiples of `n` (a `range` with the step `n`), or through all the whole numbers up to `limit`.
4. The loop includes `limit` itself (the stop of the `range` is `limit + 1`).
5. Only multiples of `n` are added to the total (the step `n`, or the test `i % n == 0`).
6. `return` of the total, and its place after the loop and not inside it.

Also correct: loop over `range(1, limit + 1)` and add `i` when `i % n == 0`.

### Question 18

`hide_letters(text, letters)`: `text` and `letters` are strings. Return a new string that is the same as `text`, but with `'*'` in place of each character that is in `letters`. Uppercase and lowercase count as the same letter.

Examples:

```text
>>> hide_letters('Banana', 'ab')
'**n*n*'

>>> hide_letters('Hello', 'xyz')
'Hello'
```

**Answer** (one correct function):

```python
def hide_letters(text, letters):
    result = ''
    for ch in text:
        if ch.lower() in letters.lower():
            result = result + '*'
        else:
            result = result + ch
    return result
```

A correct function has all of these:

1. The header: `def hide_letters(text, letters):` (the name and the two parameters).
2. A new string (or list) that is empty before the loop.
3. A `for` loop over the characters of `text`.
4. A test with `in` that the character is in `letters`.
5. Uppercase and lowercase count as the same letter (`lower` or `upper` on the character and on `letters`).
6. `'*'` is added for a character that is in `letters`, and the character itself for every other one.
7. `return` of the new string, after the loop.

Also correct: build a list of characters and return `''.join(...)` of it.

### Question 19

`big_rows(table, limit)`: `table` is a list of rows; each row is a list of numbers. Return a new list with the total of each row whose total is greater than `limit`, in the order of the rows. Do not change `table`.

Examples:

```text
>>> big_rows([[1, 2, 3], [9, 9], [4]], 5)
[6, 18]

>>> big_rows([[1, 1], [2]], 9)
[]
```

**Answer** (one correct function):

```python
def big_rows(table, limit):
    result = []
    for row in table:
        total = 0
        for number in row:
            total += number
        if total > limit:
            result.append(total)
    return result
```

A correct function has all of these:

1. The header: `def big_rows(table, limit):` (the name and the two parameters).
2. A new list that is empty before the loops.
3. A `for` loop over the rows of `table`.
4. The total of one row: it starts at `0` for each row and each number of the row is added to it (an inner loop), or `sum(row)`.
5. The total is compared with `limit` with `>`.
6. The total (not the row) is added to the new list with `append`.
7. `return` of the new list, after the loops; `table` is not changed.

Also correct: `sum(row)` in place of the inner loop.
