import io, contextlib
qdefs = '''
from doctest import run_docstring_examples

def run_doctests(func):
    run_docstring_examples(func, globals(), name=func.__name__)
'''
trim14 = '''
def count_e(word):
    """Count the letter e (or E) in word.

    >>> count_e('Eerie')
    3
    >>> count_e('sky')
    0
    """
    count = 0
    for letter in word.lower():
        if letter == 'e':
            count += 1
    return count

run_doctests(count_e)
'''
trim17 = '''
def count_doubles(word):
    """>>> count_doubles('bookkeeper')
    3
    >>> count_doubles('cat')
    0
    >>> count_doubles('aaa')
    2
    """
    count = 0
    previous = ''
    for letter in word:
        if letter == previous:
            count += 1
        previous = letter
    return count

run_doctests(count_doubles)
'''
for name, body in [('Q14 trimmed', trim14), ('Q17 trimmed', trim17)]:
    ns = {'__name__': '__main__'}
    exec(qdefs, ns)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        exec(body, ns)
    print(name, 'output:', repr(buf.getvalue()))
