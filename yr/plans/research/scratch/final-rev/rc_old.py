def run_code(code):
    try:
        ip = get_ipython()
    except NameError:
        exec(code, globals())
        return
    result = ip.run_cell(code, store_history=False)
