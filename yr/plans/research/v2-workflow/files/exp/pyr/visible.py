from os.path import basename, exists

def download(url):
    filename = basename(url)
    if not exists(filename):
        from urllib.request import urlretrieve

        local, _ = urlretrieve(url, filename)
        print("Downloaded " + str(local))
    return filename

download('https://github.com/ramalho/jupyturtle/releases/download/2024-03/jupyturtle.py');

from jupyturtle import make_turtle, forward, left, right, penup, pendown

def run_code(code):
    """Run code (a string) as if it were a cell of its own.

    Some Answers use it for code whose result is an error: the error is shown as
    usual, but it does not stop Runtime > Run all.
    """
    code = code.removeprefix('\n')   # the code starts on the line after run_code(r"""
    try:
        from IPython import get_ipython
        ip = get_ipython()
    except ImportError:
        ip = None
    if ip is None:                    # plain Python (the review tools): just run it
        exec(code, globals())
        return
    result = ip.run_cell(code, store_history=False)
    if isinstance(result.error_in_exec, KeyboardInterrupt):
        raise KeyboardInterrupt       # the Stop button still stops Run all

# Your code here

# Your code here

# Your code here

# Your code here

def countdown_by_two(n):
    if n == 0:
        print('Blastoff!')
    else:
        countdown_by_two(n - 2)

# Your code here

# Your code here
