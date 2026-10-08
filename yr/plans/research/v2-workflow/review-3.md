# review:3

```json
{
 "verdict": "v2 fixes the three things Prof. Rosenthal saw in Colab: the repeated output, the visible run_code(\"\"\"...\"\"\") wrapper, and the run cells bunched at the end. It is ready for one Colab pass (Part A2), with one cheap fix first (issue 1). The layout Colab will show on open is backed by strong evidence: Answers collapsed, form view hiding the code, stored outputs visible. I also confirmed that Run all in Colab will reproduce the stored tracebacks. The hash in his screenshot ('/tmp/ipykernel_2148/445721521.py') is exactly ipykernel's murmur2 hash of prototype part a's code, computed with the Colab-like venv. So after Run all, Q8's tracebacks will differ from the stored ones only in the pid (ipykernel_0 vs ipykernel_NNNN). Q14 will also differ in a frame file name (issue 4). Colab's shell (_shell.py) does not override run_cell. Still unknown, and only live Colab can settle them: whether stored errors get the red (!) icon or the 'Explain error' button before Run all; whether the table of contents lists form titles; whether Colab honors the PNG's width/height metadata; whether the 2026 UI still shows 'Show code'; whether '```python run' is coloured.\n\nPART A2: SMALLEST COLAB CHECKLIST (about 10 minutes, Chrome, signed in). Open v2 from a GitHub link: with his OK, push only out/chap05_review.ipynb to yr-runall-research (that branch never deploys; v1 was tested from there). Uploading the file also works, but then the 'not authored by Google' dialog is not exercised. Do NOT click the page's own 'Run this page on Colab' link: it opens today's v3 page.\n\nBEFORE Run all (do not connect):\n- A2-1 Page and contents sidebar: are all 17 Answers closed? Q1 should read '2 cells hidden' and Q8 '7 cells hidden'. Is there a red mark on any Answer row or contents entry? Does the sidebar list any 'Output' or 'Output of part a' entries? [shot of page and sidebar]\n- A2-2 Q1 and Q8 question code: syntax-coloured, and the word 'run' not shown?\n- A2-3 Open Q1. The output '2 15 / 2 0 3 / 3 -4' should appear exactly once, in a cell showing only a title, a 'Show code' link (write down the exact wording) and a play button, with no code. The explanation follows. [shot]\n- A2-4 Open Q8. Expected order: Part a text, traceback whose header reads 'ipykernel_0/2636000202.py, line 2', Part b, traceback, Part c, traceback, summary. No run_code anywhere. Is there a red (!) icon or an 'Explain error' button on these STORED errors? [shot]\n- A2-5 Open Q17: the stored tree should be about as large as a 300x220 canvas, not double size. [shot]\n\nRuntime > Run all > Run anyway; wait until idle:\n- A2-6 Did all Answers stay closed? Is anything visible outside them except 'Downloaded jupyturtle.py'? Is there a red mark on the closed Q8 or Q14 rows, or in the sidebar? [shot]\n- A2-7 Open Q8. Each header should now read ipykernel_<a number other than 0>, which proves the cells re-ran (stored and live outputs otherwise look the same). Are there red (!) icons and 'Next steps: Explain error' buttons? Ask him directly whether he minds them: this decides variant A vs B. [shot]\n- A2-8 Open Q14. The traceback should still show '<cell line: 0>' and '... last 1 frames repeated' (Colab still on IPython 7.34). The countdown_by_two frames should now read '/tmp/ipython-input-3568901665.py' (predicted, harmless). If it shows 'Cell In[', Colab has upgraded IPython and the stored outputs must be regenerated. [shot]\n- A2-9 Open Q17 and Q1: the cell now shows an execution counter, and the tree is the same size as before.\n\nWhat the results decide:\n- Code visible in A2-3: form view was not applied; check how the annotation and cellView interact.\n- Sidebar lists titles: use an empty '# @title' or a title that names the question.\n- Tree double size: store the PNG at scale 1.\n- 'run' visible or no colour: use the plan's cell-tag marker.\n- He dislikes the icons, buttons or red marks: variant B (Part B tests 7-9).\n- Answers open by themselves: fallback C.\n\nOptional, one extra look: in the test copy only, make Q1's run cell cellView-only (title without '{ display-mode: \"form\" }'). If it looks like Q2's, drop the annotation everywhere; that also removes the noise in JupyterLab's hidden-code bar.",
 "issues": [
  {
   "severity": "major",
   "where": "out/chap05_review.ipynb run cells 846ec840, 9b6401a8, 57198ee6 (Q8 a/b/c), 2b7f1ccf (Q14) and 586a560b (Q17); scripts/review_v2.py render_run_cell",
   "problem": "If a student presses play on a hidden run cell before the setup cells have run (in Colab, play on a closed runtime connects and runs only that cell), the stored output is replaced by a NameError. The traceback shows the hidden '# @title' line and the 'run_code(r\"\"\"' wrapper, which is exactly the look Prof. Rosenthal objected to. I reproduced this on the Colab-like kernel (v2review_colab/single_cell.py): 'NameError: name run_code is not defined' with '1 # @title Output of part a ... ----> 2 run_code(r\"\"\"'. Q17 gives 'NameError: make_turtle' with hidden lines 10-14 shown.",
   "fix": "Cheapest: add one line to the help note: 'If an Answer shows NameError, run the setup cells first (Runtime > Run all).' Better, since the code is hidden anyway: generate wrapped cells that do not need setup, as `get_ipython().run_cell(r\"\"\"\\n<code>\\n\"\"\");` (the trailing ';' stops the ExecutionResult from being displayed). Verified on the Colab-like kernel: correct SyntaxError at line 2, the next cell still runs, and without setup Q14 shows only 'countdown_by_two(5)' in its NameError. This drops the Stop fix and the plain-Python fallback. Keep the Stop fix with a two-line form if wanted: `r = get_ipython().run_cell(...)` / `if isinstance(r.error_in_exec, KeyboardInterrupt): raise KeyboardInterrupt`. Both forms are generated by sync, so nothing has to be kept in step by hand."
  },
  {
   "severity": "major",
   "where": "Design item 4 (errors): run_code variant A, unchanged from the prototype; builder open_issues (2)",
   "problem": "Prof. Rosenthal's 'not exactly right' description of Q8 included the red (!) icon next to each cell and 'Next steps: Explain error' under each traceback. v2 keeps variant A, so after Run all these will certainly appear again on Q8 a, b, c and Q14: Colab's _showtraceback sends an iopub 'error' message, and his screenshots show Colab marks the cell from that even though the reply status is ok. Whether they also appear on STORED errors before Run all is unknown. No Colab-saved notebook in the corpus records an error status (executionInfo is either absent or 'ok' even on error cells), so any badge on open would have to come from the outputs themselves. Also untested: whether Colab puts a red mark on a closed Answer row or contents entry. That would hint which Answers are errors, which matters on later pages where the answer to 'what is displayed?' is an error.",
   "fix": "Do not treat this as settled. A2-4, A2-6 and A2-7 ask him directly. If he dislikes the icons, buttons or marks, switch to variant B (traceback printed on stderr; plan Part B tests 7-9 already check that Run all gets past it). Before switching, adapt the S10/S11/R checks to read the error name from the last stderr line, because variant B has no ename field."
  },
  {
   "severity": "major",
   "where": "builder open_issues (1): 'check Q1, Q8, Q14 and Q17 before and after Run all'",
   "problem": "Because outputs are stored and normalized to look like Colab's, an Answer showing its output no longer proves that Run all executed that cell. Stored and live stdout and drawings look the same. The checklist as proposed would pass even if Run all skipped the Answers, or stopped early with stored outputs left in place.",
   "fix": "Use visible markers in A2. Q8 headers change from 'ipykernel_0' to 'ipykernel_<pid>'. Execution counters appear (stored cells have none). Q14's countdown_by_two frames change to '/tmp/ipython-input-3568901665.py'. Q17's cell gets the last counter. The A2 list in the verdict uses these."
  },
  {
   "severity": "minor",
   "where": "out/chap05_review.ipynb cell 2b7f1ccf (Q14) stored traceback; review_v2.normalize_text",
   "problem": "After Run all in Colab, Q14's traceback will not match the stored one. Frames from code defined in a TOP-LEVEL Colab cell are named '/tmp/ipython-input-<murmur2>.py'. I verified this: the NOAA AMS-2026 Colab outputs' 2326070031 and 3432358611 equal ipykernel's murmur2 of those cells' sources. Nested run_cell frames are named '/tmp/ipykernel_<pid>/<hash>.py', as in his screenshot. So Colab will show '/tmp/ipython-input-3568901665.py in countdown_by_two(n)' where the stored output says '/tmp/ipykernel_0/3568901665.py' (3568901665 is the hash of definition cell a4b2ec88). The report's claim that the stored outputs 'look like Colab's own' is not exact for these frames.",
   "fix": "Harmless. Document it, or have sync rewrite '/tmp/ipykernel_<pid>/<h>.py' to '/tmp/ipython-input-<h>.py' when <h> is the murmur2 hash of a top-level cell on the page. The semantic comparison already ignores file names."
  },
  {
   "severity": "minor",
   "where": "out/chap05_review.ipynb cell 586a560b (Q17) stored image/png; review_v2.store_drawing (scale=2)",
   "problem": "The stored PNG is 600x440 pixels and is shown at 300x220 only through output metadata ({'image/png': {'width': 300, 'height': 220}}). If Colab's renderer ignores that metadata, the tree appears at double size before Run all and then shrinks to the live 300x220 SVG after it. This was not verified in Colab.",
   "fix": "Covered by A2-5 and A2-9. If Colab ignores the metadata, render with scale=1, or embed the PNG with explicit width/height HTML. In either case the SVG-hash reuse rule still applies."
  },
  {
   "severity": "minor",
   "where": "Run-cell title line '# @title Output[ of part x] { display-mode: \"form\" }' (13 cells)",
   "problem": "It is unknown whether Colab's table of contents lists titled code cells. If it does, the sidebar gains 13 context-free entries ('Output', 'Output of part a', ...) on top of the 17 'Answer' entries. Also, Colab's 2026 redesign may render the title as a heading-like label, and the 'Show code' wording is unverified.",
   "fix": "Covered by A2-1 and A2-3. If titles are listed, use an empty '# @title' (Colab then shows only 'Show code'), or a title that names the question, e.g. 'Q8 part a output'. Separately, the optional cellView-only test on Q1 can settle dropping '{ display-mode: \"form\" }', which is the format Colab's own UI writes."
  },
  {
   "severity": "minor",
   "where": "Question run blocks (```python run fences), e.g. cells ecdbd022 and 2c5a5021",
   "problem": "v2 is the first page Colab will open with the '```python run' info string; prototype v1 had plain ```python. If Colab's markdown renderer uses the whole info string, the question code may show without colour, or show the word 'run'. That would make every question look worse before anything else is checked.",
   "fix": "Covered by A2-2. If it fails, use the plan's fallback marker (a cell tag); it is one constant in review_v2.RUN_FENCE."
  },
  {
   "severity": "minor",
   "where": "out/chap05_review.ipynb cell 673c9695 (run_code setup cell, tags setup + remove-cell); intro cell d9a4998f",
   "problem": "In Colab the run_code definition shows as an 18-line code cell. Nothing on the page explains it any more (the intro says only 'The setup cell below downloads jupyturtle...'), and no visible cell calls it, because every call is now hidden. It reads as clutter.",
   "fix": "Give it the same hidden-code treatment, e.g. '# @title Helper used by the Answers { display-mode: \"form\" }' with cellView form and source_hidden. Or add 'and defines a helper the Answers use' to the intro sentence. Update the managed-cell check S12 to match."
  },
  {
   "severity": "minor",
   "where": "scripts/check_v2.py S5 (`dict(c.metadata) != RUN_CELL_METADATA`); workflow",
   "problem": "If anyone saves the page from Colab back to GitHub ('Save a copy in GitHub'), Colab adds metadata to cells and outputs (id, colab, outputId, executionInfo) and stores its own live outputs (pid, ipython-input frames, ImportError NOTE blocks). The checker's exact-equality rule then reports that the run cells 'do not hide their code', and the stored outputs drift from what sync generates.",
   "fix": "Document 'never save review pages from Colab; edit locally and run sync'. Make S5 require the two keys (cellView == 'form', jupyter.source_hidden == true) and forbid outputs_hidden and collapsed, rather than demand exact equality. Or have sync strip Colab's keys."
  },
  {
   "severity": "minor",
   "where": "scripts/check_v2.py (missing rules recommended by the hidden-code research)",
   "problem": "Nothing rejects '#\\s*@(title|param|markdown)' inside a run block (Colab probably parses form markup on any line, even inside the run_code string), or a %%cell magic in a run cell. Colab tolerates a title line before a cell magic; Jupyter does not. Chapter 5 is clean, but later pages are not checked.",
   "fix": "Add both rules to S4/S5 before converting other chapters."
  }
 ]
}
```
