def run_code(code):
    """Run code (a string) as if it were a cell of its own.

    Some Answers use it for code whose result is an error: the error is shown as
    usual, but it does not stop Runtime > Run all.
    """
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
