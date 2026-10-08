#!/usr/bin/env bash
# Prototype v2 (after the reviews), end to end: convert -> sync (store outputs) -> gates -> checks -> self-test ->
# A/B error page -> website build -> screenshots. Never touches the repo (reads yr/chap05_review.ipynb only).
# Usage: make_all.sh            (from anywhere; writes into the v2 folder; log: v2/logs/make_all.txt)
set -uo pipefail
V2="$(cd "$(dirname "$0")/.." && pwd)"; cd "$V2"
PY=/root/.venvs/yrThinkPython/bin/python
LABPY=/tmp/claude-0/-home-user-yrThinkPython/6571a165-f8cc-5e43-8b74-c00357a4a6f6/scratchpad/ultra/jupyter-facts/venv-lab/bin/python
REPO=/home/user/yrThinkPython
NOISE='Debugger warning\|frozen modules\|PYDEVD\|^0.00s\|IPKernelApp\|make the debugger\|to python to disable'
step() { echo; echo "=== $*"; }

step "0. pinned Colab-like stack: build a venv from scripts/colablike.lock (kernel 'colabfresh')"
scripts/ensure_colab_venv.sh "$V2/../v2fix_exp/colab-fresh" "$V2/../v2fix_exp/kfresh"

step "1. convert (static) $REPO/yr/chap05_review.ipynb"
$PY scripts/convert_v2.py $REPO/yr/chap05_review.ipynb out/chap05_converted.ipynb out/removed_blocks.json

step "2. sync: reference run, wrap raising run cells, run as stored, store normalized outputs + stamp"
$PY scripts/sync_v2.py out/chap05_converted.ipynb --kernel colablike --out out/chap05_review.ipynb 2>&1 | grep -v "$NOISE" | cut -c1-200

step "3. conversion gate: every removed expected-output block equals the stored real output"
$PY scripts/verify_removed.py out/chap05_review.ipynb out/removed_blocks.json

step "4. determinism: two more syncs, a re-sync, a sync on the venv built from the lock, a sync with TMPDIR set"
mkdir -p out/determinism
$PY scripts/sync_v2.py out/chap05_converted.ipynb --kernel colablike --out out/determinism/run1.ipynb 2>&1 | grep -v "$NOISE" | tail -1
$PY scripts/sync_v2.py out/chap05_converted.ipynb --kernel colablike --out out/determinism/run2.ipynb 2>&1 | grep -v "$NOISE" | tail -1
$PY scripts/sync_v2.py out/chap05_review.ipynb --kernel colablike --out out/determinism/resync.ipynb 2>&1 | grep -v "$NOISE" | tail -1
$PY scripts/sync_v2.py out/chap05_converted.ipynb --kernel colabfresh --out out/determinism/freshvenv.ipynb 2>&1 | grep -v "$NOISE" | tail -1
mkdir -p "$V2/../v2fix_exp/tmpx"
TMPDIR="$V2/../v2fix_exp/tmpx" $PY scripts/sync_v2.py out/chap05_review.ipynb --kernel colablike --out out/determinism/tmpdir.ipynb 2>&1 | grep -v "$NOISE" | tail -1
sha256sum out/chap05_review.ipynb out/determinism/*.ipynb
for f in run1 run2 resync freshvenv tmpdir; do cmp -s out/chap05_review.ipynb out/determinism/$f.ipynb && echo "$f: byte-identical" || echo "$f: DIFFERS"; done
echo "sync on the book venv (IPython 9) must be refused:"
$PY scripts/sync_v2.py out/chap05_review.ipynb --kernel bookvenv --out out/determinism/bookvenv.ipynb 2>&1 | grep -v "$NOISE" | tail -2 | cut -c1-200

step "5. Run-all simulation on both stacks (stop at first error status; tags ignored; real download)"
for k in colablike bookvenv; do $PY scripts/runall_sim.py out/chap05_review.ipynb $k --download --save out/runall_$k.ipynb 2>&1 | grep -v "$NOISE"; done

step "6. checks: static, full on the pinned stack, semantic on the book venv (and without --semantic: must fail)"
$PY scripts/check_v2.py out/chap05_review.ipynb --static 2>&1 | grep -v "$NOISE"
$PY scripts/check_v2.py out/chap05_review.ipynb --kernel colablike 2>&1 | grep -v "$NOISE"
$PY scripts/check_v2.py out/chap05_review.ipynb --kernel bookvenv --semantic 2>&1 | grep -v "$NOISE"
$PY scripts/check_v2.py out/chap05_review.ipynb --kernel bookvenv 2>&1 | grep -v "$NOISE" | cut -c1-160

step "7. self-test: mutations and repair scenarios"
$PY scripts/selftest_v2.py out/chap05_review.ipynb 2>&1 | grep -v "$NOISE" | cut -c1-230

step "8. A/B error page for the Colab test"
$PY scripts/make_ab_demo.py out/errors_A_vs_B.ipynb 2>&1 | grep -v "$NOISE"

step "9. repo lint (check_notebooks.py, unchanged) on the v2 page"
python3 $REPO/.claude/skills/check-notebooks/check_notebooks.py out/chap05_review.ipynb 2>&1 | sed "s#$V2/##" | tail -16

step "10. website: build a copy of the repo with the v2 page, review_v2.py and the adapted prep"
cp out/chap05_review.ipynb book/yr/chap05_review.ipynb
cp scripts/prep_notebooks.py book/jb/prep_notebooks.py
cp scripts/review_v2.py book/yr/tools/review_v2.py
scripts/build_site.sh book
$LABPY scripts/verify_site.py book/jb/_build/html/yr/chap05_review.html book_base/jb/_build/html/yr/chap05_review.html out/chap05_review.ipynb
for c in 02 03 04 06 07; do cmp -s book/jb/yr/chap${c}_review.ipynb book_base/jb/yr/chap${c}_review.ipynb && echo "old-format chap$c: prep output identical to today's prep" || echo "old-format chap$c: prep output DIFFERS"; done
$LABPY scripts/shot_site.py book/jb/_build/html/yr/chap05_review.html out/shots site_v2 1 8 14 17

step "11. dry run on the other five pages (mechanical conversion only: no page-specific wording edits yet)"
O="$V2/../v2fix_exp/others"; mkdir -p "$O"
for c in 02 03 04 06 07; do
  echo "-- chap$c"
  $PY scripts/convert_v2.py $REPO/yr/chap${c}_review.ipynb $O/chap${c}_converted.ipynb $O/removed_$c.json 2>&1 | grep '^wrote' | sed "s#$O/##"
  $PY scripts/sync_v2.py $O/chap${c}_converted.ipynb --out $O/chap${c}_review.ipynb 2>&1 | grep -v "$NOISE" | grep -v 'new output' | sed "s#$O/##" | cut -c1-160
  $PY scripts/verify_removed.py $O/chap${c}_review.ipynb $O/removed_$c.json | grep -v '^OK' | cut -c1-200
  $PY scripts/check_v2.py $O/chap${c}_review.ipynb 2>&1 | grep -v "$NOISE" | sed "s#$O/##" | cut -c1-200
done
