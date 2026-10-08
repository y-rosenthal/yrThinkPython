#!/usr/bin/env bash
# Create or update the pinned Colab-like kernel venv that writes and checks stored outputs
# (Python 3.12, IPython 7.34.0, ipykernel 6.17.1, every other package pinned by colablike.lock),
# and register it as the Jupyter kernel "colablike" (kernelspec under $KDIR, default ~/.local/share/jupyter).
# Usage: ensure_colab_venv.sh [VENV] [KDIR]      (needs uv: https://docs.astral.sh/uv/)
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
VENV="${1:-$HOME/.venvs/colablike}"
KDIR="${2:-$HOME/.local/share/jupyter}"
[ -x "$VENV/bin/python" ] || uv venv -q -p 3.12 "$VENV"
uv pip sync -q --python "$VENV/bin/python" "$HERE/colablike.lock"
mkdir -p "$KDIR/kernels/colablike"
cat > "$KDIR/kernels/colablike/kernel.json" <<JSON
{"argv": ["$VENV/bin/python", "-m", "ipykernel_launcher", "-f", "{connection_file}"],
 "display_name": "colablike (py3.12, IPython 7.34, ipykernel 6.17.1)", "language": "python"}
JSON
"$VENV/bin/python" -c 'import sys, IPython, ipykernel; print("colablike kernel:", sys.version.split()[0], "IPython", IPython.__version__, "ipykernel", ipykernel.__version__)'
