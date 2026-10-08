# review:1

```json
{
 "verdict": "The v2 page fixes what Prof. Rosenthal complained about. I checked the notebook JSON, the built site and JupyterLab, question by question for all 17. No Answer repeats its output or shows its code. The 13 run cells each appear once. Each one sits where its removed text block was, so the existing prose leads into it or follows it naturally, and no \"displays:\"-style sentence is left dangling. Q8 interleaves correctly (Part a, its error, Part b, its error, Part c, its error, then the summary) in the notebook, on the site and in JupyterLab. Nothing that gives away an answer shows outside a collapsed Answer. Before Run all there are 13 stored outputs, all inside Answers. After Run all (in both simulated runs, out/runall_colablike.ipynb and runall_bookvenv.ipynb) the only output outside an Answer is the setup cell's 'Downloaded jupyturtle.py'. The titles 'Output' and 'Output of part a/b/c' make sense.\n\nNothing blocks, but some things still need work:\n(a) Two things from his Q8 screenshot will come back in Colab after Run all: the red error icon and the 'Explain error' button. The noisy 'File \"/tmp/ipykernel_…/….py\"' header is also still in the saved tracebacks.\n(b) On the site, Q14's traceback is wider than its box. It also shows the file path noise and a confusing '<cell line: 0>'.\n(c) In JupyterLab the question code (```python run blocks) is not syntax-highlighted. I confirmed this in the page itself.\n(d) Small wording fixes, in Q8 and in the help note.\n\nColab itself is still untested. The open questions to check there are listed below.\n\nEvidence: probe scripts in /tmp/claude-0/-home-user-yrThinkPython/6571a165-f8cc-5e43-8b74-c00357a4a6f6/scratchpad/ultra/v2review_student/ (probe.py checks JupyterLab highlighting; probe_site.py measures overflow on the site). The notebook reviewed is /tmp/claude-0/-home-user-yrThinkPython/6571a165-f8cc-5e43-8b74-c00357a4a6f6/scratchpad/ultra/v2/out/chap05_review.ipynb. The repo was not touched.",
 "issues": [
  {
   "severity": "major",
   "where": "Q8 parts a/b/c and Q14 in Colab after Run all (run_code variant A); stored error outputs in v2/out/chap05_review.ipynb cells 846ec840, 9b6401a8, 57198ee6, 2b7f1ccf",
   "problem": "His Q8 screenshot showed six problems. v2 fixes four of them: the visible run_code(\"\"\"…\"\"\") wrapper, the string-coloured code, the three cells bunched at the end, and the repeated output. Two will come back after Run all in Colab, because run_code still produces real error outputs: the red error icon next to each cell and the 'Next steps: Explain error' button under each traceback. That is four stacked Gemini buttons across Q8 and Q14. The saved tracebacks also still start with 'File \"/tmp/ipykernel_0/2636000202.py\", line 2', a made-up path that means nothing to a student. Colab will replace it with its real '/tmp/ipykernel_<pid>/…' path after Run all. We still don't know which of these he meant by 'not exactly right'.",
   "fix": "Before rollout, show him Q8 in Colab after Run all and ask him directly about the error icon and the Explain button. Have variant B ready: run_code prints the formatted traceback to stderr. That removes the icon and button both before and after Run all, and Run all still reaches the end. The checks can get the error name from the traceback's last line ('SyntaxError: expected ':''), or from the run cell's metadata. Separately, rewrite the saved '/tmp/ipykernel_\\d+/\\d+\\.py' to '<cell>' when storing outputs. The comparison with a fresh run already ignores that part, so the page shows 'File \"<cell>\", line 2' before Run all."
  },
  {
   "severity": "major",
   "where": "Website, Q14 Answer (and the headers of the three Q8 tracebacks); v2/scripts/prep_notebooks.py, the code that turns stored outputs into ```text blocks",
   "problem": "I measured this on the built page (book/jb/_build/html/yr/chap05_review.html). At a 1300px desktop width, Q14's traceback is 664px wide in a 635px box, so it needs a horizontal scrollbar. The 75-dash line and the 'RecursionError    Traceback (most recent call last)' line are cut off on screen, as the site_v2_q14_open.png screenshot shows. Today's site has no such overflow for Q14. The traceback also shows '/tmp/ipykernel_0/3608748751.py in <cell line: 0>()' directly above '----> 1 countdown_by_two(5)'. 'Line 0' next to an arrow on line 1 will confuse students. Today's site shows one clean line.",
   "fix": "Change only the site version in prep_notebooks.py, and leave the notebook's saved output as it is. Drop the dashed line and the '<Name>  Traceback (most recent call last)' line. Replace '/tmp/ipykernel_N/<hash>.py' with '<cell>', and '<cell line: 0>' with '<cell>'. For SyntaxError and IndentationError, keep only the code line, the caret and the last line. Add a check to verify_site.py that no output block inside an Answer is wider than its box at 1300px, using the scrollWidth measurement in probe_site.py."
  },
  {
   "severity": "minor",
   "where": "Every question's ```python run block (cells ecdbd022, 717efcbd, 2c5a5021, …) in JupyterLab 4.6.4 / Notebook 7",
   "problem": "The plan says each question shows its code as highlighted text. JupyterLab does not highlight these blocks. In the page, a ```python run block gets code class 'language-python run' and 0 highlight spans. Ordinary ```python blocks get 'language-python' and 5 to 7 spans. The screenshots show the same: Q1 and Q8 code is plain black, while Q9's 'def end_hour' is coloured. So the question code now looks plainer than the example code next to it. Colab is untested (plan item B2), and its markdown renderer may behave the same way.",
   "fix": "Make B2 the first item on the Colab checklist. If Colab doesn't highlight these blocks either, change the marker so the fence's language is just 'python'. One option: mark run blocks with a ~~~python fence (examples keep ```python). The other: keep ```python and mark the cell with a tag or metadata entry (e.g. \"review\": {\"run\": true}), which the plan already lists as the alternative. Either way, update parse_page, the checks and the site's prep to match."
  },
  {
   "severity": "minor",
   "where": "Q8 Answer prose (cells f164d420, 994fad7b, ff14f9e7) and Q14 (cell 91f14330); check S10 in check_v2.py",
   "problem": "To satisfy check S10, the prose now names each error right before the output names it again: '…so this is a `SyntaxError`:' followed by 'SyntaxError: invalid syntax…'. On the site and in Colab, 'RecursionError' appears three times within about 12 lines of Q14. It's a small echo, but this professor objects to repetition.",
   "fix": "Keep S10's independent record of the intended error, but store it outside the visible prose, e.g. run-cell metadata \"review\": {\"expect\": \"SyntaxError\"} or an HTML comment in the Part cell (it doesn't render in Colab, Jupyter, GitHub or MyST). Then the prose can go back to explaining the cause only, as the original did: '**Part a:** `=` assigns; comparing needs `==`:'. Or keep the current wording if he prefers it."
  },
  {
   "severity": "minor",
   "where": "Q8 summary, cell 9c4ff430",
   "problem": "'Each is found before any of that part's code runs, so nothing is displayed or assigned.' 'Each' has nothing to refer to. The word it stands for ('mistake') is in the question, three tracebacks earlier, so the sentence reads awkwardly.",
   "fix": "'Python finds each of these mistakes before it runs any of that part's code, so nothing is displayed and `x` is never assigned.'"
  },
  {
   "severity": "minor",
   "where": "First line of all 13 hidden run cells",
   "problem": "JupyterLab and Notebook 7 show the hidden input as a grey bar reading '# @title Output { display-mode: \"form\" } •••' (see lab_open_q1_expanded.png). VS Code, GitHub and nbviewer show the same line as a code comment. The '{ display-mode: \"form\" }' part is jargon to students. According to the hidden-code research, Colab's own Hide code command saves '#@title X' with cellView: form and no display-mode (332 such cells in the sample, versus 13 with both). TF docs use cellView alone for notebooks opened from GitHub.",
   "fix": "Use '# @title Output' plus cellView: form and jupyter.source_hidden: true, and drop the display-mode part. Confirm in the Colab check that the code opens hidden. Also check whether Colab's table of contents lists form titles. If it does, there will be 10 identical 'Output' entries, and the titles should be reconsidered."
  },
  {
   "severity": "minor",
   "where": "Help note (cell 78002e85) and intro (cell d9a4998f)",
   "problem": "(1) 'It explains the answer and shows the output of the question's code' is wrong for the six write-a-function questions (Q4, Q9, Q10, Q11, Q15, Q16), whose Answers have no output. (2) 'or the three dots in Jupyter': what Jupyter actually shows is a grey bar starting '# @title …'. (3) The intro says 'The setup cell below' (one cell), but there are two setup cells, and in Colab the help note sits between that sentence and the cells.",
   "fix": "(1) 'For questions about what code displays or draws, it also shows that code's output.' (2) 'click Show code in Colab, or the grey bar in Jupyter'. (3) 'The setup cells below download `jupyturtle`, import those functions, and define a helper the Answers use.' Or move the help note above that sentence."
  },
  {
   "severity": "minor",
   "where": "run_code setup cell 673c9695 (Colab and Jupyter only; removed on the site)",
   "problem": "Students in Colab see a 17-line run_code definition that they never need to read. The intro paragraph that used to explain it was deleted. The page now hides its other helper code, so this cell stands out.",
   "fix": "Put this cell in form view too: '# @title Setup for the Answers' with cellView: form and source_hidden: true. Update check S12's exact text for the managed cell to match."
  },
  {
   "severity": "minor",
   "where": "Q14 (definition cell a4b2ec88, run block 33f25cd5, Answer run cell 2b7f1ccf)",
   "problem": "'What happens with this call?' is now a markdown block, so the student can't run it where it is. 'How would you fix the function?' leaves the visible definition cell as the only place to try a fix. If the student fixes that cell and then uses Run all, the Answer shows 'Blastoff!' directly under '…It ends with a `RecursionError` when there are too many frames on the stack:'. The help note's general warning covers this, but only far away from Q14.",
   "fix": "Add a '# Your code here' cell after the question so students experiment there and not in the definition cell. Or add one line to the question: 'Try your fix in a new cell, so the cell above keeps the original code.'"
  },
  {
   "severity": "minor",
   "where": "GitHub preview, VS Code and nbviewer",
   "problem": "These viewers ignore collapsed headings and hidden code. Each Answer shows open, with the question's code a second time (now with the '# @title …' line) and its saved output. Today's <details> Answers stay closed in GitHub's preview. The plan accepts this and the help note mentions it, but it does give the answers away to anyone who opens the repo link.",
   "fix": "No change needed if the professor accepts it. Make sure the Colab link stays the main way students open the page, and add this to the README guide's known differences."
  }
 ]
}
```
