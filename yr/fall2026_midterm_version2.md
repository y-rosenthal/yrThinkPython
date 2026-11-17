---
nosearch: true
myst:
  html_meta:
    robots: noindex, nofollow
---

# Fall 2026 midterm, version 2

This is **version 2** of the midterm: question 1 starts with `a = 5`. The other version is on the page [Fall 2026 midterm, version 1](fall2026_midterm_version1.md). The page [Fall 2026 midterm](fall2026_midterm.md) tells you how to find your version. All the right answers on one sheet: [Fall 2026 midterm, version 2: answer key](fall2026_midterm_key_version2.md).

Under each part is the right answer, and then the steps that lead to it. A full answer needs every one of its steps.

## Part I: what does the code display?

These were the instructions: write all answers on the answer sheet. If a part displays nothing, write the word `nothing`.

### Question 1

```python
a = 5
b = 2
print(a / b)              # part a
print(a // b, a % b)      # part b
print(a + b * 2 ** 3)     # part c
s = '30'
print(s * b, int(s) * b)  # part d
print(s + str(b))         # part e
```

**Part a.** Answer: `2.5`

1. `/` is true division and keeps the fraction: `5 / 2 = 2.5` (a float)

**Part b.** Answer: `2 1`

1. `//` is floor division: `5 // 2 = 2`, a whole number (the fraction is dropped, not rounded up; displayed 2, not 2.0)
2. `%` is the remainder: `5 % 2 = 1`

**Part c.** Answer: `21`

1. `**` is a power: `2 ** 3 = 8`
2. `**` is done before `*`: `2 * 8 = 16`
3. `*` is done before `+`: `5 + 16 = 21`

**Part d.** Answer: `3030 60`

1. `s` is a string, so `s * b` repeats it; it is not arithmetic
2. The result is one string, `'30'` twice with nothing between: 3030
3. `int(s)` is the number 30, so `int(s) * b` is arithmetic: 60

**Part e.** Answer: `302`

1. `str(b)` turns the number 2 into the string `'2'`
2. `+` between two strings joins them; it does not add
3. The result is one string with nothing between the pieces: 302

### Question 2

```python
def f(n):
    print(n - 1)

def g(n):
    return n * 2

def h(n):
    return g(n) + 1

a = f(4)        # part a
b = g(4)        # part b
print(a)        # part c
print(b)        # part d
print(h(g(b)))  # part e
```

**Part a.** Answer: `3`

1. The call `f(4)` runs when the line `a = f(4)` runs, although it is on the right of `=`
2. `f` displays `n - 1` with print: 3

**Part b.** Answer: `nothing` (this line displays nothing, so the answer is the word `nothing`)

1. `g(4)` computes `4 * 2 = 8`
2. `g` returns it and does not print: the line displays nothing

**Part c.** Answer: `None`

1. `f` has no return, so the call gave `None` and a is `None`
2. `print(a)` displays the value of a: `None`

**Part d.** Answer: `8`

1. `g(4)` returned 8, and b holds it
2. `print(b)` displays the value: 8

**Part e.** Answer: `33`

1. `b` is 8
2. The inner call first: `g(8) = 16`
3. `h(16)` calls g again: `g(16) = 32`
4. And adds 1: 33

### Question 3

```python
def f(x, y):
    x = x * y
    y = x + 1
    return y

x = 2
y = 5
z = f(x, y)
print(x, y, z)  # part a
x = f(x, x)
print(x)        # part b
```

**Part a.** Answer: `2 5 11`

1. The x inside f is local: the x outside is still 2
2. The same for y: still 5
3. Inside f, `x = x * y = 10`
4. `y = x + 1` uses the new x: 11, which f returns to z

**Part b.** Answer: `5`

1. Both parameters get the outer x, 2 (by position: the y inside f is 2, not the outer 5)
2. `x = x * y = 4`
3. `y = x + 1 = 5` is returned
4. The returned value is assigned to the outer x and displayed

### Question 4

Draw what the turtle draws. Write the length next to each line.

```python
from jupyturtle import *

make_turtle()
forward(30)
right(90)
forward(20)
penup()
forward(10)
pendown()
left(90)
forward(50)
```

**Answer:**

<div class="yr-turtle-answer">
<svg xmlns="http://www.w3.org/2000/svg" width="308" height="158" viewBox="0 0 308 158" role="img" aria-label="The drawing of the turtle" style="max-width: 100%; color: inherit">
<line x1="34" y1="34" x2="124" y2="34" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
<text x="79" y="26" text-anchor="middle" font-size="15" fill="currentColor">30</text>
<line x1="124" y1="34" x2="124" y2="94" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
<text x="116" y="69" text-anchor="end" font-size="15" fill="currentColor">20</text>
<line x1="124" y1="94" x2="124" y2="124" stroke="currentColor" stroke-width="1.5" stroke-dasharray="2 5" opacity="0.6" stroke-linecap="round"/>
<text x="116" y="114" text-anchor="end" font-size="15" fill="currentColor" opacity="0.6">10</text>
<line x1="124" y1="124" x2="274" y2="124" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
<text x="199" y="144" text-anchor="middle" font-size="15" fill="currentColor">50</text>
<path d="M 20 28 L 32 34 L 20 40 Z" fill="currentColor"/>
</svg>
</div>

The turtle starts at the arrow and faces right. It draws a line of 30 to the right, then a line of 20 down, then a gap of 10 (the pen is up, so no line is drawn), still going down, then a line of 50 to the right. The dotted piece is the gap.

1. `forward(30)`: a line of 30 to the right (a new turtle faces right)
2. `right(90)`, `forward(20)`: a line of 20 down
3. `penup`, `forward(10)`: a gap of 10, still going down
4. `pendown`, `left(90)`, `forward(50)`: a line of 50 to the right

### Question 5

Write everything that the code displays.

```python
def f(n):
    return n % 3 == 0

n = 12
if n > 10:
    print('one')
if n > 20:
    print('two')
elif n > 0:
    print('three')
else:
    print('four')
if f(n):
    print('five')
elif n % 10 == 2:
    print('six')
print('seven')
```

**Answer:**

```text
one
three
five
seven
```

1. First if: `12 > 10`, so one
2. The second if starts a new chain: `12 > 20` is `False`, so its `elif` runs: three
3. Third chain: `f(12)` is `True` (`12 % 3 == 0`), so five, and the `elif` is skipped
4. `print('seven')` is outside every if: always displayed

### Question 6

```python
def f(a, b):
    if a < b:
        if b % 2 == 0:
            print('P', end=' ')
        else:
            print('Q', end=' ')
        print('R', end=' ')
    else:
        if a > 10:
            print('S', end=' ')
        elif a == b:
            print('T', end=' ')
    print('U')

f(3, 7)    # part a
f(5, 1)    # part b
f(12, 12)  # part c
f(4, 4)    # part d
```

**Part a.** Answer: `Q R U`

1. `3 < 7` is `True`: the if branch
2. `7 % 2 == 0` is `False`: Q (not P)
3. R is printed after the inner if/else, in the same branch
4. U is outside every branch: printed on every call

**Part b.** Answer: `U`

1. `5 < 1` is `False`: the else branch
2. `5 > 10` is `False`: no S
3. `5 == 1` is `False`, and the chain has no else: nothing
4. U is outside every branch: printed on every call

**Part c.** Answer: `S U`

1. `12 < 12` is `False`: the else branch
2. `12 > 10` is `True`: S
3. The `elif` after a true if is skipped: no T
4. U is outside every branch: printed on every call

**Part d.** Answer: `T U`

1. `4 < 4` is `False`: the else branch
2. `4 > 10` is `False`: no S
3. `a == b` is `True`: T
4. U is outside every branch: printed on every call

### Question 7

```python
x = 6
y = 2
print(x > 7 or y > 7)              # part a
print(x > 5 or (y > 5 and x < 3))  # part b
print(not (x < 5 and y < 5))       # part c
if not (x == 6 or y == 6):         # part d
    print('yes')
else:
    print('no')
```

**Part a.** Answer: `False`

1. `6 > 7` is `False`
2. `2 > 7` is `False`
3. `False` or `False` is `False`

**Part b.** Answer: `True`

1. `6 > 5` is `True`
2. The parentheses: `2 > 5` and `6 < 3` is `False`
3. `True` or `False` is `True`

**Part c.** Answer: `True`

1. `6 < 5` is `False`, `2 < 5` is `True`
2. `False` and `True` is `False`
3. Not `False` is `True`

**Part d.** Answer: `no`

1. `x == 6` is `True`, `y == 6` is `False`
2. `True` or `False` is `True`
3. Not `True` is `False`: the else branch displays no

### Question 8

Write everything that the code displays.

```python
for i in range(1, 10, 4):
    print(i, end='+')
print()
for i in range(6, 0, -3):
    print(i, end=' ')
print()
for i in range(4, 2):
    print(i, end=' ')
```

**Answer:**

```text
1+5+9+
6 3
```

1. The first loop's values: `range(1, 10, 4)` is 1, 5, 9
2. `end='+'` puts a `+` after every value, also the last one
3. The values of a loop stay on one line (`end=` replaces the line break)
4. `print()` ends the line: the second loop is on a new line
5. The second loop's values: `range(6, 0, -3)` is 6, 3, with a space after each
6. `range(4, 2)` is empty: the third loop displays nothing

### Question 9

The file nums.txt has four lines: 3, 4, 5, 6 (one number on each line).

```python
total = 0
for line in open('nums.txt'):
    n = int(line.strip())
    if n % 2 == 1:
        total += n
    else:
        total -= 1
    print(total)  # parts a, b, c, d
```

**Part a.** Answer: `3`

1. The loop takes the lines one at a time, and `print(total)` is inside it, so each pass displays one value. This is the first pass: `n` is `3`.
2. The test picks the branch for this `n`: `3 % 2 == 1` is `True`, so the `if` branch runs.
3. The update of that branch: `total += n`.
4. `total` starts at `0`: `0 + 3` is `3`.

**Part b.** Answer: `2`

1. The loop takes the lines one at a time, and `print(total)` is inside it, so each pass displays one value. This is the second pass: `n` is `4`.
2. The test picks the branch for this `n`: `4 % 2 == 1` is `False`, so the `else` branch runs.
3. The update of that branch: `total -= 1`.
4. `total` keeps its value from the pass before, `3`: `3 - 1` is `2`.

**Part c.** Answer: `7`

1. The loop takes the lines one at a time, and `print(total)` is inside it, so each pass displays one value. This is the third pass: `n` is `5`.
2. The test picks the branch for this `n`: `5 % 2 == 1` is `True`, so the `if` branch runs.
3. The update of that branch: `total += n`.
4. `total` keeps its value from the pass before, `2`: `2 + 5` is `7`.

**Part d.** Answer: `6`

1. The loop takes the lines one at a time, and `print(total)` is inside it, so each pass displays one value. This is the fourth pass: `n` is `6`.
2. The test picks the branch for this `n`: `6 % 2 == 1` is `False`, so the `else` branch runs.
3. The update of that branch: `total -= 1`.
4. `total` keeps its value from the pass before, `7`: `7 - 1` is `6`.

### Question 10

```python
s = 'Sunday'
print(s[2], s[-2], s[len(s) - 1])  # part a
print(s[1:3])                      # part b
print(s[:3] + s[5:])               # part c
print(s[2:2] == '', s < 'monday')  # part d
t = s
t = t.lower()
print(s, t)                        # part e
```

**Part a.** Answer: `n a y`

1. `s[2]` is the third character (indexes start at 0): n
2. `s[-2]` is the one before the last: a
3. `len(s) - 1` is 5, and `s[5]` is y

**Part b.** Answer: `un`

1. The slice starts at index 1 (the second character)
2. And stops before index 3: two characters

**Part c.** Answer: `Suny`

1. `s[:3]` is the first three characters: Sun
2. `s[5:]` is from index 5 to the end: y
3. `+` joins the two pieces

**Part d.** Answer: `True True`

1. `s[2:2]` is an empty slice, so `== ''` is `True`
2. Strings are compared by character codes, and capitals come before small letters: `'Sunday' < 'monday'` is `True`

**Part e.** Answer: `Sunday sunday`

1. `t.lower()` makes a new string, and `t = t.lower()` gives it to `t`: `sunday`
2. `s` is not changed (a string never changes): Sunday, displayed first

### Question 11

```python
s = '  Apple Pie  '
t = s.strip()
print(len(s), len(t))              # part a
print(t.upper().count('P'))        # part b
print(t.replace('p', 'b'))         # part c
print(t.find('Pie'), t.find('z'))  # part d
print(t.endswith('pie'))           # part e
```

**Part a.** Answer: `13 9`

1. `len(s)` counts every character, also the spaces at the ends and inside: 13
2. `strip` removes the spaces at the two ends only
3. The space inside stays and is counted: `len(t)` is 9

`11 9` is also right: during the test the class was told that several spaces in a row inside a string may be read as one space.

**Part b.** Answer: `3`

1. `upper()` makes every letter a capital, so the small p's count too
2. `count` gives the number of P: 3, and only that number is displayed

**Part c.** Answer: `Abble Pie`

1. `replace` changes every p, not only the first
2. It is case-sensitive: the capital P of Pie stays
3. Everything else stays: the capitals, the space

**Part d.** Answer: `6 -1`

1. `find` gives the index where the match starts, counting from 0 and counting the space: 6
2. It gives -1 when there is no match

**Part e.** Answer: `False`

1. `endswith` tests the end of t
2. The comparison is case-sensitive: `'pie'` is not `'Pie'`, `False`

### Question 12

```python
def f(s, t):
    for ch in s:
        if ch in t:
            return ch
    return '!'

def g(s):
    for ch in s:
        if ch == 'e':
            return True
        else:
            return False

print(f('world', 'dr'))           # part a
print(f('World', 'w'))            # part b
print(g('eel'), g('bee'), g(''))  # part c
for ch in 'python':               # part d
    if ch == 'h':
        break
    print(ch, end='')
print()
print(ch)                         # part e
```

**Part a.** Answer: `r`

1. The loop goes through s, `'world'`, one character at a time
2. Ch in t tests whether that character is in `'dr'`
3. `return` ends the function at the first match: one character, r

**Part b.** Answer: `!`

1. The test is case-sensitive: `'W'` is not `'w'`, so no character of s matches
2. The loop ends, and the line after it returns `'!'`

**Part c.** Answer: `True False None`

1. `g` returns in the first pass, so only the first character counts: `g('eel')` is `True`
2. `g('bee')` is `False`
3. `g('')`: the loop body never runs, there is no return: `None`

**Part d.** Answer: `pyt`

1. The loop displays the characters before h
2. `break` ends the loop when ch is h, before h is displayed
3. `end=''` keeps them together on one line: pyt

**Part e.** Answer: `h`

1. The loop variable still exists after the loop
2. It holds the character where break happened: h

### Question 13

```python
def f(t):
    t.append(7)

a = [4, 5, 6]
b = a
c = a[:]
b[1] = 0
c.extend([1, 2])
c.remove(5)
print(a)               # part a
print(c)               # part b
print(a is c, a == b)  # part c
f(b)
print(a)               # part d
d = a.pop(0)
print(d, a)            # part e
```

**Part a.** Answer: `[4, 0, 6]`

1. `b = a` gives the same list a second name, so `b[1] = 0` changes a
2. `c` is a copy: what is done to c does not change a

**Part b.** Answer: `[4, 6, 1, 2]`

1. `c` is a copy made before `b[1] = 0`: it starts as `[4, 5, 6]`
2. `extend` adds 1 and 2 as two elements (not as a list inside)
3. `remove(5)` takes out the value 5

**Part c.** Answer: `False True`

1. `a is c`: c is a different list (a copy), `False`
2. `a == b`: the same list, so equal, `True`

**Part d.** Answer: `[4, 0, 6, 7]`

1. `f`'s parameter is the caller's own list, so `append(7)` changes it
2. `a` and b are one list, so a shows the 7
3. The 0 from before is still in it

**Part e.** Answer: `4 [0, 6, 7]`

1. `pop(0)` returns the element at index 0: d is 4
2. That element is gone from a
3. `a` still has the 0
4. `a` still has the 7 that f appended

### Question 14

```python
words = 'one two three four'.split()
print(len(words), words[2][1])     # part a
u = '+'.join(words[:2])
print(u, u.split('+')[0])          # part b
print(sorted(words)[0], words[0])  # part c
t = [['x', 'y'], 'z']
print(len(t), 'x' in t, 'z' in t)  # part d
```

**Part a.** Answer: `4 h`

1. `split()` gives a list of the four words: `len` is 4
2. `words[2]` is the third word, three
3. `[1]` is its second letter: h

**Part b.** Answer: `one+two one`

1. `words[:2]` is the list of the first two words
2. `join` puts `+` between them: one string, one+two
3. `u.split('+')` gives the two words back, and `[0]` is the first: one

**Part c.** Answer: `four one`

1. `sorted` gives a new list in alphabetical order; its `[0]` is four
2. `words` itself is not changed: `words[0]` is still one

**Part d.** Answer: `2 False True`

1. `len` counts the top-level elements; the list inside is one element: 2
2. `in` does not look inside the nested list: `'x'` in t is `False`
3. `'z'` is an element of t: `True`

### Question 15

```python
count = 0
for i in range(1, 3):
    row = ''
    for j in range(i):
        row = row + str(i + j)
        count += 1
    print(row, count)  # parts a, b
```

**Part a.** Answer: `1 1`

1. `range(1, 3)` starts at 1: the first pass has `i = 1`
2. `range(1)` is only 0: one inner pass, `j = 0`
3. `row` is a string: `'' + str(1 + 0)` is `'1'`
4. `count` is 1

**Part b.** Answer: `23 3`

1. `i = 2`: `range(2)` is 0, 1: two inner passes
2. `row` starts again as `''` for each i
3. The pieces are joined as strings: `'2' + '3'` is 23
4. `count` is not started again: `1 + 2 = 3`

### Question 16

```python
def f(n):
    if n == 0:
        return 5
    return f(n - 1) - 1

print(f(0))  # part a
print(f(3))  # part b
```

**Part a.** Answer: `5`

1. `n == 0` is the base case: `f(0)` returns 5

**Part b.** Answer: `2`

1. `f(3)` calls `f(2)`, which calls `f(1)`, which calls `f(0)`: three calls deep
2. The base case gives 5
3. Each call takes 1 off what comes back: 4, 3, 2

## Part II: write 2 of these 3 functions

These were the instructions: answer only 2 of these 3 questions. The function must return the result, not display it.

### Question 17

`count_multiples(n, limit)`: `n` and `limit` are positive integers. Return how many multiples of `n` (`n`, `2*n`, `3*n`, ...) are less than or equal to `limit`. If there are none, return `0`.

Examples:

```text
>>> count_multiples(3, 10)
3

>>> count_multiples(5, 4)
0
```

**Answer** (one correct function):

```python
def count_multiples(n, limit):
    count = 0
    for i in range(n, limit + 1, n):
        count += 1
    return count
```

A correct function has all of these:

1. The header: `def count_multiples(n, limit):` (the name and the two parameters).
2. A counter that is set to `0` before the loop.
3. A `for` loop that goes through the multiples of `n` (a `range` with the step `n`), or through all the whole numbers up to `limit`.
4. The loop includes `limit` itself (the stop of the `range` is `limit + 1`).
5. Only multiples of `n` are counted (the step `n`, or the test `i % n == 0`), and 1 is added for each.
6. `return` of the counter, and its place after the loop and not inside it.

Also correct: loop over `range(1, limit + 1)` and count `i` when `i % n == 0`; or `return limit // n`.

### Question 18

`keep_letters(text, letters)`: `text` and `letters` are strings. Return a new string that has only the characters of `text` that are in `letters`, in the same order. Uppercase and lowercase count as the same letter.

Examples:

```text
>>> keep_letters('Banana', 'ab')
'Baaa'

>>> keep_letters('Hello', 'xyz')
''
```

**Answer** (one correct function):

```python
def keep_letters(text, letters):
    result = ''
    for ch in text:
        if ch.lower() in letters.lower():
            result = result + ch
    return result
```

A correct function has all of these:

1. The header: `def keep_letters(text, letters):` (the name and the two parameters).
2. A new string (or list) that is empty before the loop.
3. A `for` loop over the characters of `text`.
4. A test with `in` that the character is in `letters`.
5. Uppercase and lowercase count as the same letter (`lower` or `upper` on the character and on `letters`).
6. The character itself is added for a character that is in `letters`, and nothing for every other one.
7. `return` of the new string, after the loop.

Also correct: build a list of characters and return `''.join(...)` of it.

### Question 19

`small_rows(table, limit)`: `table` is a list of rows; each row is a list of numbers. Return a new list with the total of each row whose total is less than `limit`, in the order of the rows. Do not change `table`.

Examples:

```text
>>> small_rows([[1, 2, 3], [9, 9], [4]], 7)
[6, 4]

>>> small_rows([[5, 5], [8]], 3)
[]
```

**Answer** (one correct function):

```python
def small_rows(table, limit):
    result = []
    for row in table:
        total = 0
        for number in row:
            total += number
        if total < limit:
            result.append(total)
    return result
```

A correct function has all of these:

1. The header: `def small_rows(table, limit):` (the name and the two parameters).
2. A new list that is empty before the loops.
3. A `for` loop over the rows of `table`.
4. The total of one row: it starts at `0` for each row and each number of the row is added to it (an inner loop), or `sum(row)`.
5. The total is compared with `limit` with `<`.
6. The total (not the row) is added to the new list with `append`.
7. `return` of the new list, after the loops; `table` is not changed.

Also correct: `sum(row)` in place of the inner loop.
