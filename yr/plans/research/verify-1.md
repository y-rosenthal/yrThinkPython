# verify:1

```json
{
 "verdicts": [
  {
   "fact_id": "colab.Q1-format",
   "claim": "Colab stores collapsed heading sections as notebook-level metadata.colab.collapsed_sections, a list of cell-id strings naming markdown heading cells (metadata.id in Colab-saved files).",
   "verdict": "confirmed",
   "reasoning": "I downloaded and inspected these myself (scratchpad/ultra/colab-verify/dl, script scripts/insp.py): google-deepmind/dm_control tutorial.ipynb (20 ids), google/eng-edu intro_to_ml_fairness (10), intro_to_pandas (3), linear_regression_taxi, numerical_data_bad_values, bioinfkaustin gromacs GROMACS_for_production (3), lambdamai Pandas_1 (nbformat 4.5). Every id resolves to a cell's metadata.id, and the collapsed cells are headings at #, ##, ### and ####. One exception: in dm_control, 1 of the 20 ids points to a non-heading cell ('<!-- Internal installation instructions. -->'). So the list can hold stale or non-heading ids, which Colab presumably ignores. The format itself is settled."
  },
  {
   "fact_id": "colab.Q1-ids-nbformat45",
   "claim": "For nbformat 4.5 notebooks Colab reuses the top-level cell ids as its own ids, writes the same value into metadata.id, and collapsed_sections can hold Jupyter-style ids.",
   "verdict": "plausible",
   "reasoning": "lambdamai Pandas_1.ipynb (nbformat 4.5, which I inspected) has collapsed_sections ['36396f4c'] on a cell where id == metadata.id == '36396f4c'. Across the file there are 40 cells with an 8-hex top-level id equal to metadata.id, 38 cells with an 8-hex top-level id and NO metadata.id, and 20 cells where both are Colab-style 12-char ids. Colab therefore kept nbformat_minor 5 and the top-level ids, and copied the Jupyter id into metadata.id only on cells it touched. That fits Colab using the top-level id when metadata.id is absent, but it also refines the claim: Colab does not write metadata.id on every cell. The BATUTO90 release-notes copy (53/53 equal) is weak evidence, since Colab's own source notebook may already have had both ids. Not tested live. Writing both (metadata.id = id on Answer headings, plus collapsed_sections) remains the safe choice."
  },
  {
   "fact_id": "colab.Q1-github-open-collapsed",
   "claim": "A notebook opened via colab.research.google.com/github/... with collapsed_sections opens with those sections collapsed; Google course material relies on this to hide solution code cells.",
   "verdict": "plausible",
   "reasoning": "Strong but indirect evidence:\n- The gromacs README links each notebook via /github/, and the notebook's own collapsed heading text says 'Please click ↳ cells hidden below'.\n- dm_control is linked via /github/ (link found inside the file) and ships 20 collapsed sections.\n- Issue #438 (WebFetch): 'I can get sections to start collapsed by editing the collapsed_sections metadata in the raw ipynb file'.\n- New evidence: a saved Colab page (colab_20250716 build, fe/colab_page_2025-07.html) has a View-menu command 'Save collapsed section layout', which implies a saved layout is applied on open.\n\nWeaker part of the claim: I could not find a /github/ link for eng-edu prework/intro_to_pandas, the file with collapsed '### Solution' + code cell. Historically it was served from Colab's own /notebooks/mlcc path. The current MLCC exercises mostly use '# @title Solution (run this code block to view)' form cells instead; only numerical_data_bad_values collapses a section ('## Task 5') that holds code cells. Not observed live."
  },
  {
   "fact_id": "colab.Q1-saved-state",
   "claim": "Colab saves the collapsed state whenever it writes the notebook to Drive/GitHub and keeps no separate per-user state.",
   "verdict": "doubtful",
   "reasoning": "#4162 is verified only for local runtimes, where the state is not saved. #438 (2019) said UI collapsing did not change the metadata. Colab's 2025-07 menu has an explicit 'Save collapsed section layout' command (View menu, next to 'Collapse sections Ctrl+]' and 'Expand sections Ctrl+['), which suggests the layout is written by that command rather than on every save. Either way it is harmless for students. But if the professor edits a page in Colab and saves, the layout may be changed or dropped. The repo tools should re-assert and lint the collapsed metadata instead of trusting Colab saves."
  },
  {
   "fact_id": "colab.Q2-run-all-collapsed",
   "claim": "Runtime > Run all executes code cells inside collapsed sections.",
   "verdict": "plausible",
   "reasoning": "I re-downloaded GROMACS_for_production.ipynb. It collapses '#### Input' (a %%bash code cell) and '#### Installation' (2 code cells), and cell 6 says 'run the notebook by clicking *Runtime -> Run all*'. The notebook could not work if Run all skipped those cells. The 'N cells hidden' row has its own run button (#2990, verified via WebFetch). Not tested live."
  },
  {
   "fact_id": "colab.Q2-outputs-hidden",
   "claim": "A collapsed section hides its whole cells including outputs, showing only the heading plus a '↳ N cells hidden' row.",
   "verdict": "plausible",
   "reasoning": "Independent course notebooks (DS2002 Lab 1, via GitHub code search) say: 'some sections might be hidden (collapsed), showing only the title of the section with a \"↳ # cells hidden\" note beneath it ... expand ... Ctrl+['. #2990 is consistent with this. Outputs belong to their cells, so they are hidden too; this is inferred, not observed. The 2026 UI redesign could have changed the presentation."
  },
  {
   "fact_id": "colab.Q2-auto-expand-risk",
   "claim": "Keyboard navigation into a collapsed section (Down-arrow, possibly Shift+Enter) expands it; behavior during Run all is unknown.",
   "verdict": "plausible",
   "reasoning": "#171 (May 2018, closed) says verbatim 'Collapsed sections currently expand when down-arrowing over them' (WebFetch). Whether that is still true, and what Shift+Enter does, is unknown. I found no issue about Run all expanding sections. JupyterLab does expand on Shift+Enter (prototype F8), so the same in Colab is a live risk. Ctrl+[ also expands all sections at once (menu label verified)."
  },
  {
   "fact_id": "colab.Q3-run-all-stops",
   "claim": "Colab's Run all stops at the first cell whose execution fails.",
   "verdict": "confirmed",
   "reasoning": "Three independent sources:\n- The professor's direct observation.\n- Colab pins ipykernel==6.17.1 and ipython==7.34.0 (colabtools setup.py and googlecolab/backend-info pip-freeze.txt, both fetched). In ipykernel 6.17.1 kernelbase.py:756, a reply with status 'error' plus stop_on_error calls _abort_queues().\n- My own test on that exact stack (venv-ipy7; scripts/queue_test.py) queued all requests at once, the way a Run all does. The uncaught `1/0` returned 'error' and the next queued cell came back 'aborted'.\n\nColab's Kernel subclass overrides no execute path (google/colab/_kernel.py, read)."
  },
  {
   "fact_id": "colab.Q3-raises-exception",
   "claim": "Colab does not honor the raises-exception tag and has no cell-tag UI.",
   "verdict": "plausible",
   "reasoning": "Supporting evidence:\n- In the repo, the first raising cell on every page is tagged raises-exception (checked: ch02 cell 33, ch03 36, ch04 25, ch05 28, ch06 51, ch07 28). The professor saw Run all stop at the first raising cell.\n- The saved Colab page (build colab_20250716) has the experiment flag \"cell_tags\": false.\n- Its full menu list contains no tag or 'continue on error' option (Runtime menu: Run all, Run before, Run the focused cell, Run selection, Run cell and below, Interrupt, Restart and run all).\n\nThe frontend source is closed, so this is not proven."
  },
  {
   "fact_id": "colab.Q3-showtraceback-colab",
   "claim": "run_code that catches and calls showtraceback() gives an iopub 'error' output with execute_reply status 'ok' in Colab; whether Colab's frontend stops Run all on error-type outputs is unknown.",
   "verdict": "plausible",
   "reasoning": "Kernel side confirmed by me. colabtools _shell.py:101-137 overrides _showtraceback, which calls _send_error and sends an iopub 'error'; Shell does not override run_cell. On IPython 7.34.0/ipykernel 6.17.1 with queued requests, run_code+showtraceback (SyntaxError, NameError) and nested run_cell (ZeroDivisionError) returned 'ok', and the next queued cells ran.\n\nFrontend still unknown. The 2025-07 Colab page shows \"server_execution_queue\": true and \"execution_status_propagation\": true. Colab may therefore manage the Run-all queue outside the kernel, and may show or propagate error status (for example a red run icon, #3810) based on outputs. That needs the live test."
  },
  {
   "fact_id": "colab.Q3-stream-fallback",
   "claim": "Printing the ANSI traceback to stderr gives only a stream output and status ok, so nothing can stop Run all; check_review's exact-output comparison can be kept.",
   "verdict": "doubtful",
   "reasoning": "The mechanism is confirmed. I re-ran it on IPython 7.34/ipykernel 6.17.1: the only output was [('stream','stderr','\\x1b[0;31m----...NameError')] with status ok, and the next cell ran.\n\nThe impact statement is wrong. check_review.py (lines ~101-122, read) builds errors only from outputs with output_type == 'error' and stdout only from name == 'stdout'. With the stderr variant, every error would vanish from its view, so 'raises X but the Answer does not show it' and the raises-exception tag rules would silently stop checking. Using it needs a check_review change, for example parsing a marked stderr traceback, to keep the checks strong."
  },
  {
   "fact_id": "colab.Q4-engine",
   "claim": "Colab diagnostics come from Pyright on the runtime VM behind Colab's language_service proxy; the editor is Monaco.",
   "verdict": "confirmed",
   "reasoning": "GitHub code search found multiple real Colab VM 'ps' dumps: catafest/colab_google, kwmullet/sample-Google-Colab, lkk688/edgeAI, brendanpshea COMP1150. They show '/usr/colab/bin/language_service ... -- node /datalab/web/pyright/pyright-langserver.js --stdio'. The release notes mirror has 2022-01-28 'Python LSP support ... code diagnostics', 2023-06-02 'Upgraded to Monaco Editor Version 0.37.1' and 2024-06-18 'Reduced latency for LSP'. Because diagnostics run on the VM, they presumably need a connected runtime (inference)."
  },
  {
   "fact_id": "colab.Q4-setting",
   "claim": "Tools > Settings > Editor > Code diagnostics includes 'Syntax and type checking'; type checking is off by default; students on defaults probably see only syntax-error squiggles.",
   "verdict": "plausible",
   "reasoning": "The setting's existence is confirmed through independent 2025/2026 course material found by GitHub code search: ubsuny/PHY386 HW4 (2025 and 2026), panaversity/learn-agentic-ai, jbpost2/ST-554. I found no source for the other option names or the default. The impact statement is weak. Local Pyright 1.1.414 with typeCheckingMode 'off' still reports '\"undefined_name\" is not defined (reportUndefinedVariable)' as a WARNING (colab-verify/pyr/d_plain_runtime.py). Unless Colab's default filters to syntax errors only, undefined names may still be underlined on defaults."
  },
  {
   "fact_id": "colab.Q4-strings-markdown",
   "claim": "Pyright reports nothing inside string literals; markdown cells are not checked.",
   "verdict": "confirmed",
   "reasoning": "Tested locally with Pyright 1.1.414 (pyr/e_string.py). run_code(\"\"\"...if x = 5:...print(undefined_name)...len(1,2)\"\"\") produced no diagnostics inside the string; the only report was 'run_code is not defined', because it was a standalone file. That markdown cells are not sent to Pyright is inferred from LSP design, not observed in Colab."
  },
  {
   "fact_id": "colab.Q4-ignore-comments",
   "claim": "In Pyright a '# type: ignore' before the first statement suppresses all diagnostics including syntax errors; Colab applicability unknown.",
   "verdict": "confirmed",
   "reasoning": "I re-verified this in Pyright 1.1.414:\n- a file-top ignore silences the syntax error (b_fileignore_syntax.py: 0 errors);\n- an ignore after a comment line still works (h_comment_then_ignore.py: 0);\n- an ignore after a statement does not (g_ignore_after_stmt.py: still 'Expected \":\"');\n- a file-top ignore also silences undefined-name and call errors in basic mode.\n\nCOLAB APPLICABILITY IS DOUBTFUL. OSS pyright-langserver opens documents with IPythonMode.None by default (I read onDidOpenTextDocument(e,t=IPythonMode.None) in pyright-internal.js). Colab runs the stock pyright-langserver.js and still resolves names across cells, so its proxy most likely concatenates cells or prefixes earlier cells. A '# type: ignore' at the top of a question cell would then NOT be at file top. Conversely, one at the very top of the first code cell might silence the whole notebook. Both need a live test; don't design around this."
  },
  {
   "fact_id": "colab.Q4-cell-magics",
   "claim": "Colab has handled magics case by case (2022 %%writefile bodies linted, then a fix for 'some magics'); unknown custom %%magic cells show as plain uncolored text; whether their bodies get diagnostics is unknown.",
   "verdict": "plausible",
   "reasoning": "Checked:\n- #2859 (June 2022, WebFetch): 'the syntax checker tries to parse %%writefile cells as Python code'.\n- Release note 2022-07-01: 'Improve LSP handling of some magics, esp. %%writefile'.\n- #4123 (Nov 2023): %%python 'appearing the same as regular text', fixed in 2023-11-27.\n- #4526 (2024): %%writefile with a non-literal path loses highlighting, so highlighting depends on recognizing the magic line.\n- The 2025-07 Colab page shows an \"unsupported_magics_check\": true experiment, so a custom %%question might also draw an 'unsupported magic' warning.\n- Plain Pyright flags both the '%%question' line and the hidden syntax error (pyr/f_magic.py).\n\nOption C' therefore carries extra unknowns in Colab."
  },
  {
   "fact_id": "colab.Q5-details",
   "claim": "Colab renders markdown <details><summary> as a working collapsible.",
   "verdict": "confirmed",
   "reasoning": "This is the professor's own observation (screenshot), and the current review pages rely on it in Colab. I accept it as primary evidence from the user."
  },
  {
   "fact_id": "colab.Q5-forms",
   "claim": "Form cells ('# @title ... { display-mode: \"form\" }') hide only the code; cellView metadata is optional; output is always shown.",
   "verdict": "plausible",
   "reasoning": "The Colab Forms doc copies I found (phihung/ipyform colab_offical.ipynb, wgong/py4kids Forms.ipynb) say: 'You can see both code and the form, just the form, or just the code', and nothing about hiding output. Google's own MLCC exercises (numerical_data_bad_values, numerical_data_stats) use '# @title Task N: Solution (run this code block to view) { display-mode: \"form\" }' with metadata only {'id': ...}, no cellView. That confirms cellView is optional and that the solution is revealed by the cell's OUTPUT when it runs, so Run all would reveal it. 'No form mode hides output' is a negative, inferred claim."
  },
  {
   "fact_id": "colab.Q5-output-toggle-2026",
   "claim": "Colab's 2026 UI has a per-cell output collapse toggle; persistence and metadata support unknown.",
   "verdict": "plausible",
   "reasoning": "The toggle predates 2026. The 2025-07 Colab page's View menu already has 'Show/hide output Ctrl+M O' (command toggle-output). I found no evidence that Colab persists it or reads jupyter.outputs_hidden/collapsed on load. Colab-saved notebooks with 'collapsed': true or outputs_hidden exist on GitHub, but they look like Jupyter-edited files. Still an unproven alternative."
  },
  {
   "fact_id": "colab.Q6-heading-sections",
   "claim": "Sections come from markdown cells starting with a heading (seen at ##, ###, ####; leading blank line OK); a section runs to the next heading of the same or higher level; collapsed shows '↳ N cells hidden'.",
   "verdict": "plausible",
   "reasoning": "What I saw in the inspected files:\n- Collapsed headings at # (dm_control '# Imports'), ##, ### and #### (fairness, gromacs).\n- A collapsed cell whose source starts with a newline: pytorch_HMM '\\n#### *Why?*'.\n- gromacs '#### Documentation' is followed by three '#####' cells and then '#### Configuration'; its 'click ↳ cells hidden ... to show the documentation' text implies the ##### cells nest inside.\n\nSection extent is inferred from such author text, not observed live."
  },
  {
   "fact_id": "colab.Q6-colab-ui-change",
   "claim": "Colab launched a redesigned UI in January 2026, so older UI wording may differ.",
   "verdict": "confirmed",
   "reasoning": "I fetched the mirrored release notes (MdShajalalsojib/Gub_project Colaboratory_Release_Notes.ipynb). The 2026-01-20 entry reads 'Launched a new modern design for the Colab UI.' The same entry says Colab is now available in VS Code, Antigravity, Cursor and Windsurf, which matters for the collapse approach (see risks)."
  },
  {
   "fact_id": "jupyter.Q2-a",
   "claim": "Catching + showtraceback gives an error output with status ok on IPython 7.34.0/ipykernel 6.17.1 (a Colab-like stack), so Run all continues.",
   "verdict": "confirmed",
   "reasoning": "I verified that this is Colab's actual pinned stack: colabtools setup.py has 'ipykernel==6.17.1', 'ipython==7.34.0'; backend-info pip-freeze.txt has ipykernel==6.17.1, ipython==7.34.0, jupyter_client==7.4.9. I reproduced the result with requests QUEUED (closer to a Run all than nbclient's one-at-a-time): status ok, and the next queued cells ran. Colab's FRONTEND reaction remains untested."
  },
  {
   "fact_id": "jupyter.Q2-d",
   "claim": "run_code via get_ipython().run_cell(code) shows normal-looking errors with status 'ok' on IPython 7.34 and 9.17.",
   "verdict": "plausible",
   "reasoning": "I confirmed the status part on 7.34/6.17.1: run_code2 calling ip.run_cell gave an 'error' output (ZeroDivisionError) with reply 'ok', and the next queued cell ran. I did not re-check that the formatting matches a normal cell. Colab's live runtime may be Python 3.13 (backend-info os-info.txt now says 'Python 3.13.16' on Ubuntu 24.04; the pinned 2026.07 runtime is Python 3.12.13). Neither venv tested IPython 7.34 on Python 3.13."
  },
  {
   "fact_id": "jupyter.Q1-c",
   "claim": "Outside Colab the raises-exception tag makes Run All continue; Colab is said to ignore it (not verified).",
   "verdict": "plausible",
   "reasoning": "I did not re-verify the JupyterLab part (not my lens). On Colab, see colab.Q3-raises-exception: the professor's observation on tagged cells, plus the \"cell_tags\": false flag and the absence of any tag UI in the 2025-07 Colab page."
  },
  {
   "fact_id": "jupyter.Q1-f",
   "claim": "VS Code ignores collapsed-heading metadata, so answers show expanded there.",
   "verdict": "plausible",
   "reasoning": "Not re-verified (source-read claim). New Colab-lens relevance: the 2026-01-20 release note says Colab runtimes are available inside VS Code, Antigravity, Cursor and Windsurf. Students using 'Colab in VS Code' would get Colab's kernel but VS Code's notebook UI, with no collapsed sections."
  },
  {
   "fact_id": "jupyter.Q4-a",
   "claim": "A %%question cell magic stores the body without running it; whether Colab lints inside %%magic cells is unknown.",
   "verdict": "plausible",
   "reasoning": "I did not re-run the IPython part. On Colab: plain Pyright flags the magic line and the body's syntax errors (my pyr/f_magic.py: 'Expected expression' at line 1 and 'Expected \":\"' at line 3). Colab linted %%writefile bodies in 2022 (#2859). The 2025-07 page has an 'unsupported_magics_check' flag. The risk is real and untested."
  },
  {
   "fact_id": "jupyter.X-colab-meta",
   "claim": "Colab stores collapsed sections in notebook-level metadata.colab.collapsed_sections as heading cells' Colab ids; dm_control's 20 ids all match markdown heading cells.",
   "verdict": "confirmed",
   "reasoning": "I fetched dm_control tutorial.ipynb: 20 ids, all matching cells by metadata.id. Small correction: 19 are headings and 1 ('YkBQUjm6gbGF') is a non-heading '<!-- Internal installation instructions. -->' markdown cell. The format is confirmed."
  },
  {
   "fact_id": "repo.F4",
   "claim": "Colab Run all stops at the first raising cell on each page (ch02 33, ch03 36, ch04 25, ch05 28, ch06 51, ch07 28).",
   "verdict": "plausible",
   "reasoning": "I confirmed that those cell indices are the tagged raising cells in the current repo. The kernel-side stop is verified on Colab's pinned ipykernel (queue abort test). Whether Colab stops at exactly those cells also depends on its frontend ignoring the tag, which the professor's observation supports."
  },
  {
   "fact_id": "repo.F19",
   "claim": "A Colab-saved notebook stores each cell's id in metadata.id, not in the nbformat 4.5 top-level id.",
   "verdict": "doubtful",
   "reasoning": "This holds only for nbformat 4.0 files like colab-github-demo.ipynb, which cannot have top-level ids. For nbformat 4.5, the Colab-saved lambdamai Pandas_1.ipynb keeps nbformat_minor 5 and the top-level ids on all cells. 38 cells have only the top-level id; the cells Colab touched got metadata.id equal to the top-level id. So Colab keeps top-level ids and mirrors them into metadata.id; it does not replace them."
  },
  {
   "fact_id": "prototype.F1",
   "claim": "rsync is not installed; build/review scripts fail in copies without .git; Playwright in venv-lab expects a browser build that is not installed. Likely causes of earlier worker failures.",
   "verdict": "plausible",
   "reasoning": "Environment facts I verified: `which rsync` gives nothing; /opt/pw-browsers holds only chromium-1194 and chromium_headless_shell-1194, while venv-lab has playwright 1.63.0, which expects a newer build. A further trap I hit myself: `gh api` and curl to github.com for repos not attached to the session return 403 'GitHub access to this repository is not enabled for this session' (googlecolab/colabtools issues). WebFetch to github.com and raw.githubusercontent.com do work. Whether any of this caused the 3rd/4th workers' errors cannot be confirmed without their transcripts."
  },
  {
   "fact_id": "prototype.F2",
   "claim": "Colab collapsed_sections format is settled, and Google's MLCC uses the proposed pattern (collapsed '### Solution' heading followed by a solution code cell).",
   "verdict": "plausible",
   "reasoning": "The format is confirmed (see colab.Q1-format), and intro_to_pandas does have '### Solution ... Click below for a solution.' followed by a code cell. But I found no /github/ Colab link for that prework notebook. The current /github/-linked MLCC exercises mostly hide solutions in form cells ('run this code block to view'). numerical_data_bad_values does collapse '## Task 5' over 2 code cells."
  },
  {
   "fact_id": "prototype.F5",
   "claim": "A simulated Colab Run all (nbclient allow_errors=False, tags ignored) reaches the end of all six converted pages with no answer output visible.",
   "verdict": "plausible",
   "reasoning": "It is a simulation. My own queued-request test on Colab's exact kernel versions agrees on the kernel side. Colab's frontend handling of error outputs with status ok, and its rendering of collapsed sections after execution, are not tested."
  },
  {
   "fact_id": "prototype.F6",
   "claim": "Colab's Kernel and Shell classes override neither do_execute nor run_cell; Colab overrides _showtraceback to send an iopub 'error'.",
   "verdict": "confirmed",
   "reasoning": "I read google/colab/_kernel.py and _shell.py from colabtools main (fetched to colab-verify/colabtools). Kernel overrides only _shell_class_default, do_inspect, complete_request and inspect_request. Shell overrides _send_error, _showtraceback (adds optional error_details) and run_cell_magic (only for an empty-body case), not run_cell."
  },
  {
   "fact_id": "prototype.F8",
   "claim": "In JupyterLab, Shift+Enter steps into and expands collapsed Answers; Colab untested.",
   "verdict": "plausible",
   "reasoning": "JupyterLab was not re-tested (not my lens). For Colab, the only primary evidence is #171 (2018): Down-arrow expands collapsed sections. Treat accidental expansion during keyboard stepping as likely until disproven live."
  },
  {
   "fact_id": "prototype.F17",
   "claim": "Plain Pyright flags the %%question magic line, the hidden syntax errors, and 'q8a is not defined' in Answer cells.",
   "verdict": "confirmed",
   "reasoning": "Reproduced the first two with Pyright 1.1.414 (pyr/f_magic.py): 'Expected expression' at the %% line and 'Expected \":\"' at the 'if x = 5' line. Whether Colab's proxy hides magic bodies first is unknown."
  }
 ],
 "overall_risks": [
  "Highest-priority unknown: Colab's FRONTEND may react to an iopub 'error' output even when execute_reply is 'ok'. The kernel side is verified on Colab's exact pinned stack (ipykernel 6.17.1, IPython 7.34.0): queued cells continue after run_code/showtraceback and after nested run_cell, and are aborted after an uncaught error. The 2025-07 Colab build has server_execution_queue=true and execution_status_propagation=true, so the queue may be run, and error status shown, outside the kernel. Test live before rollout: open a run_code+showtraceback cell followed by print('end') from a branch via /github/ and use Run all.",
  "If the stderr-traceback fallback is ever adopted, check_review.py must be changed. Today it reads only 'error' outputs and stdout streams, so stderr tracebacks would silently disable the 'Answer shows the error' check and the raises-exception tag rules. That is a weakened check, which the professor forbids.",
  "Possible giveaway via status badges: a red run icon or error status (#3810), or status propagation to a collapsed section's header or '↳ N cells hidden' row, could reveal which Answers contain errors without opening them. The hidden-cell count itself (e.g. 2 vs 4 cells hidden) is also a weak hint. Check both live.",
  "Collapsed-on-open is strongly supported but not observed live. Write collapsed_sections AND copy each Answer heading's id into metadata.id; Colab does exactly this for nbformat 4.5 files (lambdamai example). Also write jp-MarkdownHeadingCollapsed for JupyterLab. review_cells.fresh_id and the lint tools must create and allow metadata.id, and a check should fail if an Answer heading is not collapsed.",
  "Collapsed layout is fragile when edited in Colab. Colab has an explicit 'View > Save collapsed section layout' command, and #438 says UI collapse changes were not saved, so editing and saving a page in Colab can change or drop the layout. Re-assert it with tooling instead of trusting Colab.",
  "Accidental reveal by navigation: Down-arrow expanded collapsed sections (#171, 2018); Shift+Enter does so in JupyterLab and is untested in Colab; Ctrl+[ expands all sections. Students stepping through after Run all could see live answers.",
  "The collapse approach hides nothing outside Colab and JupyterLab. That includes 'Colab in VS Code/Cursor/Antigravity' (release note 2026-01-20), where VS Code's UI ignores collapsed_sections.",
  "Squiggles: putting the question code in markdown (option A) is the only approach that avoids them for certain. Per-cell '# type: ignore' is unlikely to work in Colab: OSS pyright-langserver opens documents with IPythonMode.None, and cross-cell name resolution implies Colab concatenates or prefixes cells, so a cell's first line is not file-top. Pyright with type checking 'off' still WARNS on undefined names, so defaults may underline NameError answers if they appear in code cells.",
  "A custom %%question magic (option C') is risky in Colab. Colab linted %%writefile bodies in 2022, shows unknown magics as plain text, has an 'unsupported_magics_check' flag, and plain Pyright flags both the magic line and the hidden syntax error.",
  "Runtime drift between the checker and Colab. Colab runs IPython 7.34 tracebacks ('<ipython-input-N-...>' format), and the live image appears to be moving to Python 3.13.16 on Ubuntu 24.04, while the pinned 2026.07 runtime is Python 3.12.13. The static ```text answers come from a Python 3.13 / IPython 9 venv. Live outputs inside an Answer can differ from the static text next to them, for example in version-specific messages like \"Did you mean 'sides'?\". Also run check_review under the existing IPython 7.34/ipykernel 6.17.1 venv (scratchpad/ultra/jupyter-facts/venv-ipy7) and compare error last-lines only.",
  "Colab's table-of-contents sidebar will list every '#### Answer' heading. The credit cell needs its own heading or it is swallowed by the last Answer.",
  "Older UI evidence ('↳ N cells hidden', menu labels, Settings > Editor > Code diagnostics) predates the 2026-01-20 redesign. One live Colab smoke test of the prototype is needed before converting all six pages. I could not reach colab.research.google.com, medium.com or zenn.dev from here.",
  "About the user's question on worker errors: environment traps I verified are no rsync, a Playwright 1.63 install that expects a browser build absent from /opt/pw-browsers (only chromium-1194), git rev-parse failing in copied repos, and gh/curl GitHub API calls for repos not attached to the session returning 403 'GitHub access to this repository is not enabled' (WebFetch to github.com still works). Whether these caused the 3rd and 4th workers' errors needs their transcripts."
 ]
}
```
