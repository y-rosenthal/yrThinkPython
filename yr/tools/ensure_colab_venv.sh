#!/usr/bin/env bash
# Create or update the pinned Colab-like kernel that writes and checks the review pages' stored outputs
# (Python 3.13, IPython 7.34.0, ipykernel 6.17.1; every package pinned by colablike.lock), and register it
# as the Jupyter kernel "colablike". Called by review.sh; run it by hand only to rebuild the venv.
#   ensure_colab_venv.sh [VENV] [KDIR]     defaults: ~/.venvs/colablike, ~/.local/share/jupyter
# Colab's kernel has Python's default recursion limit, 1000 (seen 2026-10-09); here jedi, which IPython's completer
# imports, raises it to 3000, so the kernel sets it back (RecursionError tracebacks count the frames).
# Needs uv (https://docs.astral.sh/uv/); review.sh installs it into the book venv if it is missing.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
VENV="${1:-$HOME/.venvs/colablike}"
KDIR="${2:-$HOME/.local/share/jupyter}"
UV="$(command -v uv || true)"
[ -n "$UV" ] || { echo "ensure_colab_venv.sh: uv not found (pip install uv)" >&2; exit 2; }
[ -x "$VENV/bin/python" ] || "$UV" venv -q -p 3.13 "$VENV"
"$UV" pip sync -q --python "$VENV/bin/python" "$HERE/colablike.lock"
mkdir -p "$KDIR/kernels/colablike"
cat > "$KDIR/kernels/colablike/kernel.json" <<JSON
{"argv": ["$VENV/bin/python", "-m", "ipykernel_launcher", "-f", "{connection_file}",
          "--IPKernelApp.exec_lines=import sys; sys.setrecursionlimit(1000)"],
 "env": {"PYDEVD_DISABLE_FILE_VALIDATION": "1"},
 "display_name": "colablike (Python 3.13, IPython 7.34, ipykernel 6.17.1)", "language": "python"}
JSON
