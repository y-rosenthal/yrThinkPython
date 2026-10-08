# verify:3

```json
{
 "verdicts": [
  {
   "fact_id": "repo.F1",
   "claim": "All six current review pages pass check_review.py unchanged; 103 questions (17/16/19/17/17/17), one <details> Answer per question.",
   "verdict": "confirmed",
   "reasoning": "I re-ran check_review.py on copies of HEAD b389c80 and all six printed OK (verify-repo/logs/orig_*.txt). My own count script on executed copies gives 103 questions with the same per-page split."
  },
  {
   "fact_id": "repo.F2",
   "claim": "After running, 69 of 103 questions show answer-revealing output under the question; the 34 write-code questions show nothing.",
   "verdict": "confirmed",
   "reasoning": "I executed the originals (verify-repo/exorig/). Every non-write-code question has at least one code cell with output, 69 in all. Write-code questions are 4+5+8+6+6+5 = 34. execute_result appears only in ch02 Q4 ('12') and ch03 Q9."
  },
  {
   "fact_id": "repo.F3",
   "claim": "24 cells are tagged raises-exception, 19 of them run_code; 5 plain raising cells; 21 run_code cells in total; the ch06 setup has no run_code.",
   "verdict": "confirmed",
   "reasoning": "Static scan: RX 8/4/6/4/1/1 = 24. The plain raising cells are ch03[54], ch04[48,50], ch05[52] and ch06[51]. run_code cells are 10/3/4/3/0/1 = 21. The ch06 setup has no 'def run_code'."
  },
  {
   "fact_id": "repo.F4",
   "claim": "Run all stops at the first raising cell: ch02 33, ch03 36, ch04 25, ch05 28, ch06 51, ch07 28.",
   "verdict": "confirmed",
   "reasoning": "The first raises-exception cell indices match these numbers. A simulated run of ch05 (nbclient, allow_errors=False, force_raise_errors=True) stopped at cell 28 with 7 visible outputs (logs/vis_orig05.txt). That Colab itself stops there is the professor's observation, not tested here."
  },
  {
   "fact_id": "repo.F5",
   "claim": "A catching run_code yields an 'error' output with correct ename/evalue while nbclient (allow_errors=False) continues; error_line() still matches.",
   "verdict": "confirmed",
   "reasoning": "I tested the prototype's run_cell variant on IPython 9.17 and on IPython 7.34 / Python 3.12. Every page reached the end, the caught errors are 'error' outputs, and the adapted check's error_line comparison passes on all six pages. The exec+showtraceback variant was verified by the other workers, not by me."
  },
  {
   "fact_id": "repo.F6",
   "claim": "Plain exec+showtraceback adds run_code / '<string>' frames; the linecache + tb_next variant gives a clean traceback.",
   "verdict": "plausible",
   "reasoning": "Not re-tested. The prototype dropped this approach for nested run_cell; in my run its traceback for ch03 Q14 has no run_code frame on either IPython version."
  },
  {
   "fact_id": "repo.F7",
   "claim": "exec/run_code loses last-expression display; ch02 Q4 and ch03 Q9 depend on it; check_review never checks execute_result.",
   "verdict": "confirmed",
   "reasoning": "The executed originals show execute_result '12' and '<function __main__.greet()>'. Mutation M2 changed price*3 to price*4 without changing the Answer, and both the original and the adapted check printed OK, so the gap exists in both. In the prototype these two cells are plain cells and show '12' even on IPython 7.34."
  },
  {
   "fact_id": "repo.F8",
   "claim": "ch07 Q14's doctest report is identical through exec and as a plain cell.",
   "verdict": "plausible",
   "reasoning": "Not re-tested, and it does not matter for the prototype: the prototype runs that cell as a plain cell, and its check passes."
  },
  {
   "fact_id": "repo.F9",
   "claim": "groups_of / turtle questions() keep '#### Answer' inside the question group; the credit cell is the last cell and falls into the last group, so a collapsed last Answer would hide it.",
   "verdict": "confirmed",
   "reasoning": "Read the code (check_review L53-63, turtle_images L46-58). The credit cell is the last cell on all six pages. The prototype's 'credits without heading' mutation is caught by the adapted check (I re-ran it)."
  },
  {
   "fact_id": "repo.F10",
   "claim": "is_answer matches a single <details> cell and feeds the answer texts, the question text and the 'no Answer' check; it must become positional.",
   "verdict": "confirmed",
   "reasoning": "Code read. Running the original check on the new chap05 shows the effect: 'no Answer cell' errors, and no standalone .py runs for write-code answers because no answers were found."
  },
  {
   "fact_id": "repo.F11",
   "claim": "Raw '#### Answer' headings land in the page TOC with no warning; a MyST admonition cannot span cells.",
   "verdict": "confirmed",
   "reasoning": "My skew build (new chap05 + the unmodified prep_notebooks.py, verify-repo/jb_skew) gave 17 'Answer' TOC entries and 17 h4, with 'build succeeded' and no warnings. I did not re-test admonitions spanning cells; the prototype avoids the problem by merging the cells."
  },
  {
   "fact_id": "repo.F12",
   "claim": "The website does not execute review pages; process_review drops '# Your code here', converts whole-cell <details>, blanks 'solution'-tagged or '# Solution' code, strips only %%expect.",
   "verdict": "confirmed",
   "reasoning": "Code read: execute_notebooks.py L139 globs only chap*.ipynb from jb/, _config.yml has execute_notebooks 'off', and prep_notebooks.py L62-83 and L162-170 match the description."
  },
  {
   "fact_id": "repo.F13",
   "claim": "Answer pictures in ch04 Q2, Q6, Q7 and ch05 Q17 are drawn from the question's code cell (last_code); there are 23 data-turtle images (22 + 1).",
   "verdict": "confirmed",
   "reasoning": "My static scan finds exactly these four answer images with no python block above them. The image counts are 22 in ch04 and 1 in ch05."
  },
  {
   "fact_id": "repo.F14",
   "claim": "A run_code using get_ipython() without a guard breaks outside IPython; turtle_images would print 'raised NameError: get_ipython'.",
   "verdict": "doubtful",
   "reasoning": "turtle_images discards errors from question code cells (L109) and prints only errors from image code. In the prototype the image code comes from the raw question block, not from the run_code cell. My redraw of the new ch04/ch05 printed no get_ipython message, and the pictures came out byte-identical. The NameError does happen, but nothing is printed and nothing breaks."
  },
  {
   "fact_id": "repo.F15",
   "claim": "Write-code questions have only a '# Your code here' code cell; 30 of 34 show headers (ch02 Q11, Q12, Q16, Q17 tagged no-signature); all show at least 2 examples.",
   "verdict": "confirmed",
   "reasoning": "The no-signature tags are exactly ch02 Q11, Q12, Q16 and Q17. The original check passes all the header and example rules."
  },
  {
   "fact_id": "repo.F16",
   "claim": "Questions use only names from their own cells or setup; the NameError answers rely on nothing earlier defining total / num_letters / jupyturtle.",
   "verdict": "plausible",
   "reasoning": "Consistent with the converted pages passing the checker under Run-all order on both IPython stacks. I did not repeat the static name analysis."
  },
  {
   "fact_id": "repo.F17",
   "claim": "Setup cells print only 'Downloaded …' on first run (ch04, ch05, ch07); this must be exempt from a nothing-visible rule.",
   "verdict": "confirmed",
   "reasoning": "My Run-all simulation of the new ch07 shows exactly one visible output: the setup's 'Downloaded words.txt'. ch04 and ch05 print 'Downloaded jupyturtle.py' only when the file is missing (I pre-copied it)."
  },
  {
   "fact_id": "repo.F18",
   "claim": "review_cells.py builds the old format (the answer kind makes <details>, the skeleton has no run_code, the metadata has no collapse info).",
   "verdict": "confirmed",
   "reasoning": "Code read. The prototype left review_cells.py byte-identical (diff), so the authoring tool still emits the old format, and the adapted check would reject it."
  },
  {
   "fact_id": "repo.F19",
   "claim": "Colab-saved notebooks keep colab.collapsed_sections and store cell ids in metadata.id.",
   "verdict": "plausible",
   "reasoning": "Outside my lens. I inspected the colab-verify/dl copies: eng-edu intro_to_pandas (nbformat 4.0) has collapsed_sections pointing at metadata.id of '### Solution' cells, and lambdamai Pandas_1 (4.5) has top-level id == metadata.id == '36396f4c'."
  },
  {
   "fact_id": "repo.F20",
   "claim": "check_notebooks.py checks JSON, nbformat, unique ids, no outputs, KNOWN_MAGICS, '# Solution' cells, TOC/workflow; nothing about headings or metadata.",
   "verdict": "confirmed",
   "reasoning": "Code read. It prints OK on all six converted pages: the new metadata (colab, jp-MarkdownHeadingCollapsed, metadata.id) is ignored, and no outputs are stored."
  },
  {
   "fact_id": "repo.F21",
   "claim": "build_book.sh and deploy-book.yml only copy yr/*.ipynb and run prep; known_warnings.txt has 4 entries, none from yr/.",
   "verdict": "confirmed",
   "reasoning": "Read both files and known_warnings.txt (4 lines, all from chap01/chap02). There is no check step in CI, so nothing in deploy catches a broken prep (see risks)."
  },
  {
   "fact_id": "repo.F22",
   "claim": "Docs that describe the old format: yr/README.md, the yr-review skills, notebook-conventions L86, run_notebooks.sh L11 (comment only).",
   "verdict": "plausible",
   "reasoning": "The list is correct by grep, and none of these files was updated in the prototype. Correction: run_notebooks.sh is not comment-only. L62 skips error checking only for cells tagged raises-exception. On a new-layout page its logic reports the caught run_code errors as real failures: simulated on ch05, cells 37, 38, 39 and 65."
  },
  {
   "fact_id": "repo.F23",
   "claim": "The EXAMPLE regex can over-count once question code moves into the question markdown.",
   "verdict": "plausible",
   "reasoning": "It is possible in theory: a question block followed later by a ```text block with no python block in between. In practice, the example counts of all 103 questions are identical between the original and the converted pages (measured)."
  },
  {
   "fact_id": "repo.F24",
   "claim": "Parts are checked per cell (exact stdout match); eight questions have parts.",
   "verdict": "confirmed",
   "reasoning": "The per-cell logic is confirmed. The count is 7, not 8: ch02 Q9, Q10, Q14; ch03 Q10; ch04 Q14, Q15; ch05 Q8. The claim's own list also has 7."
  },
  {
   "fact_id": "repo.F25",
   "claim": "ch04 particulars: Q14 part c untagged and showing an empty canvas; Q15 part c message depends on the Python version; Q7 premise; Q18 jump only in markdown.",
   "verdict": "confirmed",
   "reasoning": "RX plain cells are ch04[48,50] (parts a and b); part c is untagged. The adapted check passes on both Python 3.13 and 3.12/IPython 7.34, so the version-dependent message is covered by the substring check. Q7's premise text still says 'and this cell', which is now stale (see risks)."
  },
  {
   "fact_id": "proto.F1",
   "claim": "rsync is missing; review.sh and build_book.sh fail in a copy without .git; Playwright in venv-lab expects chromium_headless_shell-1243 but only the 1194 builds exist. These are likely causes of the worker errors.",
   "verdict": "confirmed",
   "reasoning": "`which rsync` finds nothing. git rev-parse in proto/repo printed 'fatal: not a git repository'. /opt/pw-browsers holds only chromium-1194 and chromium_headless_shell-1194, and the venv has Playwright 1.63. That these caused the 3rd and 4th workers' errors is unverified: no transcripts are visible to me."
  },
  {
   "fact_id": "proto.F2",
   "claim": "Colab collapsed-section format (metadata.colab.collapsed_sections of heading metadata.id; Google's MLCC uses a collapsed '### Solution' heading followed by a code cell).",
   "verdict": "plausible",
   "reasoning": "The format is confirmed from primary files (colab-verify/dl eng-edu intro_to_pandas and lambdamai Pandas_1). The cited proto/dl/intro_to_pandas.ipynb is a '404: Not Found' file; the real copy is in colab-verify/dl. Colab honoring this when opening from GitHub is untestable here."
  },
  {
   "fact_id": "proto.F3",
   "claim": "JupyterLab 4.6.4 opens the converted chap05 with 30 of 79 cells hidden behind 17 buttons.",
   "verdict": "confirmed",
   "reasoning": "Primary evidence: the screenshot out/lab_runall_q8.png shows the '+ N cells hidden' buttons. The arithmetic matches my own count: 17 Answer markdown cells + 13 run cells = 30 of 79."
  },
  {
   "fact_id": "proto.F4",
   "claim": "convert.py converts all six pages mechanically; check_notebooks is OK.",
   "verdict": "confirmed",
   "reasoning": "Re-running convert.py on current HEAD gives output identical to proto/out/all on all six pages, ignoring random ids. check_notebooks.py prints 'OK: 6 notebook(s)', and nbformat.validate passes."
  },
  {
   "fact_id": "proto.F5",
   "claim": "Simulated Colab Run all reaches the end of all six converted pages with no answer output visible (only chap07's setup line); the original chap05 stops at Question 8 with 7 visible outputs. The same holds on IPython 7.34.",
   "verdict": "confirmed",
   "reasoning": "My own runvis.py (allow_errors=False, force_raise_errors=True, visibility from heading sections with any heading outside code fences, setext included) gave REACHED END and 0 visible outputs on all six pages under both the 3.13/IPython 9.17 and 3.12/IPython 7.34/ipykernel 6.17 stacks; ch07's setup is the only visible output. The original ch05 stopped at cell 28 with 7 visible."
  },
  {
   "fact_id": "proto.F6",
   "claim": "run_code = get_ipython().run_cell(code) shows errors with status ok, no run_code frame, and displays a final expression; Colab overrides neither do_execute nor run_cell.",
   "verdict": "confirmed",
   "reasoning": "In the ex13/ex12 runs, ch03 Q14 shows a clean traceback with no helper frame on both IPython versions. grep of proto/dl/colabtools finds only _showtraceback and run_cell_magic overrides. Caveat: on IPython 9 the label is off by one ('Cell In[20]' for prompt [19])."
  },
  {
   "fact_id": "proto.F7",
   "claim": "In JupyterLab, Run All Cells runs the collapsed Answer cells and their outputs stay hidden; expanding shows the real errors.",
   "verdict": "confirmed",
   "reasoning": "Primary evidence: the screenshot lab_runall_q8.png shows 'Cell 79/79' and collapsed Answers. The jupyter worker independently verified the same behavior (Q1-b)."
  },
  {
   "fact_id": "proto.F8",
   "claim": "Shift+Enter stepping in JupyterLab expands collapsed Answers; the current details layout does not.",
   "verdict": "confirmed",
   "reasoning": "The screenshot lab_shift_enter.png shows Question 2's Answer open with run cell [67] executed, and the jupyter worker found the same (Q1-e). Nuance: with the current layout, running the question cell with Shift+Enter already shows the answer output right under the question, so the comparison overstates the regression. Colab behavior is unknown."
  },
  {
   "fact_id": "proto.F9",
   "claim": "The adapted prep makes one collapsed Answer dropdown per section; no h4, no 'Answer' TOC entries, no new warnings.",
   "verdict": "confirmed",
   "reasoning": "I built my own books (verify-repo/jb_new and jb_orig) with zero warnings each. Answer dropdowns are 17/16/19/17/17/17, none shown, 0 h4, 0 'Answer' TOC entries, and the text of every dropdown is identical to the original site. Differences: a 'Credits' TOC entry is added, and question code becomes markdown blocks (ch02 code cells drop from 21 to 1; python block count unchanged)."
  },
  {
   "fact_id": "proto.F10",
   "claim": "The credit cell needs its own heading or it is hidden in the last Answer; '## Credits' fixes it and adds a TOC entry.",
   "verdict": "confirmed",
   "reasoning": "Re-ran the prototype's mutation: 'the last cell is inside the last Answer' is reported. The built pages show the 'Credits' TOC entry."
  },
  {
   "fact_id": "proto.F11",
   "claim": "Answer run cells must be byte-identical to the question code; an added comment line shifts the ch07 Q14 doctest line number and fails the check.",
   "verdict": "plausible",
   "reasoning": "Not re-tested. The mechanism is sound (a def shifted down one line changes the doctest's 'line N'), and the DRY check enforces byte equality anyway."
  },
  {
   "fact_id": "proto.F12",
   "claim": "Guessing the question code fails on refactor questions; the rule 'a question with # Your code here has no Answer code cells' works on all six pages.",
   "verdict": "confirmed",
   "reasoning": "The adapted check enforces exactly this rule and prints OK on all six pages (my runs)."
  },
  {
   "fact_id": "proto.F13",
   "claim": "chap06's setup has no run_code; every page now needs it.",
   "verdict": "confirmed",
   "reasoning": "Static scan of ch06 setup. convert.py appends run_code there, and the converted ch06 reaches the end."
  },
  {
   "fact_id": "proto.F14",
   "claim": "The current tools break on the new layout (check_review reports 18 problems on chap05 and silently skips the write-code .py check; turtle_images misses ch05 Q17). The adapted tools pass all six pages, catch all 10 mutations, and redraw the pictures byte for byte.",
   "verdict": "confirmed",
   "reasoning": "Confirmed: all 10 mutations caught (re-run), all six pass, and the ch04 (22) and ch05 (1) pictures redrawn from blank srcs are identical to the repo. Also: per-question coverage parity (stdout comparisons, error comparisons, standalone blocks, write-code and wrong-call rules) is identical on all six pages. Corrections: the original check reports 15 problems on chap05, not 18. Worse than reported, the original turtle_images run on the new ch04 silently rewrites 19 example pictures with partial NameError drawings."
  },
  {
   "fact_id": "proto.summary.checks-as-strong",
   "claim": "The adapted check keeps every existing check as strong as today.",
   "verdict": "refuted",
   "reasoning": "Mutation M1: ch05 Q8 part a edited consistently, in the question and the run cell, so that it no longer raises, while the Answer still says SyntaxError. The adapted check prints OK; the original flagged 'cell is tagged raises-exception but raised nothing'. Mutation M3: a '#### Note' heading inside an Answer passes the adapted check, yet the run output becomes visible after Run all (runvis: 1 visible output). Files: verify-repo/mut/, logs/mut_*.txt, logs/vis_M3.txt."
  },
  {
   "fact_id": "proto.F15",
   "claim": "Option A: the check fails when the question is edited but the Answer cell is not; sync regenerates the cells; sync is idempotent.",
   "verdict": "confirmed",
   "reasoning": "sync_answers.py reports 0 questions updated on all six pages. I edited Q8 part b's question block: the check failed with the DRY message, sync regenerated 3 cells, and the check then printed OK. Caveat: the message tells authors to run 'review_cells.py sync', a subcommand that does not exist."
  },
  {
   "fact_id": "proto.F16",
   "claim": "Option B runs to the end and gets 0 Pyright problems, but reads as a one-colour string and the site shows q8a = \"\"\".",
   "verdict": "plausible",
   "reasoning": "Not re-run; the screenshots exist."
  },
  {
   "fact_id": "proto.F17",
   "claim": "Option C': plain Pyright flags the %%magic line, the hidden syntax error, and the undefined q8a.",
   "verdict": "confirmed",
   "reasoning": "Local Pyright: c_magic.py gives 'Expected expression' (line 1) and 'Expected \":\"' (line 3), and c_answer.py gives '\"q8a\" is not defined'. Note that run_code itself is reported undefined in standalone files, so a per-cell Pyright document in Colab would also flag option A's run cells (hidden, and only with type checking on)."
  },
  {
   "fact_id": "proto.F18",
   "claim": "The very long RecursionError traceback is pre-existing on IPython 9; IPython 7.34 shortens it.",
   "verdict": "confirmed",
   "reasoning": "Measured: run_code on IPython 9.17 gives 6789 lines, the original plain cell 6852 lines, and IPython 7.34 18 lines."
  },
  {
   "fact_id": "jupyter.Q2-h",
   "claim": "check_review's rule 'an error output in an untagged cell is a problem' fires for untagged run_code cells that show a caught error.",
   "verdict": "confirmed",
   "reasoning": "The original check on the new ch05 reported 'code cell raised SyntaxError ... (tag it raises-exception if intended)' for the three Q8 cells and for Q14."
  },
  {
   "fact_id": "jupyter.Q3-a",
   "claim": "Toolchain versions: jupyter-book 1.0.4.post1, myst-nb 1.4.0, Sphinx 7.4.7, etc.; review pages are not executed.",
   "verdict": "confirmed",
   "reasoning": "Confirmed with pip list in /root/.venvs/yrThinkPython, and _config.yml has execute_notebooks 'off'."
  },
  {
   "fact_id": "jupyter.Q3-b",
   "claim": "myst-nb ignores jp-MarkdownHeadingCollapsed; raw '#### Answer' headings become TOC entries without warnings.",
   "verdict": "confirmed",
   "reasoning": "jb_skew build: 17 TOC 'Answer' entries, 17 h4, Answer text shown openly, and 'build succeeded' with zero warnings."
  },
  {
   "fact_id": "jupyter.Q3-e",
   "claim": "Merging the Answer section into one dropdown keeps 'Answer' out of the page TOC.",
   "verdict": "confirmed",
   "reasoning": "My jb_new build with the prototype's answer_sections has 0 TOC 'Answer' entries and the same dropdown text as today."
  },
  {
   "fact_id": "jupyter.Q4-c",
   "claim": "prep strips only %%expect; check_notebooks rejects unknown cell magics.",
   "verdict": "confirmed",
   "reasoning": "Code read: prep_notebooks.py L74 and check_notebooks.py L18 and L60-64."
  },
  {
   "fact_id": "jupyter.Q2-f",
   "claim": "Nested run_cell swallows KeyboardInterrupt (status ok), so Stop would not halt Run all.",
   "verdict": "plausible",
   "reasoning": "Not re-tested by me. The prototype's run_code (plain get_ipython().run_cell(code)) does not check result.error_in_exec, so if the claim holds, the prototype has this defect."
  },
  {
   "fact_id": "colab.Q3-stream-fallback",
   "claim": "The stderr ANSI-traceback fallback keeps check_review's exact-output comparison working.",
   "verdict": "refuted",
   "reasoning": "Mutation M15: ch05's run_code replaced by the stderr variant, plus a deliberately wrong error text in the Q8 part b Answer. The adapted check printed OK, because it reads only 'error' outputs and that variant produces none, so error answers would silently go unverified. If adopted, the check must parse the last line of the stderr traceback."
  },
  {
   "fact_id": "colab.Q6-heading-sections",
   "claim": "An Answer section ends at the next heading of the same or higher level, so Answer content must not contain headings at #### level or above.",
   "verdict": "plausible",
   "reasoning": "This matches JupyterLab semantics, and my M3 mutation shows the consequence. The adapted check does not enforce it; it treats every cell up to the next '### ' as Answer. Colab's parsing is not tested."
  }
 ],
 "overall_risks": [
  "CHECK WEAKENING (verified, M1): the adapted check_review dropped the 'tagged raises-exception but raised nothing' guard. An Answer can claim 'SyntaxError: ...' while the code no longer raises, and the check prints OK; the original check flagged it. Fix without weakening: every 'XxxError:' line in a question's Answer ```text blocks must be produced by an error output of that question's run cells, or mark raising run cells explicitly and check both directions.",
  "VISIBILITY NOT MODELLED (verified, M3): the check takes 'Answer' to mean everything up to the next '### ', but Colab/JupyterLab end a collapsed section at any heading of level 4 or higher, in JupyterLab any heading in a markdown cell, setext included. A '#### Note' inside an Answer passes the check while the run output becomes visible after Run all. Add a visibility pass that follows section semantics: every output-producing code cell except setup must sit under a collapsed heading, and Answer cells may contain no headings.",
  "STDERR FALLBACK WOULD BLIND THE CHECK (verified, M15): if Colab turns out to stop Run all on error outputs and run_code switches to printing tracebacks on stderr, check_review sees no errors and accepts wrong error text. The check must parse stderr tracebacks if that route is taken.",
  "DEPLOY VERSION SKEW (verified): new notebooks with the old prep_notebooks.py publish every answer openly on the website, plus 17 'Answer' TOC entries per page. jb build succeeds with zero warnings, and CI (deploy-book.yml) runs no check. The old turtle_images on the new ch04 silently rewrites 19 example PNGs with partial NameError drawings. Notebooks, prep_notebooks.py, check_review.py, turtle_images.py and review_cells.py must ship in one commit. Add a guard, e.g. prep or check_notebooks fails if a '#### Answer' heading or a code cell under it survives prep.",
  "AUTHORING WORKFLOW NOT PROTOTYPED: review_cells.py is unchanged. 'add' still emits <details> Answers (rejected by the new check); the skeleton lacks run_code, the Credits heading and colab metadata; there is no 'sync' subcommand, although the new check's message tells authors to run 'review_cells.py sync'. yr/README.md, the yr-review-page, yr-review-questions and notebook-conventions skills still document the old format. Expanding an Answer in JupyterLab/Colab and saving drops or changes the collapse metadata (Colab also saves outputs and metadata.id on every cell), so a normalize/recollapse command is needed. The check catches it, but authors would face constant friction.",
  "STALE PAGE TEXT (verified by scan): ch02 Q9 'For each cell...', ch02 Q14 'Each cell has an error...', ch03 Q10 and ch04 Q14 'For each of the next three cells', ch04 Q7 '...and this cell', ch02 Q4 and ch03 Q9 'this cell', ch07 Q15 'then run it'. ch06's intro got no explanation of collapsed Answers or run_code. The new intro ('cells hidden' button; 'The Answer ends with a code cell...') is shown verbatim on the website, where it is untrue. convert.py's docstring promises part labels before the run cells, but the code discards them, so multi-part Answers have unlabeled run cells.",
  "run_code = nested get_ipython().run_cell(code): (a) per the jupyter worker it swallows KeyboardInterrupt, so Stop will not halt Run all, and the prototype does not re-raise; (b) on IPython 8+ the traceback label is off by one ('Cell In[20]' under prompt [19], observed); (c) pre/post_run_cell hooks fire twice per cell, untested in Colab; (d) run_code(\"\"\"...\"\"\") is not a raw string, so a backslash in question code would change the executed code while the DRY text comparison says equal (none today; use r\"\"\"). Multi-line triple quotes inside question code also need another quote style.",
  "DRY HEURISTIC FRAGILITY: question code = ```python blocks not followed by ```text/img and not matching SIGNATURE (prefix match). A question block followed directly by a ```text block is silently exempted from running, and a block starting with a header stub is skipped whole. sync_answers keeps run_code wrapping by position, so inserting a part shifts which cells get wrapped (fails closed, via the 'Run all stops' error). An explicit marker would be safer. Only the first '#### Answer' per question is checked, so a two-section design (run code, then explanation) needs check changes.",
  "JUPYTERLAB Shift+Enter expands Answers (verified via screenshot); Colab behavior unknown. Note that the current layout also reveals output when the question cell is run, so this is a change in how the reveal is triggered, not purely a regression.",
  "run_notebooks.sh (check-notebooks skill) treats caught run_code error outputs in untagged cells as real failures (simulated on new ch05: 4 cells). It matters only if someone runs it on yr pages, but its comment says the tag logic is for yr pages.",
  "PRE-EXISTING GAPS STAY OPEN: execute_result (ch02 Q4 '12', ch03 Q9) is unchecked by both checks (verified, M2); stderr and display_data are unchecked; write-code examples are never executed against the suggested answer. With the new layout these are easy to add.",
  "COSMETIC/SITE: each page gets a 'Credits' TOC entry; question code moves from code cells into markdown code blocks, losing the cell styling; the setup cell on the site now shows run_code via get_ipython().run_cell on every page, including ch06. Colab's and JupyterLab's TOC sidebars will list 17 'Answer' headings per page. The 'N cells hidden' count reveals only the number of parts.",
  "STILL UNTESTED, BLOCKING (outside this container): whether Colab's Run all stops on an iopub error output whose reply status is ok, whether collapsed_sections with id == metadata.id opens collapsed from GitHub, and whether Colab auto-expands sections during Run all or Shift+Enter. One live Colab test of a pushed prototype page is required before converting six pages.",
  "WORKER 3/4 ERRORS: confirmed environment traps that would make workers fail: rsync is not installed; review.sh and build_book.sh call git rev-parse and fail in copies without .git; Playwright 1.63 in jupyter-facts/venv-lab looks for chromium_headless_shell-1243, but only the 1194 builds exist in /opt/pw-browsers (pass executable_path=/opt/pw-browsers/chromium-1194/chrome-linux/chrome). That these caused the 3rd and 4th workers' errors is unverified, since no transcripts are visible here. Evidence for this verification is in /tmp/claude-0/-home-user-yrThinkPython/6571a165-f8cc-5e43-8b74-c00357a4a6f6/scratchpad/ultra/verify-repo/ (logs/, mut/, runvis.py, jb_new/, jb_orig/, jb_skew/, tt/)."
 ]
}
```
