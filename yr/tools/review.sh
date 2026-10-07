#!/usr/bin/env bash
# Tools for the yr/ review notebooks. See yr/README.md.
#   review.sh images yr/chapNN_review.ipynb   draw the data-turtle pictures (runs the code)
#   review.sh check  yr/chapNN_review.ipynb   run the notebook and verify every answer
# Uses the book's venv (outside the repo) and caches jupyturtle.py next to it.
set -euo pipefail
ROOT="$(git -C "$(dirname "$0")" rev-parse --show-toplevel)"
cd "$ROOT"
source "$ROOT/.claude/skills/build-book/ensure_venv.sh" >/dev/null
python -c "import cairosvg" 2>/dev/null || pip install --quiet cairosvg

CACHE="$VENV/yr-cache"
mkdir -p "$CACHE"
if [ ! -f "$CACHE/jupyturtle.py" ]; then
  curl -sSL -o "$CACHE/jupyturtle.py" https://github.com/ramalho/jupyturtle/releases/download/2024-03/jupyturtle.py
fi

case "${1:-}" in
  images) shift; for nb in "$@"; do PYTHONPATH="$CACHE" python "$ROOT/yr/tools/turtle_images.py" "$nb"; done ;;
  check)  shift; status=0
          for nb in "$@"; do python "$ROOT/yr/tools/check_review.py" "$nb" "$CACHE/jupyturtle.py" || status=1; done
          exit $status ;;
  *) sed -n '2,5p' "$0"; exit 2 ;;
esac
