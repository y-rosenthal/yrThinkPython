from doctest import run_docstring_examples
def f(x):
    """>>> f(1)
    3
    """
    return 2
run_docstring_examples(f, globals(), name=f.__name__)
