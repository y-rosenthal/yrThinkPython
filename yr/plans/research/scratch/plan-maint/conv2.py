"""Experiment: convert a review page to the 'run block' layout.
- each question code cell (not definition-only, not '# Your code here') becomes a markdown cell
  with the SAME id holding ```python run ... ```
- <details> Answer -> '#### Answer' heading (fresh id, collapsed metadata) + body cell (old id)
- Answer run cells: ALWAYS run_code(r\"\"\"...\"\"\") (r''' if the code has \"\"\"), '# Part x' comment if 2+
usage: conv2.py OLD NEW
"""
import ast, re, secrets, string, sys
import nbformat as nbf

DETAILS = re.compile(r'\s*<details>\s*<summary>Answer</summary>\s*(.*?)\s*</details>\s*$', re.S)
RUN_CODE = re.compile(r'\s*run_code\("""\n(.*?)\n?"""\)\s*$', re.S)
CREDIT = '*Summary and questions by'
RUN_CODE_DEF = '''def run_code(code):
    """Run the code in the string code as if it were a cell of its own.

    Each Answer ends with code cells that run the question's code this way, so that you can
    see its real output. An error is shown, but it does not stop Runtime > Run all.
    """
    try:
        shell = get_ipython()
    except NameError:  # not in Jupyter or Colab: run it as plain Python
        exec(code, globals())
        return
    result = shell.run_cell(code)
    if isinstance(result.error_in_exec, KeyboardInterrupt):
        raise KeyboardInterrupt  # the Stop button still stops Run all'''


def render_run_cell(code, label=None):
    q = '"""' if '"""' not in code else "'''"
    if q in code or code.endswith('\\'):
        raise SystemExit(f'cannot quote: {code!r}')
    s = f'run_code(r{q}\n{code}\n{q})'
    return (f'# Part {label}\n' + s) if label else s


def is_definition_only(code):
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return False
    return all(isinstance(s, (ast.FunctionDef, ast.ClassDef, ast.Import, ast.ImportFrom, ast.Assign)) for s in tree.body)


def main(src, dst):
    nb = nbf.read(src, as_version=4)
    used = {c.id for c in nb.cells}

    def fresh():
        while True:
            i = secrets.token_hex(4)
            if i not in used:
                used.add(i); return i

    out, collapsed, kept = [], [], 0
    cells = nb.cells
    i = 0
    while i < len(cells):
        c = cells[i]
        if c.cell_type == 'code' and 'setup' in c.metadata.get('tags', []):
            if 'def run_code(' in c.source:
                c.source = re.sub(r'def run_code\(code\):.*', lambda m: RUN_CODE_DEF, c.source, flags=re.S)
            else:
                c.source = c.source.rstrip() + '\n\n\n' + RUN_CODE_DEF
        if c.cell_type == 'markdown' and c.source.lstrip().startswith(CREDIT):
            c.source = '## Credits\n\n' + c.source
        if not (c.cell_type == 'markdown' and c.source.lstrip().startswith('### ')):
            out.append(c); i += 1; continue
        j = i + 1
        while j < len(cells) and not (cells[j].cell_type == 'markdown' and (
                re.match(r'\s*#{1,3} ', cells[j].source) or cells[j].source.lstrip().startswith(CREDIT))):
            j += 1
        blocks, answer = [], None
        for g in cells[i:j]:
            if g.cell_type == 'markdown' and DETAILS.match(g.source):
                answer = g; continue
            if g.cell_type == 'markdown' or g.source.strip() == '# Your code here':
                out.append(g); continue
            m = RUN_CODE.match(g.source)
            body = m.group(1) if m else g.source.strip('\n')
            if not m and 'raises-exception' not in g.metadata.get('tags', []) and is_definition_only(body):
                out.append(g); continue  # definition cell stays a code cell
            md = nbf.v4.new_markdown_cell(f'```python run\n{body}\n```')
            md.id = g.id; kept += 1
            out.append(md); blocks.append(body)
        if answer is not None:
            head = nbf.v4.new_markdown_cell('#### Answer')
            head.id = fresh(); head.metadata = {'id': head.id, 'jp-MarkdownHeadingCollapsed': True}
            collapsed.append(head.id); out.append(head)
            body = nbf.v4.new_markdown_cell(DETAILS.match(answer.source).group(1)); body.id = answer.id
            out.append(body); kept += 1
            for k, b in enumerate(blocks):
                rc = nbf.v4.new_code_cell(render_run_cell(b, string.ascii_lowercase[k] if len(blocks) > 1 else None))
                rc.id = fresh(); rc.metadata = {}
                out.append(rc)
        i = j
    nb.cells = out
    nb.metadata['colab'] = {'collapsed_sections': collapsed}
    nbf.validate(nb)
    nbf.write(nb, dst)
    print(f'{dst}: {len(out)} cells, {len(collapsed)} answers, {kept} old ids kept on converted cells')


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
