#!/usr/bin/env bash
# Create (if needed) and activate the venv used for building and running the book.
# The venv lives OUTSIDE the repo because the repo is inside Dropbox.
# Uses the system Python 3.12 (/usr/bin/python3); the linuxbrew default is 3.14,
# which is too new for jupyter-book 1.x.
set -euo pipefail

VENV="${THINKPYTHON_VENV:-$HOME/.venvs/yrThinkPython}"
PY="${THINKPYTHON_PYTHON:-/usr/bin/python3}"

if [ ! -x "$VENV/bin/python" ]; then
  echo ">> creating venv at $VENV with $PY ($("$PY" --version))"
  "$PY" -m venv "$VENV"
  "$VENV/bin/pip" install --quiet --upgrade pip
fi

# shellcheck disable=SC1091
source "$VENV/bin/activate"

need_install=0
python - <<'PY' || need_install=1
import importlib
for m in ("jupyter_book", "nbformat", "nbconvert", "ipykernel", "matplotlib", "yaml", "nbdime"):
    importlib.import_module(m)
PY
if [ "$need_install" = 1 ]; then
  echo ">> installing jupyter-book<2, nbconvert, ipykernel, nbmake, matplotlib, pyyaml, nbdime into $VENV"
  # matplotlib is needed by diagram.py; pyyaml by chapter 13.
  pip install --quiet "jupyter-book<2" ghp-import nbconvert ipykernel nbmake pytest matplotlib pyyaml nbdime
fi
echo ">> venv: $VENV  ($(python --version), jupyter-book $(python -c 'import jupyter_book;print(jupyter_book.__version__)'))"
