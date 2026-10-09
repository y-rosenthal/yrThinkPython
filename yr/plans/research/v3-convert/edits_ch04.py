# Page edits for chapter 4 (convert_v3.py EDITS.py); plan section 5 wording table, E6 (square and jump in a
# definition cell in Q11; later questions point to it), audit fixes.
SUMMARY_STARTS = ['In all three parts the caller broke a precondition', 'Some correct calls:']

SQUARE_JUMP = ('def square(length):\n    for i in range(4):\n        forward(length)\n        left(90)\n\n'
               'def jump(length):\n    """Move forward length units without drawing."""\n    penup()\n    forward(length)\n'
               '    pendown()')
JUMP_POLYGON = ('def jump(length):\n    """Move forward length units without drawing."""\n    penup()\n    forward(length)\n'
                '    pendown()\n\ndef polygon(n, length):\n    angle = 360 / n\n    for i in range(n):\n        forward(length)\n'
                '        left(angle)')

EDITS = [
    ('Run the next cell first: it downloads `jupyturtle`, imports the functions the questions use, and defines `run_code`.',
     'The setup cell below downloads `jupyturtle` and imports the functions the questions use.'),
    ('Predict what this code displays, then run it to check.',
     'Predict what this code displays, then open the Answer to check.'),
    ('Describe the drawing this code makes, then run it to check.',
     'Describe the drawing this code makes, then open the Answer to check.'),
    ('and run only the setup cell (at the start of the Questions) and this cell.',
     'and run only the setup cells (at the start of the Questions), and then this code.'),
    ('For each of the next three cells, predict what happens.', 'For each of the three parts, predict what happens.'),
    ('Predict the error for each, then run the cells to check.', 'Predict the error for each, then open the Answer to check.'),
    # sync writes "Run this cell to define ..." above definition cells
    ('Run this cell to define `polygon`. Its docstring states its preconditions.',
     "`polygon`'s docstring states its preconditions."),
    ('### Question 15 (hard): keyword arguments\n\nRun this cell to define `describe`.',
     '### Question 15 (hard): keyword arguments'),
    # dangling lead-in where the typed picture and error were removed (audit)
    ('The turtle draws one line, `50` units to the east:\n\n\n\nThen Python stops with an error (a <!--=error-->`NameError`):',
     'The turtle draws one line, `50` units to the east, and then Python stops with a <!--=error-->`NameError`:'),
    # E12
    ('`angle = 360 / 4.5` works (it is `80.0`)', '`angle = 360 / 4.5` works (it is <!--= 360 / 4.5 -->`80.0`)'),
    # E6: Q17 and Q18 use the helpers defined in Q11 and Q14; their solutions don't repeat them
    ('You may use these two functions:\n\n```python\n' + SQUARE_JUMP + '\n```\n\nHint:',
     '<!-- header: grid -->\n\nHint:'),                       # its solution also defines a helper, `row`
    ('You may use these two functions:\n\n```python\n' + JUMP_POLYGON + '\n```\n\n**Examples**', '**Examples**'),
    ('```python\n' + SQUARE_JUMP + '\n\ndef row_of_squares', '```python\ndef row_of_squares'),
    ('```python\n' + SQUARE_JUMP + '\n\ndef row(cols', '```python\ndef row(cols'),
    ('```python\n' + SQUARE_JUMP + '\n\ndef grid(', '```python\ndef grid('),
    ('```python\n' + JUMP_POLYGON + '\n\ndef polygon_row', '```python\ndef polygon_row'),
]
# Q11: the two helpers it provides become a definition cell, before its examples
SPLITS = [('2f148fad', 'You may use these two functions:', '**Examples**', SQUARE_JUMP, 'b4d1e7a2', 'c9e02f51')]
