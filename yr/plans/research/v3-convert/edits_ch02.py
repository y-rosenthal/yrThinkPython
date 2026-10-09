# Page edits for chapter 2 (convert_v3.py EDITS.py); plan section 5 wording table, E9, E14, E12.
SUMMARY_STARTS = ['All three are a `TypeError`.', 'A syntax error (here, a space in a name)']

EDITS = [
    ('Run the next cell first: it imports `math` and defines `run_code`.', 'The setup cell below imports `math`.'),
    ('Predict what this code displays, then run it to check.',
     'Predict what this code displays, then open the Answer to check.'),
    ('What does this cell display when you run it in a notebook?',
     'What does this code display when it is run as a notebook cell?'),
    ('For each cell, predict whether it runs or causes an error.', 'For each part, predict whether it runs or causes an error.'),
    ('Predict the error for each, then run the cells to check.', 'Predict the error for each, then open the Answer to check.'),
    ('Each cell has an error on its second line. Predict what each cell displays before the error',
     'Each part has an error on its second line. Predict what each part displays before the error'),
    # write-code questions without a function: example 1 is now a cell
    ('**Examples** (the first lines assign the variables; your code comes after them)',
     '**Examples** (each example assigns the variables; your code comes after them)'),
    # Q10: each part carries its own import (plan section 5)
    ('~~~python\nmath.pow(2)\n~~~', '~~~python\nimport math\nmath.pow(2)\n~~~'),
    ('~~~python\nmath.pow(2, 3, 4)\n~~~', '~~~python\nimport math\nmath.pow(2, 3, 4)\n~~~'),
    ("~~~python\nmath.pow('2', 3)\n~~~", "~~~python\nimport math\nmath.pow('2', 3)\n~~~"),
    ('All three are a `TypeError`.', 'All three are a <!--=error-->`TypeError`.'),
    # E12: values in Q7's explanation
    ('so `math.sqrt(16)` is `4.0` and `math.pow(2, 3)` is `8.0`.',
     'so `math.sqrt(16)` is <!--=-->`4.0` and `math.pow(2, 3)` is <!--=-->`8.0`.'),
    # E9: Q15's fix shows only the changed lines (they run after the question's code)
    ('Fix it with parentheses:\n\n```python\nscore1 = 90\nscore2 = 80\nscore3 = 70\naverage = (score1 + score2 + score3) / 3',
     'Fix it with parentheses:\n\n```python\naverage = (score1 + score2 + score3) / 3'),
    # E14: facts listed twice inside Concepts
    ('used to specify the structure of a program. Keywords cannot be used as variable names.',
     'used to specify the structure of a program.'),
    ('is an error in the structure of a program; Python does not run a program that has one.',
     'is an error in the structure of a program.'),
    ('- A program with a semantic error runs without any error message, but does not do what was intended.\n', ''),
]
