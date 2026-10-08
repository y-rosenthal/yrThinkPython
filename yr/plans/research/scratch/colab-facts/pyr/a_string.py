def run_code(code):
    exec(code, globals())

run_code("""print('hello'
""")
run_code("""print(undefined_name)""")
run_code("""len(1, 2, 3)""")
