# Page edits for chapter 5 (convert_v3.py EDITS.py). Each (old, new) must match exactly once on the converted page.
# Plan section 5, "Wording edits", plus E9 (derived fixes), E11 ("what if" blocks), E13 (recursion limit).

SUMMARY_STARTS = ['All three are found before the cell runs']

EDITS = [
    # Questions intro (the run_code paragraph is removed by the converter)
    ('Run the next cell first: it downloads `jupyturtle`, imports those functions, and defines `run_code`.',
     'The setup cell below downloads `jupyturtle` and imports those functions.'),
    # prompts
    ('Predict what this code displays, then run it to check.',
     'Predict what this code displays, then open the Answer to check.'),
    ('Each cell has one mistake. Predict the error for each, then run the cells to check.',
     'Each part has one mistake. Predict the error for each, then open the Answer to check.'),
    ('What happens with this call? How would you fix the function?',
     'What happens with this call? How would you fix the function? '
     '(Try your fix in a new cell, so that the cell above keeps the original code.)'),
    ('Describe what it draws, then run the cell to check.', 'Describe what it draws, then open the Answer to check.'),
    # sync writes "Run this cell to define `countdown_by_two`." above the definition cell
    ('### Question 14 (hard): infinite recursion\n\nRun this cell to define `countdown_by_two`.',
     '### Question 14 (hard): infinite recursion'),
    # Q8 summary
    ('All three are found before the cell runs, so nothing is displayed or assigned.',
     "Python finds each of these mistakes before it runs any of that part's code, so nothing is displayed and "
     "`x` is never assigned."),
    # E13: the recursion limit is 1000 in Colab, not "about 3000"
    ("until Python's limit on the number of frames (about 3000) is exceeded",
     "until Python's limit on the number of frames (about <!--= import sys; sys.getrecursionlimit() -->`?`; the exact "
     "number depends on the environment) is exceeded"),
    # E11: Q5's fix as code, with its output
    ('To fix it, check `score >= 90` first.',
     'To fix it, check `score >= 90` first:\n\n'
     '<!-- derive: from=Q5 replace="if score >= 60:\\n        print(\'pass\')\\n    elif score >= 90:\\n        '
     'print(\'excellent\')" with="if score >= 90:\\n        print(\'excellent\')\\n    elif score >= 60:\\n        '
     'print(\'pass\')" -->\n```python\n```'),
    # E11: Q6's "what if" as code, with its output
    ('With `elif` instead of the second and third `if`, only `big` would be displayed.',
     'With `elif` instead of the second and third `if`, only `big` is displayed:\n\n'
     '<!-- derive: from=Q6 replace="if x > 5:\\n    print(\'medium\')\\nif x > 0:" '
     'with="elif x > 5:\\n    print(\'medium\')\\nelif x > 0:" -->\n```python\n```'),
    # E9: Q14's fix derived from the question's code
    ('Fix it by making the base case catch every number at or below zero:\n\n```python\ndef countdown_by_two(n):\n'
     "    if n <= 0:\n        print('Blastoff!')\n    else:\n        countdown_by_two(n - 2)\n```",
     'Fix it by making the base case catch every number at or below zero:\n\n'
     '<!-- derive: from=Q14 replace="if n == 0:" with="if n <= 0:" -->\n```python\n```'),
    # E9: Q10's second approach derived from the first solution
    ('A number divisible by both 3 and 5 is divisible by 15, so the first condition can also be `n % 15 == 0`:\n\n'
     '```python\ndef fizzbuzz(n):\n    if n % 15 == 0:\n',
     'A number divisible by both 3 and 5 is divisible by 15, so the first condition can also be `n % 15 == 0`:\n\n'
     '<!-- derive: from=solution replace="n % 3 == 0 and n % 5 == 0" with="n % 15 == 0" -->\n'
     '```python\ndef fizzbuzz(n):\n    if n % 15 == 0:\n'),
]
