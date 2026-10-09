"""The format of the review pages (yr/chapNN_review.ipynb): the one place that defines it. Stdlib only;
works on raw JSON dicts and on nbformat nodes (cairosvg is imported only to render a drawing).

See yr/README.md for the rules a person follows, and yr/plans/runall-collapsible-answers.md section 2 for the
design. In short, a question is:

  [md]   ### Question 8 (medium): find the error         number: digits and an optional letter (3b); stable
  [md]   prompt ...                                       may hold examples (```python + generated output)
  [md]   **Part a**\\n\\n~~~python\\n<code>\\n~~~            RUN BLOCK: the question's code, typed once
  [code] definition cells, '# Your code here'
  [md]   #### Answer                                      saved collapsed (Colab and JupyterLab)
  [md]   **Part a:** ... <!--=error-->`SyntaxError` ...   explanation; markers that sync fills
  [code] # @title Output of Question 8a                   RUN CELL, written by sync: code hidden, output stored;
         if 'run_code' in globals():                      wrapped in the page's run_code helper when the code
             run_code(r\"\"\"...\"\"\")                     raises or prints a line number (traceback printed
         else: ...                                        as text: Run all never stops, nothing turns red)

Everything that can be derived is written by `review.sh sync` (sync_review.py) by running the code on the pinned
Colab-like stack, and `review.sh check` (check_review.py) fails if sync would change anything.
"""
import ast
import base64
import hashlib
import json
import re
import struct

# ---------------------------------------------------------------- constants

ANSWER_HEADING = '#### Answer'
PLACEHOLDER = '# Your code here'
CREDITS_HEADING = '## Credits'
STAMP_KEY = 'yr_review'
QUESTION_HEADING = re.compile(r'^### Question (?P<num>\d+[a-z]?) \((?P<level>[^)]*)\): *(?P<kind>.*)$')
QUESTION_LINE = re.compile(r'^\s*### Question (?P<num>\d+[a-z]?)\b')
RUN_FENCE = re.compile(r'^(?:\*\*Part (?P<part>[a-z])\*\*[ \t]*\n\n)?~~~python\n(?P<code>.*?)\n~~~[ \t]*$', re.S)
PART_CELL = re.compile(r'^\*\*Part (?P<part>[a-z]):\*\*')
TITLE_LINE = re.compile(r'^#\s*@title\b(?P<rest>.*)$')            # any form Colab may write
TITLE_TEXT = re.compile(r'Output of Question (?P<num>\d+[a-z]?)(?:, part (?P<part>[a-z]))?')
ANSI = re.compile(r'\x1b\[[0-9;]*[A-Za-z]')
RUN_CELL_METADATA = {'cellView': 'form', 'jupyter': {'source_hidden': True}}
HELPER_TITLE = '# @title Helper for the Answers'
GUARD_MESSAGE = 'Run the setup cells first: Runtime → Run all.'
# Run-block hazards: Colab form markup (parsed on any line), cell magics, a ~~~ line (would end the fence)
BLOCK_HAZARD = re.compile(r'#\s*@(title|param|markdown)\b|^%%|^\s{0,3}~~~', re.M)
# output that names a line number: shifted by 1 in a plain run cell (its first line is the title)
LINE_REF = re.compile(r'\bline \d+\b|<>:\d+:|Cell In\[')
MEM_ADDR = re.compile(r' at 0x[0-9a-fA-F]{6,}')
MAX_OUTPUT_CHARS, MAX_OUTPUT_LINES = 8000, 60
ERROR_NAME = re.compile(r'\b([A-Z][A-Za-z]*(?:Error|Exception|Warning)|KeyboardInterrupt|StopIteration|SystemExit)\b')
# the line of a traceback that names the exception (the LAST such line: Colab adds a NOTE after import errors)
EXC_LINE = re.compile(r'^(?P<name>[A-Z][A-Za-z]*(?:Error|Exception|Warning)|KeyboardInterrupt|StopIteration|SystemExit)'
                      r'(?::|$)', re.M)
FENCE_OPEN = re.compile(r'^ {0,3}(`{3,}|~{3,})(.*)$')
# The stack that writes stored outputs: Colab's (seen 2026-10-09). colablike.lock pins every package.
PINNED_STACK = {'python': '3.13', 'ipython': '7.34.0', 'ipykernel': '6.17.1'}
STACK_PROBE = ("import sys as _s, json as _j, IPython as _I, ipykernel as _k\n"
               "print(_j.dumps({'python': '%d.%d.%d' % _s.version_info[:3], 'ipython': _I.__version__, "
               "'ipykernel': _k.__version__}))")

HELP_NOTE = '''**Using this page in Colab or Jupyter**

- Each question's **Answer** is closed: click the arrow next to **Answer** to open it. For questions about what code displays or draws, the Answer also shows that code's output. The output is saved with the page, so it is there before you run anything. The code that produced it is hidden: click **Show code** in Colab, or the grey bar in Jupyter, to see it.
- To run code yourself, start with **Runtime → Run all** (Jupyter: **Run → Run All Cells**). It runs the page's setup and re-runs the code in every Answer. The Answers stay closed, and Run all does not stop at the errors that are answers. If Colab warns that the notebook was not authored by Google, choose **Run anyway**.
- Run your own code with **Ctrl+Enter**.
- When an Answer's code runs again, its output comes from your session. It can differ from the saved output if the setup has not run yet, or if your own code changed a name that the question uses.
- VS Code, GitHub's preview and nbviewer show the Answers open.'''

HELPER_CELL = HELPER_TITLE + '''
def run_code(code):
    """Run code as a cell of its own; print an error's traceback as text instead of raising."""
    import sys
    from IPython import get_ipython
    ip = get_ipython()
    if ip is None:
        exec(code, globals())
        return
    def to_stderr(etype, evalue, stb):
        stb = getattr(stb, 'stb', stb)           # Colab passes a ColabTraceback for import errors
        print(ip.InteractiveTB.stb2text(stb), file=sys.stderr)
    ip._showtraceback = to_stderr
    try:
        ip.run_cell(code, store_history=False)
    finally:
        del ip._showtraceback'''

CREDITS = '''## Credits

*Summary and questions by Prof. Y. Rosenthal, based on*
[Think Python: 3rd Edition](https://allendowney.github.io/ThinkPython/index.html) *by Allen B. Downey.*
*Text license:* [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International](https://creativecommons.org/licenses/by-nc-sa/4.0/)'''

TITLE_CELL = '''# {N}b. Prof. Rosenthal's Review

A review of [Chapter {N}: {TITLE}](https://y-rosenthal.github.io/yrThinkPython/chap{NN}.html),
for students who have already studied the chapter.
Use the two lists under **Concepts covered** as a checklist (click a list's title to hide it), then work through the **Questions**, which go from easy to hard.
Each question has a suggested answer under **Answer**. Try the question first, then open the Answer.

[Run this page on Colab](https://colab.research.google.com/github/y-rosenthal/yrThinkPython/blob/v3/yr/chap{NN}_review.ipynb)'''
TITLE_CELL_PARSE = re.compile(r'^# (?P<N>\d+)b\. Prof\. Rosenthal\'s Review\n\nA review of \[Chapter \d+: (?P<TITLE>[^\]]*)\]')


def title_cell(n, title):
    return TITLE_CELL.replace('{NN}', f'{n:02d}').replace('{N}', str(n)).replace('{TITLE}', title)


# ---------------------------------------------------------------- small helpers

def source(cell):
    s = cell['source']
    return ''.join(s) if isinstance(s, list) else s


def text_of(v):
    return ''.join(v) if isinstance(v, list) else v


def tags(cell):
    return list(cell.get('metadata', {}).get('tags', []))


def sha1(b):
    return hashlib.sha1(b if isinstance(b, bytes) else b.encode()).hexdigest()


def stable_id(*parts):
    """A new cell id derived from its context, so sync is deterministic."""
    return sha1(':'.join(parts))[:8]


def heading_level(md):
    """Smallest heading level in a markdown cell (ATX, setext or HTML <hN>), outside code fences; or None."""
    lines, fence, best = md.split('\n'), None, None
    for k, line in enumerate(lines):
        m = FENCE_OPEN.match(line)
        if m and (fence is None or (m.group(1)[0] == fence[0] and len(m.group(1)) >= len(fence)
                                    and not m.group(2).strip())):
            fence = None if fence else m.group(1)
            continue
        if fence:
            continue
        m = re.match(r'\s{0,3}(#{1,6})(\s|$)', line)
        lev = len(m.group(1)) if m else None
        if lev is None and k > 0 and lines[k - 1].strip() and not lines[k - 1].lstrip().startswith(('-', '*', '<')) \
                and re.match(r'\s{0,3}(=+|-+)\s*$', line):
            lev = 1 if '=' in line else 2
        if lev is None:
            h = re.search(r'<h([1-6])\b', line, re.I)
            lev = int(h.group(1)) if h else None
        if lev and (best is None or lev < best):
            best = lev
    return best


def strip_fences(md):
    """Markdown without fenced code blocks (for prose rules)."""
    return re.sub(r'^ {0,3}(```|~~~).*?^ {0,3}\1[ \t]*$', '', md, flags=re.S | re.M)


def page_format(nb):
    """'v3' (Answer headings), 'legacy' (<details> Answers), 'mixed' or 'empty'."""
    new = old = False
    for c in nb['cells']:
        if c['cell_type'] != 'markdown':
            continue
        s = source(c)
        new |= s.strip() == ANSWER_HEADING
        old |= bool(re.match(r'\s*<details>\s*<summary>Answer</summary>', s))
    return {(True, False): 'v3', (False, True): 'legacy', (True, True): 'mixed'}.get((new, old), 'empty')


# ---------------------------------------------------------------- python source analysis

def parses(src):
    try:
        return ast.parse(src)
    except SyntaxError:
        return None


def module_bindings(src):
    """Names bound at module level by Python source (empty if it does not parse)."""
    tree, names = parses(src), []
    for node in (tree.body if tree else []):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.append(node.name)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            names.extend((a.asname or a.name).split('.')[0] for a in node.names)
        else:
            for t in ast.walk(node):
                if isinstance(t, ast.Name) and isinstance(t.ctx, ast.Store) and t.id not in names:
                    names.append(t.id)
    return names


def defined_functions(src):
    tree = parses(src)
    return [n.name for n in (tree.body if tree else []) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]


def assigned_names(src):
    tree, names = parses(src), []
    for node in (tree.body if tree else []):
        if isinstance(node, (ast.Assign, ast.AugAssign, ast.AnnAssign)):
            for t in ast.walk(node):
                if isinstance(t, ast.Name) and isinstance(t.ctx, ast.Store) and t.id not in names:
                    names.append(t.id)
    return names


def only_definitions(src):
    """True if the code only defines functions/classes (and imports): such a fix is run with the question's calls."""
    tree = parses(src)
    return bool(tree) and bool(tree.body) and all(
        isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Import, ast.ImportFrom))
        for n in tree.body)


def definition_cell_ok(src):
    """A definition cell only defines (def/class/import/assignment), so it displays nothing."""
    tree = parses(src)
    return bool(tree) and all(isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Import,
                                             ast.ImportFrom, ast.Assign, ast.AnnAssign)) for n in tree.body)


def calls_only(src):
    """The top-level statements of the question's code that are not definitions (its calls), as source."""
    tree = parses(src)
    if not tree:
        return ''
    lines = src.split('\n')
    keep = [n for n in tree.body if not isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef,
                                                        ast.Import, ast.ImportFrom))]
    return '\n'.join('\n'.join(lines[n.lineno - 1:n.end_lineno]) for n in keep)


def used_names(src):
    """Names the code reads (loaded anywhere), minus names it binds anywhere (module level, parameters, locals)."""
    tree = parses(src)
    if not tree:
        return []
    loads, binds = [], set()
    for t in ast.walk(tree):
        if isinstance(t, ast.Name):
            if isinstance(t.ctx, ast.Load):
                if t.id not in loads:
                    loads.append(t.id)
            else:
                binds.add(t.id)
        elif isinstance(t, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            binds.add(t.name)
        elif isinstance(t, ast.arg):
            binds.add(t.arg)
        elif isinstance(t, (ast.Import, ast.ImportFrom)):
            binds.update((a.asname or a.name).split('.')[0] for a in t.names)
    return [n for n in loads if n not in binds]


def def_headers(src, names=None):
    """The def lines (signature only) of the module-level functions in src, in order; only `names` if given."""
    tree, lines, out = parses(src), src.split('\n'), []
    for n in (tree.body if tree else []):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and (names is None or n.name in names):
            first = n.lineno - 1
            last = n.body[0].lineno - 2                     # the line before the body's first statement
            head = lines[first:last + 1]
            while head and not head[-1].rstrip().endswith(':'):
                head.pop()
            out.append('\n'.join(head) if head else lines[first])
    return out


def setup_imports(nb):
    """{name: (module, original name or None for 'import module')} bound by the import statements of the
    setup cells, in order."""
    out = {}
    for c in nb['cells']:
        if c['cell_type'] != 'code' or 'setup' not in tags(c):
            continue
        tree = parses(source(c))
        for node in (tree.body if tree else []):
            if isinstance(node, ast.ImportFrom) and node.module:
                for a in node.names:
                    out[a.asname or a.name] = (node.module, a.name, a.asname)
            elif isinstance(node, ast.Import):
                for a in node.names:
                    out[(a.asname or a.name).split('.')[0]] = (a.name, None, a.asname)
    return out


def import_lines(code, imports):
    """The import lines a block needs for the names it uses that the setup cells import (E5)."""
    need = [n for n in used_names(code) if n in imports]
    order = list(imports)
    need.sort(key=order.index)
    plain, froms = [], {}
    for n in need:
        module, name, asname = imports[n]
        if name is None:
            line = f'import {module}' + (f' as {asname}' if asname else '')
            if line not in plain:
                plain.append(line)
        else:
            froms.setdefault(module, []).append(name + (f' as {asname}' if asname else ''))
    return plain + [f'from {m} import {", ".join(ns)}' for m, ns in froms.items()]


# ---------------------------------------------------------------- markdown tokens

class Tok:
    """A run of lines of a markdown cell: kind 'text', 'fence' (info, code, char), 'region' (kind, body)
    or 'marker' (name, arg)."""
    __slots__ = ('kind', 'lines', 'info', 'code', 'name', 'arg')

    def __init__(self, kind, lines, info='', code='', name='', arg=''):
        self.kind, self.lines, self.info, self.code, self.name, self.arg = kind, lines, info, code, name, arg

    def __repr__(self):
        return f'Tok({self.kind}, {self.name or self.info!r}, {self.lines[:1]})'


REGION_BEGIN = re.compile(r'^<!-- begin generated: (?P<kind>[\w-]+) -->$')
REGION_END = '<!-- end generated: {} -->'
BLOCK_MARKER = re.compile(r'^<!--\s*(?P<name>not a solution|header|derive|generated imports|do)\s*(?::\s*(?P<arg>.*?))?\s*-->$')
REGION_KINDS = ('header', 'example', 'then-try', 'output', 'uses', 'define')


def md_tokens(md):
    lines, toks, i = md.split('\n'), [], 0
    while i < len(lines):
        line = lines[i]
        m = FENCE_OPEN.match(line)
        if m:
            fence = m.group(1)
            j = i + 1
            close = re.compile(r'^ {0,3}' + re.escape(fence[0]) + '{' + str(len(fence)) + r',}\s*$')
            while j < len(lines) and not close.match(lines[j]):
                j += 1
            toks.append(Tok('fence', lines[i:j + 1], info=m.group(2).strip(), code='\n'.join(lines[i + 1:j]),
                            name=fence[0]))
            i = j + 1
            continue
        m = REGION_BEGIN.match(line)
        if m:
            end = REGION_END.format(m.group('kind'))
            j = i + 1
            while j < len(lines) and lines[j] != end:
                j += 1
            toks.append(Tok('region', lines[i:j + 1], name=m.group('kind'), code='\n'.join(lines[i + 1:j])))
            i = j + 1
            continue
        m = BLOCK_MARKER.match(line)
        if m:
            toks.append(Tok('marker', [line], name=m.group('name'), arg=(m.group('arg') or '').strip()))
            i += 1
            continue
        if toks and toks[-1].kind == 'text':
            toks[-1].lines.append(line)
        else:
            toks.append(Tok('text', [line]))
        i += 1
    return toks


def md_join(toks):
    return '\n'.join(line for t in toks for line in t.lines)


def region_tok(kind, body):
    lines = [f'<!-- begin generated: {kind} -->'] + (body.split('\n') if body else []) + [REGION_END.format(kind)]
    return Tok('region', lines, name=kind, code=body)


def is_python(t):
    return t.kind == 'fence' and t.name == '`' and t.info.split()[:1] == ['python']


def is_examples_line(line):
    return bool(re.match(r'\s*\*\*Examples?\*\*', line))


# ---------------------------------------------------------------- inline markers (values in prose)

INLINE = re.compile(r'<!--=(?P<body>.*?)-->(?P<ticks>`+)(?P<val>.+?)(?P=ticks)')
SPAN = re.compile(r'(`+)(.+?)\1')
ANY_COMMENT = re.compile(r'<!--(.*?)-->', re.S)


def inline_markers(md):
    """[(match, kind, expr)] for every value marker outside code fences: kind 'value' (expr = the code span
    before the marker, or the marker's own text) or 'error'."""
    out = []
    offset = 0
    for t in md_tokens(md):
        text = '\n'.join(t.lines)
        if t.kind == 'text':
            for m in INLINE.finditer(text):
                body = m.group('body')
                if body.strip() == 'error':
                    out.append((offset + m.start(), offset + m.end(), m, 'error', ''))
                    continue
                if body.strip():
                    expr = body.strip()
                else:
                    line_start = text.rfind('\n', 0, m.start()) + 1
                    spans = list(SPAN.finditer(text, line_start, m.start()))
                    expr = spans[-1].group(2).strip() if spans else None
                out.append((offset + m.start(), offset + m.end(), m, 'value', expr))
        offset += len(text) + 1
    return out


def format_span(value):
    """A value as a markdown code span."""
    ticks = '`' * (1 + max((len(x) for x in re.findall(r'`+', value)), default=0))
    pad = ' ' if value.startswith('`') or value.endswith('`') else ''
    return f'{ticks}{pad}{value}{pad}{ticks}'


def marker_problems(md):
    """Malformed markers (rule 10): unknown comment forms, inline markers at the start of a line or list item,
    block markers not alone on their line, value markers whose expression cannot be found, '?' left unfilled."""
    out = []
    fenced = strip_fences(md)
    for line in fenced.split('\n'):
        if re.match(r'^\s*(?:(?:[-*+]|\d+[.)])\s+)?<!--=', line):
            out.append(f'a value marker starts a line or list item (Colab then shows the line as raw HTML): {line[:70]!r}')
    for m in ANY_COMMENT.finditer(fenced):
        body, whole = m.group(1), m.group(0)
        end = fenced.find('\n', m.end())
        line = fenced[fenced.rfind('\n', 0, m.start()) + 1:end if end >= 0 else len(fenced)]
        if body.startswith('='):
            if not re.match(r'(`+).+?\1', fenced[m.end():]):
                out.append(f'value marker {whole!r} must be followed directly by a code span (`?`)')
            continue
        if REGION_BEGIN.match(whole) or re.fullmatch(r'<!-- end generated: [\w-]+ -->', whole) or BLOCK_MARKER.match(whole):
            if line.strip() != whole:
                out.append(f'block marker {whole!r} must be alone on its line')
            name = (REGION_BEGIN.match(whole) or re.match(r'<!-- end generated: ([\w-]+)', whole))
            if name and name.group(1) not in REGION_KINDS:
                out.append(f'unknown generated region kind in {whole!r}')
            continue
        out.append(f'unknown comment {whole[:60]!r} (allowed: the markers in yr/README.md)')
    for s, e, m, kind, expr in inline_markers(md):
        if kind == 'value' and not expr:
            out.append(f'value marker {m.group(0)[:40]!r} has no code span before it on its line (write `EXPR` is <!--=-->`?`)')
    return out


# ---------------------------------------------------------------- run cells

def title_for(number, part):
    if not part:
        return f'Output of Question {number}'
    return f'Output of Question {number}, part {part}' if number[-1].isalpha() else f'Output of Question {number}{part}'


def quote(code):
    """The code as a raw string literal, with its first line on a line of its own."""
    body = '\n' + code + '\n'
    for q in ('"""', "'''"):
        if q not in body:
            lit = f'r{q}{body}{q}'
            if ast.literal_eval(lit) != body:
                raise ValueError('code cannot be quoted as a raw string: ' + code[:60])
            return lit
    raise ValueError('code contains both """ and \'\'\', so it cannot be wrapped')


def render_run_cell(code, wrapped, number, part):
    head = f'# @title {title_for(number, part)}\n'
    if not wrapped:
        return head + code
    return (head + f"if 'run_code' in globals():\n    run_code({quote(code)})\n"
            f"else:\n    print({GUARD_MESSAGE!r})")


def parse_run_cell(src):
    """dict(title_line, title, code, wrapped) of a run cell (a code cell whose first line is a Colab title), or None."""
    first, _, rest = src.partition('\n')
    m = TITLE_LINE.match(first)
    if not m or 'Helper for the Answers' in first:
        return None
    title = re.sub(r'\{.*\}\s*$', '', m.group('rest')).strip()        # Colab may add { display-mode: ... }
    info = dict(title_line=first, title=title, code=rest, wrapped=False)
    tree = parses(rest)
    if tree and len(tree.body) == 1 and isinstance(tree.body[0], ast.If):
        node = tree.body[0]
        body = node.body[0] if len(node.body) == 1 else None
        if (ast.unparse(node.test) == "'run_code' in globals()" and isinstance(body, ast.Expr)
                and isinstance(body.value, ast.Call) and ast.unparse(body.value.func) == 'run_code'
                and len(body.value.args) == 1 and isinstance(body.value.args[0], ast.Constant)
                and isinstance(body.value.args[0].value, str)):
            info.update(code=body.value.args[0].value.removeprefix('\n').removesuffix('\n'), wrapped=True)
    return info


def run_cell_part(info, number):
    """The part letter a run cell's title names for a question numbered `number` (None: no part); False if the
    title names another question."""
    m = TITLE_TEXT.fullmatch(info['title'])
    if not m:
        return False
    num, part = m.group('num'), m.group('part')
    if part:
        return part if num == number else False
    if num == number:
        return None
    if num[:-1] == number and num[-1].isalpha():
        return num[-1]
    return False


def run_block_problems(code):
    out = []
    for m in BLOCK_HAZARD.finditer(code):
        out.append(f'line "{m.group(0).strip()}..." (Colab form markup, a cell magic or a ~~~ line) is not '
                   f'allowed in a run block')
    try:
        quote(code)
    except ValueError as e:
        out.append(str(e))
    return out


# ---------------------------------------------------------------- page structure

def is_helper_cell(c):
    return c['cell_type'] == 'code' and source(c).startswith(HELPER_TITLE)


def is_help_note(c):
    return c['cell_type'] == 'markdown' and source(c).startswith('**Using this page in Colab or Jupyter**')


def parse_page(nb):
    """The questions, in page order. Each is a dict:
    number, level, kind, title, start, end, heading,
    prompt_md [idx]   markdown cells before the Answer that are not run blocks
    run_blocks [(idx, part, code)]
    defs [idx]        definition cells (code cells before the Answer, not '# Your code here')
    placeholder idx | None, nosig (the placeholder is tagged no-signature)
    answer idx | None, answer_md [idx], run_cells [idx], run_part {idx: part or None or False},
    part_cells {part: idx}, other_code [idx] (code cells in the Answer that are not run cells)."""
    cells = nb['cells']
    questions, q = [], None
    for i, c in enumerate(cells):
        lev = heading_level(source(c)) if c['cell_type'] == 'markdown' else None
        if lev is not None and lev <= 3:
            if q:
                q['end'] = i
            q = None
            first = source(c).lstrip().split('\n')[0]
            m = QUESTION_LINE.match(first)
            if m:
                h = QUESTION_HEADING.match(first)
                q = dict(number=m.group('num'), level=h.group('level') if h else '', kind=h.group('kind') if h else '',
                         title=first.lstrip('# '), start=i, end=len(cells), heading=i, prompt_md=[], run_blocks=[],
                         defs=[], placeholder=None, nosig=False, answer=None, answer_md=[], run_cells=[],
                         run_part={}, part_cells={}, other_code=[])
                questions.append(q)
            continue
        if q is None:
            continue
        s = source(c)
        if c['cell_type'] == 'markdown' and s.strip() == ANSWER_HEADING:
            if q['answer'] is None:
                q['answer'] = i
            continue
        if q['answer'] is None:
            if c['cell_type'] == 'markdown':
                m = RUN_FENCE.match(s)
                if m:
                    q['run_blocks'].append((i, m.group('part'), m.group('code')))
                else:
                    q['prompt_md'].append(i)
            elif s.strip() == PLACEHOLDER:
                q['placeholder'] = i
                q['nosig'] = 'no-signature' in tags(c)
            else:
                q['defs'].append(i)
        else:
            if c['cell_type'] == 'code':
                info = parse_run_cell(s)
                if info:
                    q['run_cells'].append(i)
                    q['run_part'][i] = run_cell_part(info, q['number'])
                else:
                    q['other_code'].append(i)
            else:
                q['answer_md'].append(i)
                m = PART_CELL.match(s)
                if m:
                    q['part_cells'][m.group('part')] = i
    return questions


def multi(q):
    return len(q['run_blocks']) > 1


def run_cell_for(q, part):
    """Index of the run cell for a run block (by the part named in its title), or None."""
    want = part if multi(q) else None
    return next((i for i in q['run_cells'] if q['run_part'][i] == want), None)


def collapsed_sections_hidden(nb):
    """Indices of cells hidden when the notebook opens in Colab (collapsed headings in colab.collapsed_sections)."""
    ids = set(nb['metadata'].get('colab', {}).get('collapsed_sections', []))
    stack, hidden = [], set()
    for i, c in enumerate(nb['cells']):
        if c['cell_type'] == 'markdown':
            lev = heading_level(source(c))
            if lev:
                while stack and lev <= stack[-1]:
                    stack.pop()
                if stack:
                    hidden.add(i)
                if c.get('id') in ids:
                    stack.append(lev)
                continue
        if stack:
            hidden.add(i)
    return hidden


def answer_prose(nb, q):
    """{part: markdown of that part's explanation} ({None: all} for a single run block) plus 'summary': the
    markdown cells after the last run cell of a multi-part Answer."""
    cells = nb['cells']
    if not multi(q):
        return {None: '\n\n'.join(source(cells[i]) for i in q['answer_md']), 'summary': ''}
    out, cur = {'summary': ''}, None
    last_run = max(q['run_cells']) if q['run_cells'] else q['end']
    for i in q['answer_md']:
        m = PART_CELL.match(source(cells[i]))
        cur = m.group('part') if m else cur
        key = 'summary' if i > last_run else cur
        out[key] = out.get(key, '') + '\n\n' + source(cells[i])
    return out


# ---------------------------------------------------------------- outputs

TMP_PATH = re.compile(r'(?:[A-Za-z]:)?[/\\][^\s"\'\x1b]*?ipykernel_\d+[/\\]')
CELL_IN = re.compile(r'(Cell(?:\x1b\[[0-9;]*m)*\s?(?:\x1b\[[0-9;]*m)*In\[)\d+(\])')


def normalize_text(s):
    s = TMP_PATH.sub('/tmp/ipykernel_0/', s)
    return CELL_IN.sub(r'\g<1>1\2', s)


SVG_DRAWING = re.compile(r'\s*<svg width="(\d+)" height="(\d+)">.*</svg>\s*$', re.S)


def drawing_svg(o):
    html = text_of(o.get('data', {}).get('text/html'))
    return html if html and SVG_DRAWING.match(html) else None


def png_size(png):
    if len(png) < 24 or png[:8] != b'\x89PNG\r\n\x1a\n' or png[12:16] != b'IHDR':
        return None
    return struct.unpack('>II', png[16:24])


def svg_to_png(svg):
    import cairosvg
    svg = svg if 'xmlns=' in svg else svg.replace('<svg ', '<svg xmlns="http://www.w3.org/2000/svg" ', 1)
    return cairosvg.svg2png(bytestring=svg.encode(), scale=2)


def drawing_problems(o):
    meta = o.get('metadata', {})
    rd, size = meta.get('review_drawing', {}), meta.get('image/png', {})
    try:
        png = base64.b64decode(text_of(o['data']['image/png']), validate=True)
    except Exception:
        return ['the stored drawing is not valid base64']
    out = []
    if sha1(png) != rd.get('png_sha1'):
        out.append('the stored drawing PNG does not match its png_sha1 (edited by hand?)')
    wh = png_size(png)
    if wh is None:
        out.append('the stored drawing is not a PNG')
    elif wh != (2 * size.get('width', 0), 2 * size.get('height', 0)):
        out.append(f'the stored drawing PNG is {wh[0]}x{wh[1]}, not twice its display size')
    return out


def store_drawing(o, previous):
    """A jupyturtle drawing is stored as a PNG (shown everywhere before Run all), with the SHA-1 of its SVG and
    of the PNG; the PNG is re-rendered only when the SVG changed, so another machine's cairo does not rewrite it."""
    svg = drawing_svg(o)
    sha = sha1(svg)
    w, h = (int(x) for x in SVG_DRAWING.match(svg).groups())
    for p in previous:
        rd = p.get('metadata', {}).get('review_drawing', {})
        if rd.get('svg_sha1') == sha and p.get('metadata', {}).get('image/png') == {'width': w, 'height': h} \
                and not drawing_problems(p):
            return json.loads(json.dumps(p))
    png = svg_to_png(svg)
    return {'output_type': 'display_data',
            'data': {'image/png': base64.b64encode(png).decode(), 'text/plain': '<jupyturtle drawing>'},
            'metadata': {'image/png': {'width': w, 'height': h},
                         'review_drawing': {'svg_sha1': sha, 'png_sha1': sha1(png)}}}


def normalize_outputs(outputs, previous=()):
    """Stored outputs independent of the run: no execution counts, no kernel PID in traceback paths, stream
    outputs of the same name merged, drawings as PNG + hashes."""
    out = []
    prev_drawings = [p for p in previous if p.get('output_type') == 'display_data']
    for o in outputs:
        o = json.loads(json.dumps(o))
        o.pop('transient', None)
        if 'execution_count' in o:
            o['execution_count'] = None
        if o['output_type'] == 'stream':
            o['text'] = normalize_text(text_of(o['text']))
            if out and out[-1]['output_type'] == 'stream' and out[-1]['name'] == o['name']:
                out[-1]['text'] += o['text']
                continue
        elif o['output_type'] == 'error':
            o['evalue'] = normalize_text(o['evalue'])
            o['traceback'] = [normalize_text(t) for t in o['traceback']]
        elif drawing_svg(o):
            o = store_drawing(o, prev_drawings)
        out.append(o)
    return out


def stream_text(outputs, name):
    return ''.join(text_of(o['text']) for o in outputs if o['output_type'] == 'stream' and o['name'] == name)


def output_text(outputs):
    parts = []
    for o in outputs:
        if o['output_type'] == 'stream':
            parts.append(text_of(o['text']))
        elif o['output_type'] == 'error':
            parts.append('\n'.join(o['traceback']))
        elif 'text/plain' in o.get('data', {}) and 'review_drawing' not in o.get('metadata', {}):
            parts.append(text_of(o['data']['text/plain']))
    return ANSI.sub('', '\n'.join(parts))


def raised(outputs):
    """The exception names an output shows: error outputs, and (variant B) the last exception line of stderr."""
    names = [o['ename'] for o in outputs if o['output_type'] == 'error']
    err = ANSI.sub('', stream_text(outputs, 'stderr'))
    found = list(EXC_LINE.finditer(err))
    if found:
        names.append(found[-1].group('name'))
    return names


def needs_wrap(outputs):
    """A run cell is wrapped exactly when its code, run alone, raises or prints a line number."""
    return any(o['output_type'] == 'error' for o in outputs) or bool(LINE_REF.search(output_text(outputs)))


def output_problems(outputs):
    out, text = [], output_text(outputs)
    if len(text) > MAX_OUTPUT_CHARS or text.count('\n') + 1 > MAX_OUTPUT_LINES:
        out.append(f'the output is too long ({len(text)} characters, {text.count(chr(10)) + 1} lines; the limit is '
                   f'{MAX_OUTPUT_CHARS} / {MAX_OUTPUT_LINES})')
    m = MEM_ADDR.search(text)
    if m:
        out.append(f'the output contains a memory address ("{m.group(0).strip()}"), which changes on every run')
    return out


HASHED_FILE = re.compile(r'/tmp/ipykernel_0/\d+\.py')


def seen(outputs):
    """What a student reads, the same for a plain cell whose code raises (an error output) and for the wrapped
    cell (variant B: the traceback as stderr text): stdout, the traceback text with the cell's hashed file name
    masked, displayed data, drawings by SVG hash."""
    out = []
    for o in outputs:
        t = o['output_type']
        if t == 'stream':
            text = HASHED_FILE.sub('<cell>', ANSI.sub('', normalize_text(text_of(o['text']))))
            key = 'stdout' if o['name'] == 'stdout' else 'trace'
            if out and out[-1][0] == key:
                out[-1] = (key, out[-1][1] + text)
            else:
                out.append((key, text))
        elif t == 'error':
            text = HASHED_FILE.sub('<cell>', ANSI.sub('', normalize_text('\n'.join(o['traceback']))))
            out.append(('trace', text + '\n'))
        elif drawing_svg(o):
            out.append(('drawing', sha1(drawing_svg(o))))
        elif o.get('metadata', {}).get('review_drawing', {}).get('svg_sha1'):
            out.append(('drawing', o['metadata']['review_drawing']['svg_sha1']))
        else:
            out.append(('data', json.dumps({k: text_of(v) for k, v in o.get('data', {}).items()}, sort_keys=True)))
    return [(k, MEM_ADDR.sub(' at 0x?', v).strip('\n') if k == 'trace' else v) for k, v in out]


def canon_outputs(outputs):
    out = []
    for o in outputs:
        o = json.loads(json.dumps(o))
        if 'text' in o:
            o['text'] = text_of(o['text'])
        if 'data' in o:
            o['data'] = {k: text_of(v) for k, v in o['data'].items()}
        out.append(o)
    return json.dumps(out, sort_keys=True, ensure_ascii=False)


# ---------------------------------------------------------------- generated snippets (examples, fixes, values)

def turtle_img(svg, previous_imgs=()):
    """An <img data-turtle> tag with a PNG of the drawing; reuses a previous tag with the same SVG hash."""
    sha = sha1(svg)
    for tag in previous_imgs:
        if f'data-svg-sha1="{sha}"' in tag:
            return tag
    width = int(re.search(r'width="(\d+)"', svg).group(1))
    data = base64.b64encode(svg_to_png(svg)).decode()
    return f'<img data-turtle data-svg-sha1="{sha}" alt="Turtle drawing" width="{width}" src="data:image/png;base64,{data}">'


IMG_TAG = re.compile(r'<img\b[^>]*\bdata-turtle\b[^>]*>')


def snippet_markdown(result, previous_imgs=(), short_errors=True):
    """The markdown sync writes for a snippet's result (from the kernel): printed text and values as a ```text
    block, an error as its last line, drawings as pictures; '(nothing is displayed)' if there is nothing."""
    text, imgs = '', []
    for ev in result.get('events', []):
        kind = ev[0]
        if kind in ('stdout', 'stderr'):
            text += ev[1]
        elif kind == 'result':
            text += ev[1].get('text/plain', '') + '\n'
        elif kind == 'error':
            lines = ANSI.sub('', ev[2]).rstrip('\n').split('\n')
            text += (lines[-1] if short_errors else '\n'.join(lines)) + '\n'
        elif kind == 'drawing':
            imgs.append(turtle_img(ev[1], previous_imgs))
    parts = []
    if text.strip('\n'):
        parts.append(text_block(ANSI.sub('', text)))
    parts.extend(imgs)
    return '\n'.join(parts) if parts else '(nothing is displayed)'


def text_block(text):
    ticks = '`' * max(3, 1 + max((len(m) for m in re.findall(r'`+', text)), default=0))
    return f'{ticks}text\n{text.rstrip(chr(10))}\n{ticks}'


# ---------------------------------------------------------------- sync stamp

def code_sha1(nb):
    return sha1(json.dumps([source(c) for c in nb['cells'] if c['cell_type'] == 'code']))


def outputs_sha1(nb):
    return sha1(json.dumps([canon_outputs(c.get('outputs', [])) for c in nb['cells'] if c['cell_type'] == 'code']))


def generated_parts(nb):
    """Every generated region's body and filled value, in page order (what sync writes into markdown)."""
    out = []
    for c in nb['cells']:
        if c['cell_type'] != 'markdown':
            continue
        md = source(c)
        for t in md_tokens(md):
            if t.kind == 'region':
                out.append(t.code)
        for s, e, m, kind, expr in inline_markers(md):
            out.append(m.group('val'))
        toks = md_tokens(md)
        for k, t in enumerate(toks):
            if t.kind == 'marker' and t.name == 'generated imports' and k + 1 < len(toks):
                n = int(t.arg or 0)
                out.append('\n'.join(toks[k + 1].code.split('\n')[:n]))
    return out


def generated_sha1(nb):
    return sha1(json.dumps(generated_parts(nb), ensure_ascii=False))


def make_stamp(nb, stack):
    return {'code_sha1': code_sha1(nb), 'outputs_sha1': outputs_sha1(nb), 'generated_sha1': generated_sha1(nb),
            'stack': stack}


def stack_pinned(stack):
    return bool(stack) and stack.get('python', '').rsplit('.', 1)[0] == PINNED_STACK['python'] and all(
        stack.get(k) == v for k, v in PINNED_STACK.items() if k != 'python')


def stamp_problems(nb):
    st = nb['metadata'].get(STAMP_KEY)
    if not st or 'code_sha1' not in st:
        return ['the page was never synced (no metadata.yr_review): run review.sh sync']
    out = []
    if st.get('code_sha1') != code_sha1(nb):
        out.append('code changed since the last sync (a run block, definition cell or setup cell): run review.sh sync')
    if st.get('outputs_sha1') != outputs_sha1(nb):
        out.append('stored outputs differ from what the last sync wrote (edited by hand, or by Colab): run review.sh sync')
    if st.get('generated_sha1') != generated_sha1(nb):
        out.append('generated text (a region, an import line or a value) differs from what the last sync wrote: '
                   'it was edited by hand; run review.sh sync and read its diff')
    if not stack_pinned(st.get('stack')):
        out.append(f'stored outputs were written on {st.get("stack")}, not the pinned Colab-like stack {PINNED_STACK}')
    return out


# ---------------------------------------------------------------- the website (used by jb/prep_notebooks.py)

def strip_markers(md):
    """Markdown for the website: block markers and region delimiters removed (their lines too), value markers
    removed (the values stay)."""
    md = re.sub(r'<!--=.*?-->', '', md)
    out = []
    for line in md.split('\n'):
        if REGION_BEGIN.match(line) or re.fullmatch(r'<!-- end generated: [\w-]+ -->', line) or BLOCK_MARKER.match(line):
            continue
        out.append(line)
    return '\n'.join(out)


def site_traceback(text):
    """A traceback (ANSI removed) for the website: without IPython's banner, file paths and '<cell line: 0>'; a
    syntax error keeps only its code line, caret and message."""
    out = []
    for line in text.split('\n'):
        if re.fullmatch(r'-{20,}', line) or re.fullmatch(r'\w+\s{2,}Traceback \(most recent call last\)', line):
            continue
        if re.fullmatch(r'\s*File "[^"]*", line \d+', line) or re.fullmatch(r'\s*Cell In\[\d+\], line \d+', line):
            continue
        m = re.fullmatch(r'(?P<path>\S+\.py) in (?P<func>.+)', line) or \
            re.fullmatch(r'Cell In\[\d+\], line \d+(?:, in (?P<func>.+))?', line)
        if m:
            func, path = m.group('func'), m.groupdict().get('path') or ''
            in_cell = not path or 'ipykernel_' in path
            if in_cell and (not func or func.startswith('<cell line') or func.startswith('<module>')):
                continue
            prefix = '' if in_cell else re.split(r'[/\\]', path)[-1] + ', '
            out.append(f'In {func}:' if not prefix else f'{prefix}in {func}:')
            continue
        out.append(line)
    return re.sub(r'\n{3,}', '\n\n', '\n'.join(out).strip('\n'))


def raw_html(html):
    return '<div class="review-output">\n' + re.sub(r'\n\s*\n', '\n', html.strip()) + '\n</div>'


def render_outputs(outputs):
    """A run cell's stored outputs as markdown for the website."""
    parts = []
    for o in outputs:
        t = o['output_type']
        if t == 'stream':
            text = ANSI.sub('', text_of(o['text']))
            if o['name'] == 'stderr':
                text = site_traceback(text) + '\n'
            if parts and isinstance(parts[-1], list):
                parts[-1][1] += text
            else:
                parts.append(['text', text])
            continue
        if t == 'error':
            parts.append(text_block(site_traceback(ANSI.sub('', '\n'.join(o['traceback'])))))
            continue
        data = {k: text_of(v) for k, v in o.get('data', {}).items()}
        if 'image/png' in data:
            size = o.get('metadata', {}).get('image/png', {})
            attrs = ''.join(f' {k}="{size[k]}"' for k in ('width', 'height') if k in size)
            alt = 'Turtle drawing' if 'review_drawing' in o.get('metadata', {}) else 'output'
            parts.append(raw_html(f'<img alt="{alt}"{attrs} src="data:image/png;base64,{data["image/png"].strip()}">'))
        elif 'text/html' in data:
            parts.append(raw_html(data['text/html']))
        elif 'text/markdown' in data:
            parts.append(data['text/markdown'])
        elif 'text/plain' in data:
            parts.append(text_block(data['text/plain']))
    return '\n\n'.join(text_block(p[1]) if isinstance(p, list) else p for p in parts)
