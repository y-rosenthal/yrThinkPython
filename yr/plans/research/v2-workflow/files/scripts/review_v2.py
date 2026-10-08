"""Prototype v2 of the review-page format (one place that defines it; stdlib only).

Layout of a question (cells top to bottom):
  [md]   ### Question N (level): kind ... prompt
  [md]   **Part a**\n\n```python run\n<code>\n```         (one run block per markdown cell; the label only
                                                          when the question has 2 or more run blocks)
  [code] definition cells / '# Your code here' (unchanged)
  [md]   #### Answer                                      (saved collapsed: Colab + JupyterLab)
  [md]   **Part a:** explanation ...                      (multi-part) or the explanation (single part)
  [code] # @title Output of part a { display-mode: "form" }      <- RUN CELL: generated from the run
         run_code(r\"\"\"\n<code>\n\"\"\")                         block, code hidden, OUTPUT STORED
  [md]   ... more explanation, Part b ..., summary cells

A run cell's code is hidden (Colab form view + JupyterLab source_hidden). Its outputs are stored in
the notebook by sync_v2.py, so an Answer shows the real output once, even before Run all.
"""
import ast
import hashlib
import json
import re

ANSWER_HEADING = '#### Answer'
PLACEHOLDER = '# Your code here'
CREDITS_HEADING = '## Credits'
RUN_FENCE = re.compile(r'^(?:\*\*Part (?P<part>[a-z])\*\*\s*\n\n)?```python run\n(?P<code>.*?)\n```\s*$', re.S)
PART_CELL = re.compile(r'^\*\*Part (?P<part>[a-z]):\*\*')
TITLE_LINE = re.compile(r'^# @title (?P<title>.*?) \{ display-mode: "form" \}$')
ERROR_NAME = re.compile(r'\b([A-Z][A-Za-z]*(?:Error|Exception|Warning|Interrupt|Exit))\b')
ANSI = re.compile(r'\x1b\[[0-9;]*[A-Za-z]')
RUN_CELL_METADATA = {'cellView': 'form', 'jupyter': {'source_hidden': True}}

RUN_CODE_CELL = '''def run_code(code):
    """Run code (a string) as if it were a cell of its own.

    Some Answers use it for code whose result is an error: the error is shown as
    usual, but it does not stop Runtime > Run all.
    """
    code = code.removeprefix('\\n')   # the code starts on the line after run_code(r"""
    try:
        from IPython import get_ipython
        ip = get_ipython()
    except ImportError:
        ip = None
    if ip is None:                    # plain Python (the review tools): just run it
        exec(code, globals())
        return
    result = ip.run_cell(code, store_history=False)
    if isinstance(result.error_in_exec, KeyboardInterrupt):
        raise KeyboardInterrupt       # the Stop button still stops Run all'''

HELP_CELL = '''**Using this page in Colab or Jupyter**

- Each question's **Answer** is closed: click the arrow next to **Answer** to open it. It explains the answer and shows the output of the question's code. That output is saved with the page, so it is there even before you run anything. The code that produced it is hidden (click **Show code** in Colab, or the three dots in Jupyter, to see it).
- To run code yourself, first run the setup cells. **Runtime → Run all** (Jupyter: **Run → Run All Cells**) does that, and re-runs the code in every Answer. The Answers stay closed, and Run all does not stop at the errors that are answers. If Colab warns that the notebook was not authored by Google, choose **Run anyway**.
- Run your own code with **Ctrl+Enter**.
- After Run all, an Answer shows the output from your session. If your own code changed a name that a question uses, that output can differ from the saved one.
- VS Code, GitHub's preview and nbviewer show the Answers open.'''


def source(cell):
    s = cell['source']
    return ''.join(s) if isinstance(s, list) else s


def stable_id(*parts):
    """A new cell id derived from its context, so the converter is deterministic."""
    return hashlib.sha1(':'.join(parts).encode()).hexdigest()[:8]


def heading_level(md):
    """Smallest heading level in a markdown cell (ATX, setext or HTML <hN>), outside code fences; or None."""
    lines, fence, best = md.split('\n'), False, None
    for k, line in enumerate(lines):
        if line.lstrip().startswith(('```', '~~~')):
            fence = not fence
            continue
        if fence:
            continue
        m = re.match(r'\s{0,3}(#{1,6})(\s|$)', line)
        lev = len(m.group(1)) if m else None
        if lev is None and k > 0 and lines[k - 1].strip() and re.match(r'\s{0,3}(=+|-+)\s*$', line):
            lev = 1 if '=' in line else 2
        if lev is None:
            h = re.search(r'<h([1-6])\b', line, re.I)
            lev = int(h.group(1)) if h else None
        if lev and (best is None or lev < best):
            best = lev
    return best


def strip_fences(md):
    """Markdown without fenced code blocks (for prose rules)."""
    return re.sub(r'^(```|~~~).*?^\1[ \t]*$', '', md, flags=re.S | re.M)


def error_names(md):
    return set(ERROR_NAME.findall(strip_fences(md)))


# ---------------------------------------------------------------- run cells

def title_for(part):
    return f'Output of part {part}' if part else 'Output'


def quote(code):
    body = '\n' + code + '\n'
    if re.search(r'^\s*>>>', code, re.M):
        raise ValueError('code for run_code may not contain ">>>" lines (IPython 8+ strips them)')
    for q in ('"""', "'''"):
        if q not in body:
            lit = f'r{q}{body}{q}'
            if ast.literal_eval(lit) != body:
                raise ValueError('code cannot be quoted as a raw string: ' + code[:60])
            return lit
    raise ValueError('code contains both """ and \'\'\'')


def render_run_cell(code, wrapped, part):
    head = f'# @title {title_for(part)} {{ display-mode: "form" }}\n'
    return head + (f'run_code({quote(code)})' if wrapped else code)


def parse_run_cell(src):
    """(title, code, wrapped) of a run cell, or None if src is not a run cell."""
    first, _, rest = src.partition('\n')
    m = TITLE_LINE.match(first)
    if not m:
        return None
    try:
        tree = ast.parse(rest)
    except SyntaxError:
        return m.group('title'), rest, False
    if (len(tree.body) == 1 and isinstance(tree.body[0], ast.Expr) and isinstance(tree.body[0].value, ast.Call)
            and isinstance(tree.body[0].value.func, ast.Name) and tree.body[0].value.func.id == 'run_code'
            and len(tree.body[0].value.args) == 1 and isinstance(tree.body[0].value.args[0], ast.Constant)
            and isinstance(tree.body[0].value.args[0].value, str)):
        code = tree.body[0].value.args[0].value.removeprefix('\n')
        return m.group('title'), code.removesuffix('\n'), True
    return m.group('title'), rest, False


def is_run_cell(cell):
    return cell['cell_type'] == 'code' and parse_run_cell(source(cell)) is not None


# ---------------------------------------------------------------- page structure

def parse_page(nb):
    """Questions with their cells. Each question: dict(title, start, end, run_blocks=[(idx, part, code)],
    answer=idx or None, answer_end, run_cells=[idx], part_cells={part: idx}, other_code=[idx])."""
    cells = nb['cells']
    questions, q = [], None
    for i, c in enumerate(cells):
        lev = heading_level(source(c)) if c['cell_type'] == 'markdown' else None
        if lev is not None and lev <= 3:
            if q:
                q['end'] = i
            q = None
            if source(c).lstrip().startswith('### Question'):
                q = dict(title=source(c).lstrip('# ').split('\n')[0], start=i, end=len(cells), run_blocks=[],
                         answer=None, run_cells=[], part_cells={}, other_code=[], answer_md=[])
                questions.append(q)
            continue
        if q is None:
            continue
        s = source(c)
        if c['cell_type'] == 'markdown' and s.strip() == ANSWER_HEADING:
            q['answer'] = i
            continue
        if q['answer'] is None:
            m = RUN_FENCE.match(s) if c['cell_type'] == 'markdown' else None
            if m:
                q['run_blocks'].append((i, m.group('part'), m.group('code')))
            elif c['cell_type'] == 'code':
                q['other_code'].append(i)
        else:
            if c['cell_type'] == 'code':
                (q['run_cells'] if is_run_cell(c) else q['other_code']).append(i)
            else:
                q['answer_md'].append(i)
                m = PART_CELL.match(s)
                if m:
                    q['part_cells'][m.group('part')] = i
    return questions


def answer_heading_cells(nb):
    return [c for c in nb['cells'] if c['cell_type'] == 'markdown' and source(c).strip() == ANSWER_HEADING]


def collapsed_sections_hidden(nb):
    """Index set of cells hidden when the notebook opens (collapsed headings, JupyterLab/Colab rule)."""
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
                collapsed = c['metadata'].get('jp-MarkdownHeadingCollapsed') or c.get('id') in ids
                if collapsed:
                    stack.append(lev)
                continue
        if stack:
            hidden.add(i)
    return hidden


# ---------------------------------------------------------------- outputs

TMP_PATH = re.compile(r'/tmp/ipykernel_\d+/')
CELL_IN = re.compile(r'Cell In\[\d+\]')


def normalize_text(s):
    s = TMP_PATH.sub('/tmp/ipykernel_0/', s)
    return CELL_IN.sub('Cell In[1]', s)


def normalize_outputs(outputs):
    """Make stored outputs independent of the run: no execution counts, no kernel PID in traceback
    paths, IPython 8+ 'Cell In[N]' headers numbered 1. Text is stored as one string per output."""
    out = []
    for o in outputs:
        o = json.loads(json.dumps(o))
        if 'execution_count' in o:
            o['execution_count'] = None
        if o['output_type'] == 'stream':
            o['text'] = normalize_text(''.join(o['text']) if isinstance(o['text'], list) else o['text'])
        elif o['output_type'] == 'error':
            o['evalue'] = normalize_text(o['evalue'])
            o['traceback'] = [normalize_text(t) for t in o['traceback']]
        o.pop('transient', None)
        out.append(o)
    return out


def plain_traceback(o):
    return ANSI.sub('', '\n'.join(o['traceback'])).rstrip('\n')


def semantic(outputs):
    """What a student sees, independent of the IPython version: stdout/stderr text, error kind and
    message (without SyntaxError's '(file, line N)'), displayed data."""
    sem = []
    for o in outputs:
        t = o['output_type']
        if t == 'stream':
            text = ANSI.sub('', normalize_text(o['text'] if isinstance(o['text'], str) else ''.join(o['text'])))
            if sem and sem[-1][0] == 'stream:' + o['name']:
                sem[-1] = (sem[-1][0], sem[-1][1] + text)
            else:
                sem.append(('stream:' + o['name'], text))
        elif t == 'error':
            sem.append(('error', o['ename'], re.sub(r' \([^()]*, line \d+\)$', '', ANSI.sub('', o['evalue']))))
        else:
            data = {k: (''.join(v) if isinstance(v, list) else v) for k, v in o.get('data', {}).items()}
            sem.append(('data', json.dumps(data, sort_keys=True)))
    return sem
