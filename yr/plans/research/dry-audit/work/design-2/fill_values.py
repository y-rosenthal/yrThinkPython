"""Prototype: values in prose are generated, never typed.
Two forms:
  1. `EXPR` is `VALUE`          -> the visible EXPR is evaluated; VALUE is rewritten (fill) or compared (check)
  2. <!--= EXPR -->`VALUE`      -> EXPR is not shown; VALUE is rewritten/compared (for free-form sentences)
'context' is the namespace of the question (its definition cells and %%question code)."""
import re, sys
FORM1 = re.compile(r"`([^`\n]+)` is `([^`\n]*)`")
FORM2 = re.compile(r"<!--=\s*(.+?)\s*-->`([^`\n]*)`")

def value(expr, ns):
    try:
        return repr(eval(expr, ns))
    except Exception as e:
        return None

def process(text, ns, fill):
    problems = []
    def sub(m, visible):
        expr, typed = m.group(1), m.group(2)
        got = value(expr, ns)
        if got is None:
            return m.group(0)           # not an expression (prose list, placeholder): skip
        if got != typed and not fill:
            problems.append(f"{expr!r}: typed {typed!r}, real {got!r}")
        return (f"`{expr}` is `{got}`" if visible else f"<!--= {expr} -->`{got}`")
    text = FORM1.sub(lambda m: sub(m, True), text)
    text = FORM2.sub(lambda m: sub(m, False), text)
    return text, problems

if __name__ == "__main__":
    import sys as _s
    ns = {"n": 17, "sys": _s}
    md = ("After `n = 17`, `n + 25` is `?` and `105 // 60` is `1`. `-7 // 2` is `-3`.\n"
          "The recursion goes on until Python's limit (about <!--= sys.getrecursionlimit() -->`3000` frames) is exceeded.")
    print(process(md, ns, fill=False)[1])
    print(process(md, ns, fill=True)[0])
