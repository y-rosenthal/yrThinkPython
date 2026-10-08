def run_code(code):
    """Run code (a string) as if it were a cell of its own."""
    try:
        ip = get_ipython()
    except NameError:                 # plain Python (the review tools): just run it
        exec(code, globals())
        return
    result = ip.run_cell(code, store_history=False)
    if isinstance(result.error_in_exec, KeyboardInterrupt):
        raise KeyboardInterrupt       # the Stop button still stops Run all
