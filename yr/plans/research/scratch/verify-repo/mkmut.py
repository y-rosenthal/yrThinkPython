import nbformat as nbf, re, sys
def load(p): return nbf.read(p, as_version=4)
def save(nb, p): nbf.write(nb, p)
def find(nb, pred):
    return [i for i,c in enumerate(nb.cells) if pred(c)]

# M1: chap05 Q8 part a no longer raises (question + Answer cell consistent; Answer text still says SyntaxError)
nb = load('new/chap05_review.ipynb')
for c in nb.cells:
    if c.cell_type=='markdown' and c.source.startswith('### Question 8'):
        c.source = c.source.replace("x = 5\nif x = 5:\n    print('five')", "x = 5\nif x == 6:\n    print('five')")
    if c.cell_type=='code' and "if x = 5:" in c.source:
        c.source = c.source.replace("if x = 5:", "if x == 6:")
save(nb, 'mut/M1_new.ipynb')
nb = load('orig/chap05_review.ipynb')
for c in nb.cells:
    if c.cell_type=='code' and "if x = 5:" in c.source:
        c.source = c.source.replace("if x = 5:", "if x == 6:")
save(nb, 'mut/M1_orig.ipynb')

# M3: chap05 Q1: a '#### Note' heading inside the Answer, before the run cell
nb = load('new/chap05_review.ipynb')
i = next(i for i,c in enumerate(nb.cells) if c.cell_type=='code' and c.source.startswith('minutes = 135'))
nb.cells.insert(i, nbf.v4.new_markdown_cell('#### Note\n\nThe code again:'))
save(nb, 'mut/M3_new.ipynb')

# M2: chap02 Q4 last-expression display changed (Answer still says 12)
nb = load('new/chap02_review.ipynb')
for c in nb.cells:
    if 'price * 3' in c.source:
        c.source = c.source.replace('price * 3', 'price * 4')
save(nb, 'mut/M2_new.ipynb')
nb = load('orig/chap02_review.ipynb')
for c in nb.cells:
    if c.cell_type=='code' and 'price * 3' in c.source:
        c.source = c.source.replace('price * 3', 'price * 4')
save(nb, 'mut/M2_orig.ipynb')

# M15: stderr variant of run_code (the Colab fallback), plus a WRONG error text in chap05 Q8 part b's Answer
STDERR = '''def run_code(code):
    import sys
    ip = get_ipython()
    try:
        exec(code, globals())
    except Exception:
        print(ip.InteractiveTB.stb2text(ip.InteractiveTB.structured_traceback(*sys.exc_info())), file=sys.stderr)'''
nb = load('new/chap05_review.ipynb')
for c in nb.cells:
    if c.cell_type=='code' and 'def run_code(' in c.source:
        c.source = re.sub(r'def run_code\(code\):.*', STDERR, c.source, flags=re.S)
    if c.cell_type=='markdown' and "SyntaxError: expected ':'" in c.source:
        c.source = c.source.replace("SyntaxError: expected ':'", "SyntaxError: totally wrong message")
save(nb, 'mut/M15_new.ipynb')
