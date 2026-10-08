"""Build Q8 variants for the DRY options B (string variable) and C' (%%question cell magic)
from the converted notebook; write them to out/dry_B.ipynb and out/dry_C.ipynb."""
import re, copy, secrets
import nbformat as nbf
nb0 = nbf.read('repo/yr/chap05_review.ipynb', 4)
parts = {'a': "x = 5\nif x = 5:\n    print('five')", 'b': "x = 5\nif x > 0\n    print('positive')", 'c': "x = 5\n y = 6"}
MAGIC = '''
from IPython.core.magic import register_cell_magic

@register_cell_magic
def question(line, cell):
    """%%question NAME: store the cell's code in the variable NAME, without running it.
    The Answer runs it with run_code(NAME)."""
    get_ipython().user_ns[line.strip()] = cell'''

def build(kind):
    nb = copy.deepcopy(nb0)
    cells = nb.cells
    q = next(i for i, c in enumerate(cells) if c.source.startswith('### Question 8'))
    h = q + 1
    assert cells[h].source.strip() == '#### Answer'
    def code(s):
        c = nbf.v4.new_code_cell(s); c.id = secrets.token_hex(4); return c
    def md(s):
        c = nbf.v4.new_markdown_cell(s); c.id = secrets.token_hex(4); return c
    new_q = [md('### Question 8 (medium): find the error\n\nEach part has one mistake. Predict the error for each, then open the Answer to check.')]
    for p, src in parts.items():
        new_q.append(md(f'**Part {p}**'))
        if kind == 'B':
            new_q.append(code(f'q8{p} = """\n{src}\n"""'))
        else:
            new_q.append(code(f'%%question q8{p}\n{src}'))
    # answer: keep heading + explanation; replace run cells
    expl = cells[h + 1]
    runs = [code(f'run_code(q8{p})') for p in parts]
    j = h + 2
    while j < len(cells) and cells[j].cell_type == 'code':
        j += 1
    nb.cells = cells[:q] + new_q + [cells[h], expl] + runs + cells[j:]
    if kind == 'C':
        setup = next(c for c in nb.cells if 'setup' in c.metadata.get('tags', []))
        setup.source += '\n' + MAGIC
    nbf.write(nb, f'out/dry_{kind}.ipynb')
build('B'); build('C')
print('ok')
