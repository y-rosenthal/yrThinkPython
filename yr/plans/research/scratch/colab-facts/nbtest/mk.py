import nbformat, sys
nb = nbformat.v4.new_notebook()
setup = r'''
import sys
def run_code(code):
    try:
        exec(compile(code, "<question>", "exec"), globals())
    except Exception:
        get_ipython().showtraceback()

def run_code_stream(code):
    try:
        exec(compile(code, "<question>", "exec"), globals())
    except Exception:
        ip = get_ipython()
        etype, value, tb = sys.exc_info()
        stb = ip.InteractiveTB.structured_traceback(etype, value, tb)
        print(ip.InteractiveTB.stb2text(stb), file=sys.stderr)
'''
nb.cells = [nbformat.v4.new_code_cell(setup),
            nbformat.v4.new_code_cell('run_code("""print(undefined_name)""")'),
            nbformat.v4.new_code_cell('run_code_stream("""print(undefined_name)""")'),
            nbformat.v4.new_code_cell('run_code("""if x = 3:\n    pass""")'),
            nbformat.v4.new_code_cell('print("reached the end")')]
nbformat.write(nb, sys.argv[1])
