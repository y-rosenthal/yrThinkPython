# Build notes (from the retired project board)

Moved from `PROJECT_BOARD.md` on 2026-10-12, when its tasks became GitHub issues on y-rosenthal/yrThinkPython
(the pending-work items; Task N is issue #N). These notes describe the build with the `ThinkPythonSolutions`
notebooks as they were on 2026-09-19. Check them against `README.md` before you rely on them.

## How this repo fits together

`ThinkPythonSolutions/soln/*.ipynb` is the canonical source: it holds the prose, the code, and the executed outputs. Everything else is generated from it by a `prep_notebooks.py` + `build.sh` pair:

| Target | Built by | What the prep step does |
|--------|----------|-------------------------|
| `chapters/` (student notebooks, and `ThinkPythonNotebooks.zip`) | `chapters/build.sh` | Replaces solution source with `# Solution goes here`, clears tags, **clears all outputs** |
| `blank/` | `blank/build.sh` | Clears the source of every code cell except those tagged `keep`, clears all outputs |
| `jb/` → GitHub Pages | `jb/build.sh` | Blanks solution source, strips `%%expect`, adds MyST labels; **keeps outputs** |

So a content fix belongs in `ThinkPythonSolutions/soln/`, and reaches readers only after the relevant `build.sh` is re-run. The published HTML and the downloadable notebooks are prepped differently, which is the direct cause of issue #3.

## Editing a chapter

Edit through jupytext rather than the notebook JSON, and keep the `.md` afterward:

```bash
cd ThinkPythonSolutions/soln
jupytext --to md chapNN.ipynb          # re-export first, so the md is fresh
#  ... edit chapNN.md ...
jupytext --update --to ipynb chapNN.md # --update preserves stored outputs
```

`--update` merges into the existing notebook; plain `--to ipynb` would discard the outputs the website renders.

The round-trip was verified once on this repo — byte-identical, with tags (`solution`, `remove-cell`, `keep`) and `%%add_method_to` magics surviving intact. Treat that as settled; there is no need to re-check it after each conversion.

The `.md` stays on disk, untracked, as a recovery copy: an open Jupyter session saving over a chapter will silently revert edits back to HEAD, and re-applying from the markdown is far cheaper than redoing the work. Two cautions: always re-export before editing, or a stale `.md` pushed back with `--update` will clobber edits made in Jupyter; and close the Jupyter tab for a chapter before editing it here.
