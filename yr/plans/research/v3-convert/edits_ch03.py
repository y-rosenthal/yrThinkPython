# Page edits for chapter 3 (convert_v3.py EDITS.py); plan section 5 wording table, audit fixes.
SUMMARY_STARTS = []

EDITS = [
    ('\n\nRun the next cell first: it defines `run_code`.', ''),
    ('Predict what this code displays, then run it to check.',
     'Predict what this code displays, then open the Answer to check.'),
    ('What does this cell display in a notebook?', 'What does this code display when it is run as a notebook cell?'),
    ('For each of the next three cells, predict', 'For each of the three parts, predict'),
    # sync writes "Run this cell to define ..." above the definition cells
    ('### Question 10 (medium): local variables and wrong calls\n\nRun this cell to define `add_and_show`.',
     '### Question 10 (medium): local variables and wrong calls'),
    ('### Question 14 (hard): tracebacks\n\nRun this cell to define `outer` and `inner`.',
     '### Question 14 (hard): tracebacks'),
    # lead-ins left dangling where a typed output was removed (audit)
    ('**Part a:** The call works and displays\n\n\n\nand then `print(total)` fails (a <!--=error-->`NameError`):',
     '**Part a:** The call works and displays its line, and then `print(total)` fails with a <!--=error-->`NameError`:'),
    ("It displays\n\n\n\nand then the error happens in `inner`, when it tries to add the number `1` to the string `'hi'` "
     "(a <!--=error-->`TypeError`):",
     "It displays `outer`'s line, and then the error happens in `inner`, when it tries to add the number `1` to the "
     "string `'hi'`: a <!--=error-->`TypeError`."),
    ("first the line `outer('hi')` in the cell,", "first the line `outer('hi')` in the question's code,"),
    # Q16: the solution also defines a helper; the header shows only the two functions asked for (E4)
    ('then a final `|`.\n\n**Examples**', 'then a final `|`.\n\n<!-- header: print_border print_grid -->\n\n**Examples**'),
]
