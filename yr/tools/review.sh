#!/usr/bin/env bash
# Tools for the yr/ review notebooks. See yr/README.md.
#   review.sh sync      yr/chapNN_review.ipynb [--accept]  write everything derivable (outputs, examples, values, ...)
#   review.sh check     yr/chapNN_review.ipynb [--static]  verify the page (fails if sync would change anything)
#   review.sh normalize yr/chapNN_review.ipynb             repair a page saved in Colab (no kernel), then sync it
#   review.sh selftest                                     prove that sync and check catch broken pages
#   review.sh images    yr/chapNN_review.ipynb             old-format pages only: draw the data-turtle pictures
# Uses the book's venv (outside the repo) and the pinned Colab-like kernel "colablike" (ensure_colab_venv.sh);
# caches jupyturtle.py and other downloads next to the book's venv.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(git -C "$HERE" rev-parse --show-toplevel 2>/dev/null || (cd "$HERE/../.." && pwd))"
cd "$ROOT"
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

cmd="${1:-}"; [ $# -gt 0 ] && shift
case "$cmd" in
  sync)      colab_kernel; status=0
             args=(); nbs=(); for a in "$@"; do case "$a" in -*) args+=("$a");; *) nbs+=("$a");; esac; done
             for nb in "${nbs[@]}"; do python "$HERE/sync_review.py" "$nb" "${args[@]}" || status=$?; done
             exit $status ;;
  check)     colab_kernel; status=0
             args=(); nbs=(); for a in "$@"; do case "$a" in -*) args+=("$a");; *) nbs+=("$a");; esac; done
             for nb in "${nbs[@]}"; do python "$HERE/check_review.py" "$nb" "$CACHE/jupyturtle.py" "${args[@]}" || status=1; done
             exit $status ;;
  normalize) for nb in "$@"; do python "$HERE/sync_review.py" "$nb" --static; done ;;
  selftest)  colab_kernel; python "$HERE/selftest_review.py" ;;
  images)    for nb in "$@"; do PYTHONPATH="$CACHE" python "$HERE/turtle_images.py" "$nb"; done ;;
  *) sed -n '2,8p' "$0"; exit 2 ;;
esac
