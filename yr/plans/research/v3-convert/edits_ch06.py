# Page edits for chapter 6 (convert_v3.py EDITS.py); plan section 5 wording table, E3, E9.
SUMMARY_STARTS = []

EDITS = [
    ('Run the next cell first: it imports `math`.', 'The setup cell below imports `math`.'),
    ('Predict what this code displays, then run it to check.',
     'Predict what this code displays, then open the Answer to check.'),
    ('### Question 15 (hard): missing the base case\n\nRun this cell to define `factorial`.',
     '### Question 15 (hard): missing the base case'),
    # E9: Q8's fix shows only the changed lines (they run after the question's code)
    ('```python\ndef add_tip(bill):\n    return bill + bill // 5\n\nbill = 50\nbill = add_tip(bill)\nprint(bill)\n```',
     '```python\nbill = add_tip(bill)\nprint(bill)\n```'),
    # E3: the halfway version of Q17 is not a full solution; its own call shows its scaffolding output
    ("A version in the middle of the development, with scaffolding, could be:\n\n```python\ndef triangle_area(a, b, c):\n"
     "    s = (a + b + c) / 2\n    print('s is', s)         # for 3, 4, 5 it should be 6.0\n    return 0\n```",
     "A version in the middle of the development, with scaffolding, could be:\n\n<!-- not a solution -->\n```python\n"
     "def triangle_area(a, b, c):\n    s = (a + b + c) / 2\n    print('s is', s)         # for 3, 4, 5 it should be 6.0\n"
     "    return 0\n\nprint(triangle_area(3, 4, 5))\n```"),
]
