# Page edits for chapter 7 (convert_v3.py EDITS.py); plan section 5 wording table, E6 (run_doctests where first
# used), E9 (Q14's fix derived from the question's code).
SUMMARY_STARTS = []

HELPER = ('from doctest import run_docstring_examples\n\ndef run_doctests(func):\n'
          '    run_docstring_examples(func, globals(), name=func.__name__)')
EDITS = [
    ('Run the next cell first: it downloads `words.txt` and defines `run_code`.',
     'The setup cell below downloads `words.txt`.'),
    ('Predict what this code displays, then run it to check.',
     'Predict what this code displays, then open the Answer to check.'),
    ('predict what it means, then run it.)', 'predict what it means, then open the Answer to see the number.)'),
    # Q14: the helper becomes a definition cell (NEW_CELLS); the run block keeps count_e and the call
    ('~~~python\n' + HELPER + '\n\ndef count_e', '~~~python\ndef count_e'),
    # Q14's fix, derived from the question's code
    ('Fix it by converting the word to lowercase first; then running the tests displays nothing, because they all pass:\n\n'
     '```python\ndef run_doctests(func):\n    run_docstring_examples(func, globals(), name=func.__name__)\n\ndef count_e(word):',
     'Fix it by converting the word to lowercase first; then running the tests displays nothing, because they all pass:\n\n'
     '<!-- derive: from=Q14 replace="for letter in word:" with="for letter in word.lower():" -->\n'
     '```python\ndef count_e(word):'),
    # Q17: the solution uses the provided helper and runs its doctests
    ('```python\ndef run_doctests(func):\n    run_docstring_examples(func, globals(), name=func.__name__)\n\n'
     'def count_doubles(word):', '```python\ndef count_doubles(word):'),
    ('        previous = letter\n    return count\n```',
     '        previous = letter\n    return count\n\nrun_doctests(count_doubles)\n```'),
]
NEW_CELLS = [('a7d0c714', 'e13328c2', HELPER, 'code')]
