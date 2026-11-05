#!/usr/bin/env bash
# Tools for the yr/ review notebooks. See yr/README.md.
#   review.sh sync      PAGE... [--accept]   write everything derivable (outputs, examples, values, ...)
#   review.sh check     PAGE... [--static]   verify the page (fails if sync would change anything)
#   review.sh normalize PAGE...              repair a page saved in Colab (no kernel), then sync it
#   review.sh selftest                       prove that sync and check catch broken pages
#   review.sh pages                          list the pages in the review format
#   review.sh [COMMAND] --help               this help; with sync, check or selftest, also its options
# PAGE is a page in the review format (yr/chapNN_review.ipynb, or another page of a chapter written in that
# format: review_format.uses_review_format), or "all" for every such page (review.sh pages lists them).
# Uses the book's venv (outside the repo) and the pinned Colab-like kernel "colablike" (ensure_colab_venv.sh);
# caches jupyturtle.py and other downloads next to the book's venv.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(git -C "$HERE" rev-parse --show-toplevel 2>/dev/null || (cd "$HERE/../.." && pwd))"
cd "$ROOT"
for a in "$@"; do
  case "$a" in -h|--help)
    sed -n '2,/^[^#]/{/^#/s/^# \{0,1\}//p}' "$0"
    case "${1:-}" in sync|normalize) py=sync_review.py ;; check) py=check_review.py ;; selftest) py=selftest_review.py ;; *) py= ;; esac
    if [ -n "$py" ]; then
      echo; python3 -c 'import ast, sys; print(ast.get_docstring(ast.parse(open(sys.argv[1]).read())))' "$HERE/$py"
    fi
    exit 0 ;;
  esac
done
source "$ROOT/.claude/skills/build-book/ensure_venv.sh" >/dev/null
python -c "import cairosvg, nbclient" 2>/dev/null || pip install --quiet cairosvg nbclient
command -v uv >/dev/null || pip install --quiet uv

CACHE="$VENV/yr-cache"
export YR_REVIEW_CACHE="$CACHE"
mkdir -p "$CACHE"
if [ ! -f "$CACHE/jupyturtle.py" ]; then
  curl -sSL -o "$CACHE/jupyturtle.py" https://github.com/ramalho/jupyturtle/releases/download/2024-03/jupyturtle.py
fi
colab_kernel() { "$HERE/ensure_colab_venv.sh" >/dev/null; }

review_pages() { python - <<'PY'
import sys
from pathlib import Path
sys.path.insert(0, 'yr/tools')
import review_format
for p in sorted(Path('yr').glob('chap*_*.ipynb')):
    if review_format.uses_review_format(p):
        print(p)
PY
}

cmd="${1:-}"; [ $# -gt 0 ] && shift
if [ "${1:-}" = all ]; then shift; set -- $(review_pages) "$@"; fi
case "$cmd" in
  pages)     review_pages ;;
  sync)      colab_kernel; status=0
             args=(); nbs=(); for a in "$@"; do case "$a" in -*) args+=("$a");; *) nbs+=("$a");; esac; done
             for nb in "${nbs[@]}"; do python "$HERE/sync_review.py" "$nb" "${args[@]}" || status=$?; done
             exit $status ;;
  check)     colab_kernel; status=0
             args=(); nbs=(); for a in "$@"; do case "$a" in -*) args+=("$a");; *) nbs+=("$a");; esac; done
             for nb in "${nbs[@]}"; do python "$HERE/check_review.py" "$nb" "${args[@]}" || status=1; done
             exit $status ;;
  normalize) for nb in "$@"; do python "$HERE/sync_review.py" "$nb" --static; done ;;
  selftest)  colab_kernel; python "$HERE/selftest_review.py" ;;
  *) sed -n '2,/^[^#]/{/^#/s/^# \{0,1\}//p}' "$0"; exit 2 ;;
esac
