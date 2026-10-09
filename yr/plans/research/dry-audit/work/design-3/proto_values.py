"""Design-3 feasibility prototype: values in prose that sync fills by running code.

Markup (invisible when rendered; the author types the expression once and never the value):
    `EXPR` is <!--=-->`?`            value  = repr(eval(EXPR))         -> `EXPR` is <!--=-->`42`
    `CODE` displays <!--=print-->`?`   value  = stdout of exec(CODE)     (one line, stripped)
    `CODE` is a <!--=error-->`?`       value  = type of the exception    -> <!--=error-->`SyntaxError`
    after <!--do-->`n = 17`, ...       run CODE silently first (context typed once, visible)
The expression is the nearest code span before the marker in the same paragraph.
Context: the question's namespace (setup + definition cells + its run blocks), then the
paragraph's <!--do--> spans in order. sync fills; check fails when a filled value is stale.
"""
import contextlib, io, re, sys

SPAN = r'`([^`]+)`'
TOKEN = re.compile(r'<!--(=|=print|=error|do)-->`([^`]*)`|' + SPAN)


def _exec(code, ns):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        exec(compile(code, '<prose>', 'exec'), ns)
    return buf.getvalue()


def fill(md, base_ns):
    out = []
    for para in re.split(r'(\n\s*\n)', md):
        ns = dict(base_ns)
        last, pieces, pos = None, [], 0
        for m in TOKEN.finditer(para):
            pieces.append(para[pos:m.start()])
            pos = m.end()
            kind, val, plain = m.group(1), m.group(2), m.group(3)
            if plain is not None:                       # an ordinary code span: candidate expression
                last = plain
                pieces.append(m.group(0))
                continue
            if kind == 'do':
                _exec(val, ns)
                last = val
                pieces.append(m.group(0))
                continue
            if last is None:
                raise ValueError(f'marker with no expression before it: {para[:60]!r}')
            if kind == '=':
                new = repr(eval(last, ns))
            elif kind == '=print':
                new = _exec(last, dict(ns)).strip()
            else:
                try:
                    compile(last, '<prose>', 'exec')
                    _exec(last, dict(ns))
                    new = 'NO ERROR'
                except BaseException as e:            # SyntaxError comes from compile
                    new = type(e).__name__
            pieces.append(f'<!--{kind}-->`{new}`')
        pieces.append(para[pos:])
        out.append(''.join(pieces))
    return ''.join(out)


def render(md):
    """What a reader sees (comments removed)."""
    return re.sub(r'<!--[^>]*-->', '', md)


SAMPLES = [  # (namespace code, authored prose) taken from today's pages, with markers added
    ('', "After <!--do-->`n = 17`, `n + 25` is <!--=-->`?` and `print(n)` displays <!--=print-->`?`."),
    ('import math', "`math.sqrt(25)` is <!--=-->`?`, `math.pow(5, 2)` is <!--=-->`?` and `5 ** 2` is <!--=-->`?`."),
    ('', "`105 // 60` is <!--=-->`?`, `-7 // 2` is <!--=-->`?` and `105 % 60` is <!--=-->`?`."),
    ('', "`17 = n` is a <!--=error-->`?`; `import maath` is a <!--=error-->`?`."),
    ('import math', "`math.pow(2)` is a <!--=error-->`?` and `range(4.5)` is a <!--=error-->`?`."),
    ('', "`'  hi \\n'.strip()` is <!--=-->`?` and `'Gadsby'.lower()` is <!--=-->`?`."),
    ('', "`'-' * 5` is <!--=-->`?`, and `int('101', 2)` is <!--=-->`?`."),
    ('', "`print('The answer is', 42)` displays <!--=print-->`?`."),
    ('def double(x):\n    return x * 2', "`double(5)` is <!--=-->`?`, and `double(5) + 1` is <!--=-->`?`."),
    ('', "`22 + 5` is <!--=-->`?`, which is 3 more than 24, so the event ends at <!--=-->`?`."),
    ('import sys', "Python's limit on the number of frames (`sys.getrecursionlimit()`, <!--=-->`?` here) is exceeded."),
]


def main():
    ok = True
    for ns_code, md in SAMPLES:
        ns = {'__name__': '__main__'}
        exec(ns_code, ns)
        try:
            filled = fill(md, ns)
        except Exception as e:
            print('FAIL', md[:50], e); ok = False; continue
        again = fill(filled, ns)
        idem = again == filled
        ok &= idem
        print('SEEN :', render(filled))
        print('     idempotent:', idem)
    # staleness: a hand edit to a filled value is detected
    md = fill("`3 % 7` is <!--=-->`?`.", {})
    tampered = md.replace('`3`', '`7`')
    print('stale detected:', fill(tampered, {}) != tampered)
    # the 'is 3 more than 24, so ... ends at' sample shows a LIMIT: the second marker evaluates the
    # nearest span (`22 + 5`) again; the author must give it its own expression, e.g. `(22 + 5) % 24`.
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
