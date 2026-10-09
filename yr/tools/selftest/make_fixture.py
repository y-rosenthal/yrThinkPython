"""Build selftest/fixture.ipynb: a small review page, as an author types it (before sync), that has every kind
of question in yr/README.md. selftest_review.py syncs a copy, checks it, then breaks it in many ways.

    python make_fixture.py        (rewrites fixture.ipynb next to this file)
"""
import json
from pathlib import Path

CELLS = []


def md(text, cid):
    CELLS.append({'cell_type': 'markdown', 'id': cid, 'metadata': {}, 'source': text})


def code(text, cid, tags=None):
    CELLS.append({'cell_type': 'code', 'execution_count': None, 'id': cid,
                  'metadata': {'tags': tags} if tags else {}, 'outputs': [], 'source': text})


md("""# 99b. Prof. Rosenthal's Review

A review of [Chapter 99: Self-test](https://y-rosenthal.github.io/yrThinkPython/chap99.html),
for students who have already studied the chapter.""", 'title000')
md('## Concepts covered', 'concept0')
md("""<details open>
<summary><strong>Python Syntax and Semantics</strong></summary>

- `X // Y` rounds down: `-7 // 2` is <!--=-->`?`.
- The recursion limit is about <!--= import sys; sys.getrecursionlimit() -->`?` frames.

</details>""", 'concept1')
md("""## Questions

The setup cell below downloads `jupyturtle` and imports the functions the questions use.""", 'qintro00')
code("""from os.path import basename, exists

def download(url):
    filename = basename(url)
    if not exists(filename):
        from urllib.request import urlretrieve

        local, _ = urlretrieve(url, filename)
        print("Downloaded " + str(local))
    return filename

download('https://github.com/ramalho/jupyturtle/releases/download/2024-03/jupyturtle.py');

import math
from jupyturtle import make_turtle, forward, left""", 'setup000', ['setup'])

# 1: what is displayed, with values in the prose
md("""### Question 1 (easy): what is displayed?

Predict what this code displays, then open the Answer to check.""", 'q1head00')
md("""~~~python
minutes = 135
print(minutes // 60, minutes % 60)
~~~""", 'q1run000')
md('#### Answer', 'q1answer')
md("""135 minutes is 2 hours (`minutes // 60` is <!--=-->`?`) and `minutes % 60` is <!--=-->`?` minutes.""", 'q1expl00')

# 2: find the error, three parts, error names generated
md("""### Question 2 (medium): find the error

Each part has one mistake. Predict the error for each, then open the Answer to check.""", 'q2head00')
md("""**Part a**

~~~python
x = 5
if x = 5:
    print('five')
~~~""", 'q2runa00')
md("""**Part b**

~~~python
print('start')
print(undefined_name)
~~~""", 'q2runb00')
md("""**Part c**

~~~python
import no_such_module
~~~""", 'q2runc00')
md('#### Answer', 'q2answer')
md("""**Part a:** `=` assigns; comparing needs `==`, so this is a <!--=error-->`?`.""", 'q2parta0')
md("""**Part b:** `start` is displayed, then a <!--=error-->`?`: the name was never assigned.""", 'q2partb0')
md("""**Part c:** There is no such module, so this is a <!--=error-->`?`.""", 'q2partc0')
md("""Each part stops at its mistake.""", 'q2summ00')

# 3: write a function, two solutions (E3), examples generated (E2), header (E4), Then try (E19)
md("""### Question 3 (easy): write a function

Write a function called `end_hour` that takes `start` and `duration` (hours on a 24-hour clock) and displays the
hour when the event ends.

**Examples**

```python
end_hour(9, 3)
end_hour(22, 5)
```

```python
end_hour(20, 28)
```""", 'q3head00')
code('# Your code here', 'q3place0')
md('#### Answer', 'q3answer')
md("""Use `%` to wrap around:

```python
def end_hour(start, duration):
    print((start + duration) % 24)
```

Another way, with `if`, works only for durations under a day:

<!-- not a solution -->
```python
def end_hour(start, duration):
    end = start + duration
    if end >= 24:
        end = end - 24
    print(end)

end_hour(20, 28)
```""", 'q3expl00')

# 3b: a lettered question (stable numbers)
md("""### Question 3b (easy): what is displayed?""", 'q3bhead0')
md("""~~~python
print(math.sqrt(16))
~~~""", 'q3brun00')
md('#### Answer', 'q3banswe')
md("""`math.sqrt` returns a float, so `math.sqrt(16)` is <!--=-->`?`.""", 'q3bexpl0')

# 4: a provided helper (definition cell, E6) and a drawing question
md("""### Question 4 (medium): write a function that draws

Write a function called `two_squares` that draws a square, turns left 180 degrees, and draws another square.""", 'q4head00')
code("""def square(length):
    for i in range(4):
        forward(length)
        left(90)""", 'q4def000')
md("""**Examples**

```python
make_turtle()
two_squares(40)
```""", 'q4ex0000')
code('# Your code here', 'q4place0')
md('#### Answer', 'q4answer')
md("""```python
def two_squares(length):
    square(length)
    left(180)
    square(length)
```""", 'q4expl00')

# 5: uses the helper from Question 4; a fix (changed lines only, E9) and a "what if" drawing (E11)
md("""### Question 5 (medium): what is drawn?""", 'q5head00')
md("""~~~python
make_turtle()
square(30)
left(45)
square(30)
~~~""", 'q5run000')
md('#### Answer', 'q5answer')
md("""Two squares; the second is turned 45 degrees. With `left(90)` instead, the second square covers the first:

```python
make_turtle()
square(30)
left(90)
square(30)
```""", 'q5expl00')

# 6: a fix derived from the question's code (E9), and a fix that keeps its input line (E10)
md("""### Question 6 (medium): find the bug

`total` should be the sum of the numbers from 1 to `n`. What does the code display, and how do you fix it?""", 'q6head00')
md("""~~~python
def total(n):
    result = 0
    for i in range(n):
        result = result + i
    return result

print(total(4))
~~~""", 'q6run000')
md('#### Answer', 'q6answer')
md("""`range(n)` stops before `n`. Count to `n + 1`:

<!-- derive: from=Q6 replace="range(n)" with="range(n + 1)" -->
```python
```

A fix that keeps its own input line:

```python
price = 4
print(price * 2)
```""", 'q6expl00')

# 7: an infinite recursion, wrapped (prints line numbers)
md("""### Question 7 (hard): what happens?""", 'q7head00')
md("""~~~python
def countdown(n):
    if n == 0:
        print('Blastoff!')
    else:
        countdown(n - 2)

countdown(3)
~~~""", 'q7run000')
md('#### Answer', 'q7answer')
md("""`n` skips over `0`, so the function never stops calling itself: a <!--=error-->`?`.""", 'q7expl00')

# 8: write code without a function (no-signature): the example assigns the inputs
md("""### Question 8 (medium): write code

The variables `hours` and `minutes` have already been assigned. Write code that displays the total number of minutes.

**Examples**

```python
hours = 1
minutes = 2
```""", 'q8head00')
code('# Your code here', 'q8place0', ['no-signature'])
md('#### Answer', 'q8answer')
md("""```python
print(hours * 60 + minutes)
```""", 'q8expl00')

md("""*Summary and questions by Prof. Y. Rosenthal, based on*
[Think Python: 3rd Edition](https://allendowney.github.io/ThinkPython/index.html) *by Allen B. Downey.*""", 'credits0')

nb = {'cells': CELLS, 'metadata': {'kernelspec': {'display_name': 'Python 3 (ipykernel)', 'language': 'python',
                                                   'name': 'python3'}, 'language_info': {'name': 'python'}},
      'nbformat': 4, 'nbformat_minor': 5}
for c in nb['cells']:
    s = c['source'].split('\n')
    c['source'] = [x + '\n' for x in s[:-1]] + [s[-1]]
Path(__file__).with_name('fixture.ipynb').write_text(json.dumps(nb, indent=1, ensure_ascii=False) + '\n')
print('wrote fixture.ipynb')
