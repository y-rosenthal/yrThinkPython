#!/usr/bin/env bash
# Execute chapter notebooks top to bottom in a scratch directory and report errors.
# Usage: run_notebooks.sh chapters/chap03.ipynb [chapters/chap04.ipynb ...]   or   run_notebooks.sh all
#
# Cells are run with errors allowed, then the executed copy is inspected:
#   - an error in a cell BEFORE the "## Exercises" heading fails the notebook (real bug);
#   - errors AFTER it are reported but expected, because exercise cells depend on
#     "# Solution goes here" cells that are intentionally empty.
#   - a "%%expect SomeError" cell that raises exactly SomeError is a pass (the magic re-raises
#     the traceback as an error output under nbconvert);
#   - input() is replaced by a stub returning a non-numeric string (IPython startup file), so
#     the chapter 5 input() cells and the "%%expect ValueError / int(speed)" cell behave as in the book.
# download() cells fetch files from upstream GitHub into the scratch dir, never into the repo.
set -euo pipefail
ROOT="$(git -C "$(dirname "$0")" rev-parse --show-toplevel)"
cd "$ROOT"
source "$ROOT/.claude/skills/build-book/ensure_venv.sh"

if [ $# -eq 0 ]; then echo "usage: $0 <notebook.ipynb ...|all>" >&2; exit 2; fi
if [ "$1" = "all" ]; then set -- chapters/chap[01][0-9].ipynb; fi

WORK="${THINKPYTHON_RUN_DIR:-${TMPDIR:-/tmp}/yrThinkPython-run}"
mkdir -p "$WORK"
cp thinkpython.py diagram.py structshape.py words.txt photos.zip "$WORK"/ 2>/dev/null || true
if [ -f Turtle.py ]; then cp Turtle.py "$WORK"/; fi
export IPYTHONDIR="$WORK/ipython"
mkdir -p "$IPYTHONDIR/profile_default/startup"
cat > "$IPYTHONDIR/profile_default/startup/00-fake-input.py" <<'PY'
# ipykernel re-binds builtins.input to Kernel.raw_input before every cell, so patch the
# kernel method itself rather than builtins.
from ipykernel.kernelbase import Kernel
def _fake_raw_input(self, prompt=""):
    print(prompt, end="")
    return "an African or a European swallow?"
Kernel.raw_input = _fake_raw_input
Kernel.getpass = _fake_raw_input
PY

fail=0
for nb in "$@"; do
  name="$(basename "$nb")"
  cp "$nb" "$WORK/$name"
  printf '>> running %s ... ' "$nb"
  if ! (cd "$WORK" && jupyter nbconvert --to notebook --execute --inplace --allow-errors \
        --ExecutePreprocessor.timeout=300 --ExecutePreprocessor.kernel_name=python3 \
        "$name" >"$WORK/$name.log" 2>&1); then
    echo "nbconvert itself FAILED (kernel died or timed out); see $WORK/$name.log"; fail=1; continue
  fi
  python - "$WORK/$name" <<'PY' || fail=1
import json, re, sys
path = sys.argv[1]
nb = json.load(open(path, encoding="utf-8"))
cells = nb["cells"]
ex_start = next((i for i, c in enumerate(cells)
                 if c["cell_type"] == "markdown" and "".join(c["source"]).lstrip().startswith("## Exercises")),
                len(cells))
ansi = re.compile(r"\x1b\[[0-9;]*m")
real, expected = [], []
for i, c in enumerate(cells):
    if c["cell_type"] != "code":
        continue
    first = "".join(c["source"]).split("\n", 1)[0].split()
    declared = first[1] if len(first) == 2 and first[0] == "%%expect" else None
    for o in c.get("outputs", []):
        if o.get("output_type") == "error":
            if declared and o.get("ename") == declared:
                break  # %%expect got the exception it declared
            msg = f"cell {i}: {o.get('ename')}: {ansi.sub('', o.get('evalue', ''))[:120]}"
            if declared:
                msg += f"  (%%expect {declared} declared)"
            (expected if i >= ex_start else real).append(msg)
            break
if real:
    print("FAILED")
    for m in real:
        print("   ", m)
        src = "".join(cells[int(m.split()[1].rstrip(':'))]["source"]).splitlines()
        print("      " + "\n      ".join(src[:6]))
else:
    print("ok" + (f"  ({len(expected)} expected error(s) in exercise cells after cell {ex_start})" if expected else ""))
if expected:
    for m in expected:
        print("    exercises:", m)
sys.exit(1 if real else 0)
PY
done
echo ">> executed copies and logs are in $WORK (the repo notebooks were not modified)"
exit $fail
