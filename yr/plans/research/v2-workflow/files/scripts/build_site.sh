#!/usr/bin/env bash
# Build the Jupyter Book from a COPY of the repo (no .git), mirroring .claude/skills/build-book/build_book.sh.
# Usage: build_site.sh ROOT [--no-exec]     (ROOT = the copy; it is set explicitly since git rev-parse fails)
set -euo pipefail
ROOT="$(cd "$1" && pwd)"; NOEXEC="${2:-}"
export PATH="/root/.venvs/yrThinkPython/bin:$PATH"
cd "$ROOT"
echo ">> copying chapters and yr/*.ipynb into jb/"
cp chapters/chap[01][0-9].ipynb jb/
mkdir -p jb/yr && cp yr/*.ipynb jb/yr/
if [ "$NOEXEC" = "--no-exec" ]; then echo ">> skipping execute_notebooks.py"
else echo ">> execute_notebooks.py"; (cd jb && python execute_notebooks.py) > "$ROOT/../logs/$(basename "$ROOT")_execute.log" 2>&1 || { echo "!! execute failed"; tail -20 "$ROOT/../logs/$(basename "$ROOT")_execute.log"; }
fi
echo ">> prep_notebooks.py"
(cd jb && python prep_notebooks.py >/dev/null)
echo ">> jb build ."
LOG="$ROOT/../logs/$(basename "$ROOT")_jb.log"
(cd jb && jb build . ) >"$LOG" 2>&1 || { echo "!! build FAILED"; tail -40 "$LOG"; exit 1; }
BASE="$ROOT/.claude/skills/build-book/known_warnings.txt"
NORM="$ROOT/../logs/$(basename "$ROOT")_warnings.txt"
sed -r 's/\x1b\[[0-9;]*m//g' "$LOG" | grep -E "(WARNING|ERROR|CRITICAL):" \
  | sed -r 's#^.*/jb/([^:]+):[0-9]+: #\1: #' | sort -u >"$NORM" || true
echo ">> warnings: $(wc -l <"$NORM") total, $(comm -12 "$NORM" "$BASE" | wc -l) known (known_warnings.txt has $(wc -l <"$BASE"))"
NEW="$(comm -23 "$NORM" "$BASE")"
if [ -n "$NEW" ]; then echo "!! NEW warnings:"; echo "$NEW"; else echo ">> no new warnings"; fi
echo ">> missing known warnings:"; comm -13 "$NORM" "$BASE" | cut -c1-120
ls jb/_build/html/yr/ | head
