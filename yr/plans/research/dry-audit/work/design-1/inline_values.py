"""Prototype (design-1): inline generated values in markdown prose.

The author writes the expression once and a placeholder value followed by a
marker comment; sync replaces the value with the real one:

    `n + 25` is `?`<!--=-->            -> `n + 25` is `42`<!--=-->
    `17 = n` is a `?`<!--=error-->     -> ... `SyntaxError`<!--=error-->
    `print(n)` displays `?`<!--=out--> -> ... `17`<!--=out-->
    only ?<!--=s count--> words        -> only 10<!--=s count--> words

The expression is the comment's text if given, else the nearest code span
before the value in the same sentence.  Context: the page setup, then the
question's code (passed in), then every assignment code span earlier in the
same paragraph ("after `n = 17`, ...").  Running sync twice changes nothing."""
import ast, contextlib, io, re, sys

MARK = re.compile(r'(`[^`\n]*`|[^\s`<>]+)<!--=(\w*)\s*(.*?)-->')
SPAN = re.compile(r'`([^`\n]+)`')

def run(code, ns):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        exec(compile(code, '<claim>', 'exec'), ns)
    return buf.getvalue()

def value(expr, mode, ns):
    ns = dict(ns)
    try:
        if mode == 'out':
            return run(expr, ns).rstrip('\n')
        if mode == 'error':
            run(expr, ns)
            return 'NO ERROR'          # check fails: the claim says it raises
        v = eval(compile(expr, '<claim>', 'eval'), ns)
        return str(v) if mode == 's' else repr(v)
    except Exception as e:
        if mode == 'error':
            return type(e).__name__
        raise

def fill_paragraph(par, base_ns):
    out, pos, ctx = [], 0, dict(base_ns)
    for m in MARK.finditer(par):
        before = par[pos:m.start()]
        # context: assignments in code spans earlier in this paragraph
        for span in SPAN.findall(par[:m.start()]):
            try:
                t = ast.parse(span)
                if all(isinstance(n, (ast.Assign, ast.AugAssign, ast.Import, ast.ImportFrom))
                       for n in t.body):
                    run(span, ctx)
            except Exception:
                pass
        token, mode, expr = m.groups()
        if not expr:   # the nearest code span before the value token, same sentence
            sentence = re.split(r'(?<=[.;:])\s', before)[-1]
            spans = SPAN.findall(sentence)
            expr = spans[-1]
        v = value(expr, mode, ctx)
        new = f'`{v}`' if token.startswith('`') else v
        out.append(before + new + f'<!--={mode}{" " + m.group(3) if m.group(3) else ""}-->')
        pos = m.end()
    return ''.join(out) + par[pos:]

def fill(md, base_ns):
    # a paragraph, or one bullet of a list, is a context unit
    return '\n'.join(fill_paragraph(p, base_ns) for p in re.split(r'\n(?=- |\n)', md)) if False else \
        re.sub(r'(?ms)^(- .*?)(?=^- |\Z)', lambda m: fill_paragraph(m.group(1), base_ns), md)

if __name__ == '__main__':
    setup = 'import math\nimport sys\n'
    ns = {}; run(setup, ns)
    words = '/home/yitz/Dropbox/_yrQuarto-master/yrThinkPython-work/dry/chap07-audit/words.txt'
    ns['WORDS'] = words
    sample = r'''- After `n = 17`, `n + 25` is `?`<!--=--> and `print(n)` displays `?`<!--=out-->.
- `math.pi` is `?`<!--=-->. `math.sqrt(25)` is `?`<!--=--> and `math.pow(5, 2)` is `?`<!--=-->, but `5 ** 2` is `?`<!--=-->.
- `int('101', 2)` is `?`<!--=-->. `round(3.14159, 3)` is `?`<!--=-->.
- `17 = n` is a `?`<!--=error-->. `import maath` is a `?`<!--=error-->. `math.pow(2)` is a `?`<!--=error-->.
- `-7 // 2` is `?`<!--=-->, and `105 % 60` is `?`<!--=-->.
- Python's limit on the number of frames is about ?<!--=s sys.getrecursionlimit()-->; going past it is a `RecursionError`.
- Only ?<!--=s sum(1 for w in open(WORDS) if 'q' in w and 'u' not in w)--> words contain a `q` but no `u`.
- `'Gadsby'.lower()` is `'old value'`<!--=-->.'''
    once = fill(sample, ns)
    twice = fill(once, ns)
    print(once)
    print('idempotent:', once == twice)
