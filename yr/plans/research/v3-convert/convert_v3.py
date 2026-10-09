"""One-off converter (plan section 5, Step 4): an old-format review page (<details> Answers) -> the v3 format.

    python convert_v3.py OLD.ipynb NEW.ipynb REMOVED.json EDITS.py

Static (no kernel). Everything it removes because sync will write it again is listed in REMOVED.json, so that
gate_v3.py can prove, after `review.sh sync`, that sync wrote the same thing:
  - question code cells -> '~~~python' run blocks (same id; the old run_code wrapper removed; part labels folded in);
    definition-only cells and '# Your code here' stay code cells;
  - the "Start from this header" block of write-code questions (kind 'header');
  - each ```text block or picture after a ```python example in a prompt (kind 'example');
  - each ```text block or picture in an Answer that showed the run block's output (kind 'run'); it is replaced by
    the run cell, at the place of the first one; an error line in it becomes <!--=error--> in the prose;
  - in Answers: import lines (sync writes them), example calls after a solution, and the question's own calls after a
    fix that only redefines a function (sync runs them) (kind 'trim');
  - values in prose written as `EXPR` is `V` with EXPR a literal expression -> `EXPR` is <!--=-->`V` (kind 'value');
  - page edits: the old run_code helper and its intro, '<details>' Answers -> '#### Answer'; EDITS.py holds the
    page's wording edits (each must match exactly once) and any hand-written cells.
"""
import ast
import json
import os
import re
import sys
from pathlib import Path

import nbformat as nbf

TOOLS = Path(os.environ.get('YR_TOOLS', Path(__file__).resolve().parents[5] / 'yrThinkPython' / 'yr' / 'tools'))
sys.path.insert(0, str(TOOLS))
import review_format as rf  # noqa: E402

DETAILS = re.compile(r'\s*<details>\s*<summary>Answer</summary>\s*(.*?)\s*</details>\s*$', re.S)
OLD_RUN_CODE = re.compile(r'^\s*run_code\(')
PART_LINE = re.compile(r'\n*\*\*Part (?P<part>[a-z])\*\*\s*$')
PART_PARA = re.compile(r'^\*\*Part [a-z]:\*\*', re.M)
EXPECTED = re.compile(r'```text\n.*?\n```|<img\b[^>]*\bdata-turtle\b[^>]*>', re.S)
HEADER = re.compile(r'Start from this header \(replace `\.\.\.` with the body\):\n\n```python\n.*?\n```\n*', re.S)
EXAMPLE_OUT = re.compile(r'(```python\n(?:(?!```).)*?\n```)\n(```text\n.*?\n```|<img\b[^>]*\bdata-turtle\b[^>]*>)', re.S)
VALUE = re.compile(r'`([^`\n]+)` is `([^`\n]+)`')
removed = []


def old_code(src):
    if OLD_RUN_CODE.match(src):
        return ast.parse(src).body[0].value.args[0].value.strip('\n')
    return src.strip('\n')


def definition_only(cell):
    if 'raises-exception' in rf.tags(cell) or OLD_RUN_CODE.match(cell.source):
        return False
    return rf.definition_cell_ok(cell.source)


def literal_value(expr):
    """repr of a literal-only expression (numbers, strings, operators), or None."""
    try:
        tree = ast.parse(expr, mode='eval')
    except SyntaxError:
        return None
    if any(isinstance(n, (ast.Name, ast.Call, ast.Attribute, ast.Subscript, ast.Lambda)) for n in ast.walk(tree)):
        return None
    try:
        return repr(eval(compile(tree, '<v>', 'eval'), {'__builtins__': {}}))
    except Exception:
        return None


def mark_values(md, where):
    """`EXPR` is `V` -> `EXPR` is <!--=-->`V`, where EXPR is a literal expression whose value is V."""
    def repl(m):
        if literal_value(m.group(1)) == m.group(2):
            removed.append({'kind': 'value', 'where': where, 'expr': m.group(1), 'value': m.group(2)})
            return f'`{m.group(1)}` is <!--=-->`{m.group(2)}`'
        return m.group(0)
    out = []
    for line in md.split('\n'):
        out.append(VALUE.sub(repl, line) if not line.lstrip().startswith(('```', '~~~')) else line)
    return '\n'.join(out)


def trim_block(code, where, drop_calls_of=None, calls=None):
    """Drop import lines (sync writes them) and, after the last def, example calls (write-code: calls of the
    functions the block defines) or the question's own calls (a fix that only redefines a function)."""
    tree = ast.parse(code)
    lines = code.split('\n')
    keep = []
    last_def = max((k for k, n in enumerate(tree.body) if isinstance(n, (ast.FunctionDef, ast.ClassDef))), default=-1)
    for k, n in enumerate(tree.body):
        seg = '\n'.join(lines[n.lineno - 1:n.end_lineno])
        if isinstance(n, (ast.Import, ast.ImportFrom)):
            removed.append({'kind': 'trim', 'where': where, 'text': seg})
            continue
        if k > last_def >= 0 and isinstance(n, ast.Expr) and isinstance(n.value, ast.Call):
            name = rf.used_names(seg)[:1]
            if (drop_calls_of and name and name[0] in drop_calls_of) or (calls is not None and seg.strip() in calls):
                removed.append({'kind': 'trim', 'where': where, 'text': seg})
                continue
        keep.append(seg)
    out = []
    for seg in keep:                                   # keep the blank lines between top-level statements
        if out and (seg.startswith(('def ', 'class ')) or out[-1].startswith(('def ', 'class '))):
            out.append('')
        out.append(seg)
    return '\n'.join(out).strip('\n')


def trim_answer_blocks(body, where, writecode, qcalls):
    def repl(m):
        code = m.group(1)
        if writecode:
            new = trim_block(code, where, drop_calls_of=set(rf.defined_functions(code)))
        else:
            new = trim_block(code, where, calls=qcalls if rf.defined_functions(code) else None)
        return f'```python\n{new}\n```'
    return re.sub(r'```python\n(.*?)\n```', repl, body, flags=re.S)


def error_marker(text, names):
    """Name the errors of a removed output block in the prose with <!--=error-->."""
    for name in names:
        if f'`{name}`' in text:
            text = text.replace(f'`{name}`', f'<!--=error-->`{name}`', 1)
        elif re.search(rf'\b{name}\b', text):
            text = re.sub(rf'\b{name}\b', f'<!--=error-->`{name}`', text, count=1)
        elif text.rstrip().endswith(':'):
            text = text.rstrip()[:-1] + f' ({article(name)} <!--=error-->`{name}`):\n'
        else:
            text = text.rstrip() + f' This is {article(name)} <!--=error-->`{name}`.\n'
    return text


def article(name):
    return 'an' if name[0] in 'AEIOU' else 'a'


def error_names(block):
    out = []
    for line in block.split('\n'):
        m = re.match(r'(' + rf.ERROR_NAME.pattern + r'):?', line)
        if m and m.group(1) not in out:
            out.append(m.group(1))
    return out


def md(text, cid):
    c = nbf.v4.new_markdown_cell(text.strip('\n'))
    c.id = cid
    return c


def convert_answer(answer, runs, title, writecode, qcalls, summary_starts):
    aid = answer.id
    head = md(rf.ANSWER_HEADING, aid)
    body = DETAILS.match(answer.source).group(1)
    body = trim_answer_blocks(body, title, writecode, qcalls)
    body = mark_values(body, title)
    out, k = [head], 0

    def add(text):
        nonlocal k
        if text.strip():
            out.append(md(text, rf.stable_id(aid, 'md', str(k))))
            k += 1

    if not runs:
        add(body)
        return out
    summary = ''
    for start in summary_starts:
        pos = body.find(start)
        if pos >= 0 and len(runs) > 1:
            body, summary = body[:pos], body[pos:]
    if len(runs) == 1:
        segments = [body]
    else:
        starts = [m.start() for m in PART_PARA.finditer(body)]
        if len(starts) != len(runs):
            sys.exit(f'{title}: {len(runs)} run blocks but {len(starts)} "**Part x:**" paragraphs')
        add(body[:starts[0]])
        segments = [body[a:b] for a, b in zip(starts, starts[1:] + [len(body)])]
    for (part, code), seg in zip(runs, segments):
        blocks, before, pos = [], '', 0
        for m in EXPECTED.finditer(seg):
            if '```python' in seg[:m.start()]:
                break
            before += seg[pos:m.start()]
            blocks.append(m.group(0))
            pos = m.end()
        after = seg[pos:] if blocks else ''
        before = before if blocks else seg
        names = [n for b in blocks for n in error_names(b)]
        before = error_marker(before, names)
        for b in blocks:
            removed.append({'kind': 'run', 'where': title, 'part': part, 'block': b})
        add(before)
        number = rf.QUESTION_LINE.match('### ' + title).group('num')
        rc = nbf.v4.new_code_cell(rf.render_run_cell(code, False, number, part if len(runs) > 1 else None))
        rc.id = rf.stable_id(aid, 'run', part or '-')
        rc.metadata = dict(rf.RUN_CELL_METADATA)
        out.append(rc)                                 # where the old output was; sync stores its output
        add(after)
    add(summary)
    return out


def main(src, dst, removed_path, edits_path):
    edits = {}
    exec(Path(edits_path).read_text(), edits)
    nb = nbf.read(src, as_version=4)
    cells, out = nb.cells, []
    i = 0
    while i < len(cells):
        c = cells[i]
        s = c.source
        if c.cell_type == 'markdown' and s.lstrip().startswith('## Questions'):
            c.source = re.sub(r'\n*Some questions show their code inside `run_code.*?prediction\.\n*', '\n\n', s,
                              flags=re.S).strip('\n')
            out.append(c)
            i += 1
            continue
        if c.cell_type == 'code' and 'setup' in rf.tags(c):
            c.source = re.sub(r'\n*def run_code\(code\):.*', '', s, flags=re.S).rstrip('\n')
            out.append(c)
            i += 1
            continue
        if c.cell_type == 'markdown' and not rf.QUESTION_LINE.match(s):
            if '<summary><strong>' in s:
                c.source = mark_values(s, 'Concepts')
            out.append(c)
            i += 1
            continue
        if c.cell_type != 'markdown':
            out.append(c)
            i += 1
            continue
        j = i + 1
        while j < len(cells) and not (cells[j].cell_type == 'markdown' and (
                re.match(r'\s*#{1,3} ', cells[j].source) or cells[j].source.lstrip().startswith('*Summary and'))):
            j += 1
        title = s.lstrip('# ').split('\n')[0]
        group = cells[i:j]
        writecode = any(g.cell_type == 'code' and g.source.strip() == rf.PLACEHOLDER for g in group)
        label, runs, answer = None, [], None
        for g in group:
            if g.cell_type == 'markdown' and DETAILS.match(g.source):
                answer = g
                continue
            if g.cell_type == 'markdown':
                t = g.source
                if writecode:
                    for m in HEADER.finditer(t):
                        removed.append({'kind': 'header', 'where': title, 'text': m.group(0).strip()})
                    t = HEADER.sub('', t)

                def ex(m):
                    removed.append({'kind': 'example', 'where': title, 'code': m.group(1)[10:-4], 'block': m.group(2)})
                    return m.group(1)
                t = EXAMPLE_OUT.sub(ex, t)
                t = mark_values(t, title)
                m = PART_LINE.search(t)
                if m:
                    label, t = m.group('part'), t[:m.start()]
                if t.strip():
                    g.source = t.rstrip('\n')
                    out.append(g)
                continue
            if g.source.strip() == rf.PLACEHOLDER or definition_only(g):
                g.metadata.pop('tags', None) if g.source.strip() != rf.PLACEHOLDER else None
                out.append(g)
                continue
            code = old_code(g.source)
            out.append(md((f'**Part {label}**\n\n' if label else '') + f'~~~python\n{code}\n~~~', g.id))
            runs.append((label, code))
            label = None
        if answer is None:
            sys.exit(f'{title}: no <details> Answer')
        qcalls = {line.strip() for code in [c for _, c in runs] for line in rf.calls_only(code).split('\n') if line.strip()}
        out.extend(convert_answer(answer, runs, title, writecode, qcalls, edits.get('SUMMARY_STARTS', [])))
        i = j
    nb.cells = out
    nb.metadata.pop('colab', None)
    # wording edits: (old, new), each must match exactly once on the page
    text = json.dumps([c.source for c in nb.cells])
    for old, new in edits.get('EDITS', []):
        n = sum(c.source.count(old) for c in nb.cells)
        if n != 1:
            sys.exit(f'edit matches {n} times (must be 1): {old[:80]!r}')
        for c in nb.cells:
            if old in c.source:
                c.source = c.source.replace(old, new)
    for cid, after_id, text in edits.get('NEW_CELLS', []):   # hand-written markdown cells
        at = next(k for k, c in enumerate(nb.cells) if c.id == after_id)
        nb.cells.insert(at + 1, md(text, cid))
    nbf.validate(nb)
    nbf.write(nb, dst)
    Path(removed_path).write_text(json.dumps(removed, indent=1, ensure_ascii=False))
    kinds = {}
    for r in removed:
        kinds[r['kind']] = kinds.get(r['kind'], 0) + 1
    print(f'wrote {dst}: {len(nb.cells)} cells; removed for sync to regenerate: {kinds}')
    for k, cell in enumerate(nb.cells):
        if cell.cell_type == 'markdown':
            for m in re.finditer(r'[^\n]*(\bcells?\b|\brun (it|this|the)\b|run_code)[^\n]*', cell.source):
                print(f'  review wording, cell {k}: {m.group(0)[:120]}')


if __name__ == '__main__':
    main(*sys.argv[1:5])
