def run_question(line, cell):
    """The %%run_question cell magic: run the code under it like a normal cell, show its output.

    Each Answer ends with a %%run_question cell that runs the question's code, so you can see
    its real output. Unlike a normal cell, an error is shown without stopping Runtime > Run all.
    """
    result = get_ipython().run_cell(cell)
    if isinstance(result.error_in_exec, KeyboardInterrupt):
        raise KeyboardInterrupt  # the Stop button still stops Run all

try:
    get_ipython().register_magic_function(run_question, 'cell')
except NameError:  # plain Python (e.g. the review tools): no cell magics
    pass
