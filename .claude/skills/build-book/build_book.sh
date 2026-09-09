#!/usr/bin/env bash
# Build the Jupyter Book locally, mirroring .github/workflows/deploy-book.yml.
# Usage: build_book.sh [--clean] [--open] [--update-baseline]
set -euo pipefail
ROOT="$(git -C "$(dirname "$0")" rev-parse --show-toplevel)"
cd "$ROOT"
source "$ROOT/.claude/skills/build-book/ensure_venv.sh"

CLEAN=0; OPEN=0; UPDATE=0
for a in "$@"; do
  case "$a" in
    --clean) CLEAN=1 ;;
    --open) OPEN=1 ;;
    --update-baseline) UPDATE=1 ;;
    *) echo "unknown option: $a" >&2; exit 2 ;;
  esac
done

if [ "$CLEAN" = 1 ]; then
  echo ">> jb clean"; (cd jb && jb clean . >/dev/null)
fi

echo ">> copying chapters/chap[01][0-9].ipynb -> jb/"
cp chapters/chap[01][0-9].ipynb jb/

echo ">> prep_notebooks.py (strip %%expect, blank '# Solution' cells, add section labels)"
(cd jb && python prep_notebooks.py >/dev/null)

echo ">> jb build ."
LOG="$(mktemp)"
if ! (cd jb && jb build . ) >"$LOG" 2>&1; then
  echo "!! build FAILED. Last 40 lines:"; tail -40 "$LOG"; exit 1
fi
# Sphinx warnings are the usual way a broken TOC/link shows up. The upstream notebooks
# already produce a fixed set of warnings (missing section_* cross-reference targets, a few
# lexing warnings); those are recorded in known_warnings.txt so only NEW ones are shown.
BASE="$ROOT/.claude/skills/build-book/known_warnings.txt"
NORM="$(mktemp)"
sed -r 's/\x1b\[[0-9;]*m//g' "$LOG" | grep -E "(WARNING|ERROR|CRITICAL):" \
  | sed -r 's#^.*/jb/([^:]+):[0-9]+: #\1: #' | sort -u >"$NORM" || true
if [ "$UPDATE" = 1 ]; then
  cp "$NORM" "$BASE"; echo ">> baseline updated: $(wc -l <"$BASE") known warnings"
fi
touch "$BASE"
NEW="$(comm -23 "$NORM" "$BASE")"
echo ">> warnings: $(wc -l <"$NORM") total, $(comm -12 "$NORM" "$BASE" | wc -l) known (see known_warnings.txt)"
if [ -n "$NEW" ]; then
  echo "!! NEW warnings (fix these):"; echo "$NEW"
else
  echo ">> no new warnings"
fi
rm -f "$NORM"
rm -f "$LOG"

INDEX="$ROOT/jb/_build/html/index.html"
echo ">> output: $INDEX"
ls jb/_build/html/chap*.html | wc -l | xargs echo ">> chapter pages built:"
if [ "$OPEN" = 1 ]; then xdg-open "$INDEX" >/dev/null 2>&1 || true; fi
