"""Prototype of a mechanical check: find "`EXPR` is `VALUE`"-style claims in the
markdown of the review pages and evaluate them, with no hand curation.

For each claim: evaluate in a namespace with the page's setup imports; if a name
is missing, retry in a namespace where the question's own code cells have run.
Usage: python auto_extract.py ../../../yrThinkPython/yr/chap0*_review.ipynb
"""
import ast, contextlib, io, json, re, sys, types
from collections import Counter

CODE = r'`([^`]+)`'
PATTERNS = [
    ('error',   re.compile(CODE + r'(?:,? and ' + CODE + r')? (?:is|are each|are) a `(\w+(?:Error|Exception))`')),
    ('display', re.compile(CODE + r' displays `([^`]*)`')),
    ('value',   re.compile(CODE + r' (?:is still|is|returns|which is) `([^`]+)`')),
    ('truth',   re.compile(CODE + r' is (true|false)\b')),
]
SKIP_UPPER = re.compile(r'\b[A-Z][A-Z_]{2,}\b')   # placeholders like EXPR, STRING1


def stub_turtle(ns):
    m = types.ModuleType('jupyturtle')
    for name in ['make_turtle', 'forward', 'left', 'right', 'penup', 'pendown']:
        setattr(m, name, lambda *a, **k: None)
    sys.modules['jupyturtle'] = m


def setup_ns(setup_src):
    ns = {'__name__': '__main__'}
    stub_turtle(ns)
    src = setup_src.replace("download('", "('")       # no network
    with contextlib.redirect_stdout(io.StringIO()):
        exec(src, ns)
    return ns


def try_eval(kind, groups, ns):
    out = io.StringIO()
    if kind == 'value':
        expr, val = groups
        with contextlib.redirect_stdout(out):
            got = eval(expr, ns)
        try:
            want = eval(val, ns)
        except Exception:
            return str(got) == val, repr(got)          # e.g. `type(True)` is `bool`
        return repr(got) == repr(want) or got is want, repr(got)
    if kind == 'truth':
        expr, tv = groups
        with contextlib.redirect_stdout(out):
            got = bool(eval(expr, ns))
        return got == (tv == 'true'), str(got)
    if kind == 'display':
        code, shown = groups
        with contextlib.redirect_stdout(out):
            exec(compile(code, '<c>', 'exec'), ns)
        return out.getvalue().rstrip('\n') == shown, repr(out.getvalue())
    if kind == 'error':
        *codes, err = groups
        res = []
        for code in [c for c in codes if c]:
            try:
                with contextlib.redirect_stdout(out):
                    exec(compile(code, '<c>', 'exec'), ns)
                res.append('no error')
            except BaseException as e:
                res.append(type(e).__name__)
        return all(r == err for r in res), ','.join(res)


def main(paths):
    tally = Counter()
    rows = []
    for path in paths:
        nb = json.load(open(path))
        cells = nb['cells']
        setup = next(''.join(c['source']) for c in cells if 'setup' in c.get('metadata', {}).get('tags', []))
        q_code = []                     # code cells of the current question
        section = 'Concepts'
        for c in cells:
            src = ''.join(c['source'])
            if c['cell_type'] == 'code':
                if 'setup' not in c.get('metadata', {}).get('tags', []):
                    q_code.append(src)
                continue
            if src.startswith('### Question'):
                section, q_code = src.splitlines()[0][4:], []
            if '<summary>Answer' not in src and not src.startswith('<details open'):
                if not src.startswith('### Question'):
                    continue                                   # only Concepts and Answers (+ question prose)
            prose = re.sub(r'```.*?```', '', src, flags=re.S)  # drop code/output blocks
            for line in prose.splitlines():
                for kind, pat in PATTERNS:
                    for m in pat.finditer(line):
                        groups = m.groups()
                        if any(g and SKIP_UPPER.search(g) for g in groups[:1]):
                            tally['placeholder'] += 1
                            continue
                        status, got = None, ''
                        for ctx in ('setup', 'question'):
                            ns = setup_ns(setup)
                            if ctx == 'question':
                                for qc in q_code:
                                    try:
                                        with contextlib.redirect_stdout(io.StringIO()):
                                            exec(qc, ns)
                                    except BaseException:
                                        pass
                            try:
                                ok, got = try_eval(kind, groups, ns)
                                status = ('OK' if ok else 'WRONG') + '/' + ctx
                                break
                            except NameError as e:
                                status, got = 'NAME?', str(e)
                            except BaseException as e:
                                status, got = 'CANT', f'{type(e).__name__}: {e}'
                                break
                        tally[status.split('/')[0]] += 1
                        rows.append((status, path.split('/')[-1][:6], section, m.group(0), got))
    for r in rows:
        if not r[0].startswith('OK'):
            print(' | '.join(r))
    print(tally, 'matched:', len(rows))
    print('by context:', Counter(r[0] for r in rows))


if __name__ == '__main__':
    main(sys.argv[1:])
