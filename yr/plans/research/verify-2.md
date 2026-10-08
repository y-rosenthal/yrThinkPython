# verify:2

```json
{
 "verdicts": [
  {
   "fact_id": "jupyter:Q1-a",
   "claim": "JupyterLab 4 and Notebook 7 save a collapsed heading as cell metadata jp-MarkdownHeadingCollapsed: true, read it on load, and hide everything up to the next heading of the same or higher level.",
   "verdict": "confirmed",
   "reasoning": "Source: jupyterlab v4.6.4 packages/cells/src/widget.ts:152 defines the constant; about line 2149 reads it on load; the setter at 2244-2248 sets or deletes it. Browser test: I ran my own headless JupyterLab 4.6.4 on port 8912 with verify-jupyter/lab/root/v.ipynb. It opened with cells 4,5 / 8,9 / 12 hidden and headings 3, 7 and 11 collapsed. A '## Credits' heading ended the last section. I did not re-test Notebook 7; it uses the same @jupyterlab cells and notebook packages."
  },
  {
   "fact_id": "jupyter:Q1-b",
   "claim": "Run All executes cells inside collapsed headings; the cells and their outputs stay hidden afterwards; the last cell inside a collapsed section was not expanded either.",
   "verdict": "confirmed",
   "reasoning": "Reproduced in my browser test. After notebook:run-all-cells, the hidden cells got counts 2, 3 and 4, with outputs error:SyntaxError, error:ZeroDivisionError and the stream, and stayed hidden:true. The cell after '## Credits' ran (count 5). runAll passes notebook.widgets to Private.runCells (actions.tsx:940-965). I did not reproduce the last-cell sub-claim. runAll sets activeCellIndex to the last cell, and notebook-extension wires activeCellChanged to expandParent (index.ts:2636-2638), so by the source that sub-claim looks fragile. A '## Credits' heading makes it moot."
  },
  {
   "fact_id": "jupyter:Q1-c",
   "claim": "JupyterLab, Notebook 7, classic Notebook and VS Code honor raises-exception during Run All (stop_on_error=false).",
   "verdict": "confirmed",
   "reasoning": "In jupyterlab v4.6.4 packages/outputarea/src/widget.ts:981-987, the raises-exception tag sets stopOnError=false. In nbclassic codecell.js:340-343 I fetched the same logic; the worker's own saved classic_codecell.js is only a 14-byte '404: Not Found' page, but the citation is right. vscode-jupyter cellExecutionQueue.ts:246-253 sets cellErrorsAllowed for the tag. Kernel side: ipykernel 7.4.0 kernelbase.py:925 and 6.17.1 kernelbase.py:756 abort the queue only when status=='error' and stop_on_error."
  },
  {
   "fact_id": "jupyter:Q1-d",
   "claim": "In JupyterLab and Notebook 7, Run All continues past an untagged cell that shows a traceback but returns status 'ok'.",
   "verdict": "confirmed",
   "reasoning": "My browser test used untagged run_code cells built on nested run_cell (a SyntaxError and a 1/0). Run All continued to the last cell. cellexecutor.ts:103 treats reply.content.status==='ok' as success. I tested the run_cell variant; the worker tested exec+showtraceback. Both return status ok (see Q2-a)."
  },
  {
   "fact_id": "jupyter:Q1-e",
   "claim": "Shift+Enter (run-cell-and-select-next) onto/through a collapsed Answer heading expands it; arrow-down skips collapsed sections.",
   "verdict": "confirmed",
   "reasoning": "Independently reproduced with real Shift+Enter key presses starting at the setup cell. Press #2 made the collapsed '#### Answer' heading active, still collapsed. Press #3 moved active to cell 4, and the section was no longer hidden (hidden list went from [4,5,8,9,12] to [8,9,12]). Source: runAndAdvance does activeCellIndex++ (actions.tsx:814-856) → expandParent. selectBelow skips isHidden cells."
  },
  {
   "fact_id": "jupyter:Q1-f",
   "claim": "VS Code ignores jp-MarkdownHeadingCollapsed (folding is view state), so answers open expanded there.",
   "verdict": "plausible",
   "reasoning": "I grepped the worker's clones of microsoft/vscode (d2a9268) and vscode-jupyter (src/, extensions/) for 'HeadingCollapsed' and 'jp-Markdown' and found nothing, which supports the claim. I did not run VS Code."
  },
  {
   "fact_id": "jupyter:Q1-g",
   "claim": "Plain JupyterLab 4.6 has no editor linting/squiggles.",
   "verdict": "plausible",
   "reasoning": "In v4.6.4 packages/codemirror/package.json there is no 'lint' dependency. But JupyterLab 4 ships the jupyter_lsp server extension; my lab.log shows 'jupyter_lsp | extension was successfully linked'. A JupyterHub that also installs jupyterlab-lsp plus pylsp or pyright would show diagnostics. So this holds for default installs only."
  },
  {
   "fact_id": "jupyter:Q2-a",
   "claim": "exec + catch + get_ipython().showtraceback() gives an 'error' output with execute_reply status 'ok' and nbclient (allow_errors=False) continues, on IPython 9.17 and on 7.34/ipykernel 6.17.1.",
   "verdict": "confirmed",
   "reasoning": "I re-ran it in verify-jupyter/k/mk.py with an on_cell_executed hook that records the reply status. rc_show_* cells gave status=ok with an error output on both stacks (out_ipy9.txt, out_ipy7.txt). nbclient's _check_raise_for_error (client.py:899-918) raises only when the reply status is 'error'."
  },
  {
   "fact_id": "jupyter:Q2-b",
   "claim": "Syntax error via exec+showtraceback shows 'File <string>:3' (IPython 9) / 'File \"<string>\", line 3' (7.34), the same caret and message, and a line number one higher; the current uncaught form shows a noisy traceback through interactiveshell.py.",
   "verdict": "confirmed",
   "reasoning": "Exactly reproduced on both versions (out_ipy9.txt rc_show_syn, out_ipy7.txt rc_show_syn). Uncaught form (k/plain.py): 'Traceback ... File ~/.venvs/.../interactiveshell.py:3823 in run_code ... Cell In[2], line 1 run_code(\"\"\" ... Cell In[1], line 2 in run_code exec(code, globals()) ... File <string>:3'."
  },
  {
   "fact_id": "jupyter:Q2-c",
   "claim": "Runtime errors via showtraceback: IPython 9.17 shows the helper frame plus 'Could not get source' and tb_offset=1 does not remove it; IPython 7.34 hides the helper frame but shows '<string> in <module>' without source.",
   "verdict": "confirmed",
   "reasoning": "Reproduced: rc_show_rt and rc_show_off1_rt (tb_offset=1) on 9.17 both show 'Cell In[1], line 7, in rc_show' and \"'Could not get source, probably due dynamically evaluated source code.'\". On 7.34 they show '<string> in <module>' and '<string> in f(n)' with no source lines."
  },
  {
   "fact_id": "jupyter:Q2-d",
   "claim": "run_code = get_ipython().run_cell(code, store_history=False) makes errors look like a normal cell's on 7.34 and 9.17, status ok, leading blank lines stripped, trailing expression displayed; label 'Cell In[N+1]' on IPython 8+.",
   "verdict": "confirmed",
   "reasoning": "Reproduced. On 7.34, rc_cell_rt is the same format as normal_rt ('/tmp/ipykernel_N/hash.py in <cell line: 0>()'), and the syntax error shows line 2. On 9.17, rc_cell_syn (8th executed cell) printed 'Cell In[9], line 2', which is the N+1 label. rc_cell_expr produced execute_result 12. All status ok. I did not re-test the decrement variant."
  },
  {
   "fact_id": "jupyter:Q2-e",
   "claim": "compile+linecache/cache then showtraceback((etype, value, tb.tb_next)) looks normal on IPython 9 but loses the module frame on 7.34.",
   "verdict": "confirmed",
   "reasoning": "Reproduced with the repo worker's linecache variant (rc_linecache). On 9.17 it is clean ('File <run_code>:5 ----> 5 f(3)'). On 7.34, rc_linecache_rt shows only '<run_code> in f(n)', and rc_linecache_name shows NO frame at all, just 'NameError: ...'. This contradicts repo:F6's recommendation for Colab."
  },
  {
   "fact_id": "jupyter:Q2-f",
   "claim": "Nested run_cell swallows KeyboardInterrupt (status ok), exec with 'except Exception' does not.",
   "verdict": "confirmed",
   "reasoning": "I re-ran it with jupyter_client and a real km.interrupt_kernel() (k/intr.py) on both stacks. Nested run_cell gave ('ok', ['error:KeyboardInterrupt']); exec+catch gave ('error', ...); a plain cell gave ('error', ...). Adding 'if isinstance(r.error_in_exec, KeyboardInterrupt): raise r.error_in_exec' gives status 'error', but prints the KeyboardInterrupt traceback twice (two error outputs). The prototype's run_code does not have this re-raise."
  },
  {
   "fact_id": "jupyter:Q2-g",
   "claim": "Turtle drawings work through exec and nested run_cell (display_data).",
   "verdict": "plausible",
   "reasoning": "Not re-run by me. My nested-run_cell tests show that display and execute_result messages pass through normally, and the prototype's Colab-like Run all (which I re-ran) includes turtle questions and reached the end."
  },
  {
   "fact_id": "jupyter:Q2-h",
   "claim": "check_review runs with allow_errors=True, reads only error outputs, error_line strips ' (file, line N)'; its 'errors and not tagged' rule would fire for untagged run_code cells.",
   "verdict": "confirmed",
   "reasoning": "yr/tools/check_review.py: error_line is at L73-76, allow_errors=True at L93 (not 94), errors come from output_type=='error' at L104, and the rule is at L107. The measured evalues '(<string>, line 3)' and '(445721521.py, line 2)' match my outputs exactly. Consequence: any stderr-stream fallback would make check_review silently skip error checking unless it is updated."
  },
  {
   "fact_id": "jupyter:Q3-a",
   "claim": "Toolchain versions; execute_notebooks 'off'; execute_notebooks.py globs only chap*.ipynb.",
   "verdict": "confirmed",
   "reasoning": "Imports report jupyter-book 1.0.4.post1, sphinx-book-theme 1.3.0, pydata-sphinx-theme 0.17.1, sphinx-togglebutton 0.4.5 and sphinx_design 0.7.0; my build log shows myst v3.0.1, myst-nb v1.4.0 and Sphinx 7.4.7. jb/_config.yml has execute_notebooks: 'off'. jb/execute_notebooks.py:139 is sorted(glob('chap*.ipynb'))."
  },
  {
   "fact_id": "jupyter:Q3-b",
   "claim": "Every heading becomes a right-hand page-TOC entry; repeated '#### Answer' get #answer, #id1 ... with no warning; myst-nb ignores jp-MarkdownHeadingCollapsed.",
   "verdict": "confirmed",
   "reasoning": "My mini book (verify-jupyter/book, repo _config.yml) lists 'toc-h4 #answer' and 'toc-h4 #id1' with no warning for them. A grep of myst_nb, jupyter_book and myst_parser for HeadingCollapsed or collapsed_sections finds nothing."
  },
  {
   "fact_id": "jupyter:Q3-c",
   "claim": "myst-nb parses each markdown cell separately; an unclosed admonition closes at end of its cell, the next code cell renders outside, the stray ':::' becomes an empty div, with no warning.",
   "verdict": "confirmed",
   "reasoning": "myst_nb/core/nb_to_tokens.py:72 calls mdit_parser.parse(nb_cell['source']) once per cell. In my build, Question 3 renders '<div class=\"dropdown admonition\">...opened here</div>', then the code cell outside it, then '<div class=\"docutils\"> </div>'. The only warning in the build was the deliberate H3→H5 one."
  },
  {
   "fact_id": "jupyter:Q3-d",
   "claim": "hide-cell/hide-input/hide-output/remove-* behaviors; mystnb.code_prompt_show/hide relabel; markdown-cell tags do nothing except remove-cell; 'toggle' tag only adds tag_toggle.",
   "verdict": "confirmed",
   "reasoning": "Verified the parts that matter. hide-cell with mystnb {code_prompt_show:'Answer', code_prompt_hide:'Hide answer'} renders '<details class=\"admonition hide above-input\">' with the labels 'Answer' and 'Hide answer'. The toggle tag only adds class 'tag_toggle'. hide-output on an unexecuted cell shows just the input, since there is no output to hide. I did not re-test hide-input, remove-* or markdown-cell tags."
  },
  {
   "fact_id": "jupyter:Q3-e",
   "claim": "Rubric, bold paragraph, or merging into one dropdown keeps 'Answer' out of the page TOC.",
   "verdict": "confirmed",
   "reasoning": "In my build the rubric (Question 6) and the merged single-cell dropdown (Question 7) produced no TOC entries. Prototype build evidence: proto/repo/jb/_build/html/yr/chap05_review.html has 17 dropdown admonitions, only toc-h2 and toc-h3 entries, and no #answer or #idN anchors."
  },
  {
   "fact_id": "jupyter:Q3-f",
   "claim": "H3 directly followed by H5 yields 'Non-consecutive header level increase' warning.",
   "verdict": "confirmed",
   "reasoning": "My build.log: 'v.ipynb:230002: WARNING: Non-consecutive header level increase; H3 to H5 [myst.header]', 'build succeeded, 1 warning'."
  },
  {
   "fact_id": "jupyter:Q3-g",
   "claim": "Review-page code cells use the 'python' Pygments lexer, not ipython3.",
   "verdict": "confirmed",
   "reasoning": "The current jb/_build/html/yr/chap05_review.html has 50 highlight-python, 27 highlight-text and 3 highlight-default blocks, and no ipython3. My mini book with language_info {'name':'python'} also produced highlight-python."
  },
  {
   "fact_id": "jupyter:Q4-a",
   "claim": "A register_cell_magic magic receives a body with a SyntaxError as a raw string and stores it (status ok, no output); running it later via nested run_cell gives normal errors.",
   "verdict": "confirmed",
   "reasoning": "Reproduced on both stacks with magic_use / magic_check. It stored \"x = 5\\nif x = 5:\\n    print('five')\\n\", the magic cell's status was ok, and the later rc_cell showed a normal SyntaxError. Colab's Shell overrides run_cell_magic only to turn a line-only magic into cell=' ' (colabtools _shell.py:216-223), so it does not interfere. Whether Colab's editor lints magic bodies is still unknown."
  },
  {
   "fact_id": "jupyter:Q4-b",
   "claim": "A misspelled or not-yet-registered cell magic gives 'UsageError: Cell magic ... not found.' on stderr and status 'error'.",
   "verdict": "confirmed",
   "reasoning": "Reproduced on both stacks: unknown_magic gave status=error and stream stderr 'UsageError: Cell magic `%%questoin` not found.'"
  },
  {
   "fact_id": "jupyter:Q4-c",
   "claim": "On the site a %%question line would show unless prep strips it (prep strips only %%expect); ipython3 lexer makes the body one Text token; check_notebooks rejects unknown magics.",
   "verdict": "confirmed",
   "reasoning": "jb/prep_notebooks.py:73-74 strips only lines starting with '%%expect'. With the ipython3 lexer the tokens are [Operator '%%', Keyword 'question', Text '<whole body>']; with the python lexer the body is highlighted. check_notebooks.py:18 has KNOWN_MAGICS={%%expect,%%add_method_to,%%expect_error} and line 63 rejects any other magic."
  },
  {
   "fact_id": "jupyter:X-colab-meta",
   "claim": "Colab stores collapsed sections as notebook metadata colab.collapsed_sections listing heading cells' metadata.id.",
   "verdict": "plausible",
   "reasoning": "Outside my lens and not re-checked against GitHub files. I did verify that the prototype pages write collapsed_sections plus matching id == metadata.id plus jp-MarkdownHeadingCollapsed on every Answer heading, on all six pages (17/16/19/17/17/17). Whether Colab honors this when opening from GitHub is still unverified."
  },
  {
   "fact_id": "colab:Q3-run-all-stops",
   "claim": "Colab's Run all stops at the first cell whose execution fails.",
   "verdict": "confirmed",
   "reasoning": "The kernel mechanism is confirmed. colabtools main google/colab/_kernel.py subclasses ipykernel.IPythonKernel and overrides only do_inspect, complete_request and inspect_request. colabtools setup.py pins ipykernel==6.17.1, whose kernelbase.py:756 aborts queued requests when the reply status is 'error' and stop_on_error is set. The frontend behaviour rests on the professor's own observation."
  },
  {
   "fact_id": "colab:Q3-raises-exception",
   "claim": "Colab does not honor the raises-exception tag.",
   "verdict": "plausible",
   "reasoning": "Honoring the tag is a frontend job: JupyterLab and nbclassic set stop_on_error=false themselves (see Q1-c). The professor saw Colab's Run all stop at tagged cells, which fits. There is no source I can inspect for Colab's frontend."
  },
  {
   "fact_id": "colab:Q3-showtraceback-colab",
   "claim": "In Colab, run_code with caught exception + showtraceback emits an iopub 'error' message with reply status 'ok'; whether Colab's frontend stops Run all on error outputs is unknown.",
   "verdict": "plausible",
   "reasoning": "Source confirmed: colabtools _shell.py:101-136 _showtraceback → _send_error → session.send(..., 'error', ...), and neither Kernel nor Shell overrides do_execute or run_cell. Note also that Colab installs a custom handler for ImportError/ModuleNotFoundError (_shell_customizations.py:62-105) that appends a NOTE to the traceback. With nested run_cell it still applies, as in a normal cell. With exec+showtraceback it does not, which matters for ch02 Q14a. The frontend question is genuinely unknown, and nbclient cannot model it: it looks only at reply status (client.py:906)."
  },
  {
   "fact_id": "colab:Q3-stream-fallback",
   "claim": "Printing ip.InteractiveTB.stb2text(structured_traceback(*sys.exc_info())) to stderr yields only a stream output with status ok; traceback text is the same so check_review's comparison can be kept.",
   "verdict": "doubtful",
   "reasoning": "The mechanism is confirmed: only a stderr stream and status ok on both stacks. The rest is wrong. (1) For SyntaxError this form prints only the header and message, with no source line or caret, on both 7.34 and 9.17; on 9.17 runtime errors also show the helper frame and 'Could not get source'. (2) check_review reads only output_type=='error' (L104), so with stderr output every error check would be silently skipped. A better fallback I tested (k/stderr2.py) gives tracebacks identical to normal cells on both stacks, as a stderr stream with status ok: temporarily set ip._showtraceback = lambda et, ev, stb: print(ip.InteractiveTB.stb2text(stb), file=sys.stderr), call ip.run_cell(code), then del the override. check_review would then need to parse the stderr traceback's last line."
  },
  {
   "fact_id": "repo:F5",
   "claim": "Catching run_code (exec + showtraceback) gives an 'error' output with right ename/evalue and nbclient allow_errors=False continues; error_line strips ' (<string>, line N)'.",
   "verdict": "confirmed",
   "reasoning": "Reproduced (rc_show_*, rc_linecache_* status ok with error outputs). The error_line regex r' \\([^()]*, line \\d+\\)$' strips '(<string>, line 3)', '(<run_code>, line 3)' and '(445721521.py, line 2)'."
  },
  {
   "fact_id": "repo:F6",
   "claim": "Registering code in linecache under '<run_code>' and showtraceback((etype, value, tb.tb_next)) gives a traceback that starts at the student's line, like a normal cell; recommended for ch03 Q14.",
   "verdict": "refuted",
   "reasoning": "True only on IPython 9. Colab pins ipython==7.34.0 (colabtools setup.py), and on 7.34 this variant drops the module frame: ZeroDivisionError shows only '<run_code> in f(n)', and a module-level NameError shows no frame at all. That would break exactly ch03 Q14, whose answer is about the order of frames. Line numbers are also shifted by +1 because of the newline after the opening triple quotes. Use nested run_cell instead."
  },
  {
   "fact_id": "repo:F7",
   "claim": "Passing code through exec/run_code loses the last-expression display (ch02 Q4, ch03 Q9); check_review does not check execute_result.",
   "verdict": "confirmed",
   "reasoning": "rc_show_expr, rc_stderr_expr and rc_linecache_expr produced no output for 'price = 4\\nprice * 3'. The nested run_cell variant does produce execute_result 12. check_review L102-104 reads only stdout and error outputs."
  },
  {
   "fact_id": "repo:F9",
   "claim": "groups_of starts groups at '### ' and ends at '# '/'## ', so '#### Answer' stays inside its question group.",
   "verdict": "confirmed",
   "reasoning": "check_review.py:53-63 is as described, and '#### Answer'.startswith('### ') is False."
  },
  {
   "fact_id": "repo:F11",
   "claim": "'#### Answer' headings appear in the page TOC with no warning; an admonition opened in one cell cannot contain later cells.",
   "verdict": "confirmed",
   "reasoning": "Same as jupyter:Q3-b and Q3-c, reproduced in my own mini book."
  },
  {
   "fact_id": "repo:F12",
   "claim": "Website does not execute review pages; prep strips only %%expect; '# Solution'/'solution'-tagged cells are blanked.",
   "verdict": "confirmed",
   "reasoning": "jb/_config.yml has execute_notebooks 'off'. execute_notebooks.py:139 globs chap*.ipynb. prep_notebooks.py:70 checks source.startswith('# Solution') or 'solution' in tags, and line 74 is the %%expect strip."
  },
  {
   "fact_id": "repo:F14",
   "claim": "run_code calling get_ipython() breaks under turtle_images' plain exec.",
   "verdict": "plausible",
   "reasoning": "Not run. With the prototype's run_code (get_ipython().run_cell(code)), get_ipython is used on every call, not just in an except branch. So any run_code cell executed by plain exec raises NameError before drawing anything. The adapted tools must define a fallback, or inject get_ipython."
  },
  {
   "fact_id": "prototype:F1",
   "claim": "rsync not installed; build scripts use git rev-parse; venv-lab Playwright wants chromium(-headless-shell)-1243 but /opt/pw-browsers has only 1194; likely causes of worker failures.",
   "verdict": "confirmed",
   "reasoning": "The environment facts are confirmed: 'command -v rsync' finds nothing; venv-lab's playwright browsers.json lists chromium and chromium-headless-shell revision 1243; /opt/pw-browsers holds chromium-1194 and chromium_headless_shell-1194. I hit more traps myself. jupyter lab exits as root without --allow-root ('Running as root is not recommended'). window.jupyterapp needs --LabApp.expose_app_in_browser=True. 'pkill -f'/'pgrep -f ... | kill' with a pattern found in the Bash command itself kills the calling shell (exit 144, twice). Linking any of these to workers 3 and 4 is still a guess."
  },
  {
   "fact_id": "prototype:F3",
   "claim": "JupyterLab 4.6.4 reads jp-MarkdownHeadingCollapsed on load; converted pages open collapsed.",
   "verdict": "confirmed",
   "reasoning": "Confirmed by the source (cells widget.ts ~2149) and by my own browser test on an equivalent notebook. I did not open their chap05 in the browser."
  },
  {
   "fact_id": "prototype:F5",
   "claim": "Simulated Colab Run all (nbclient allow_errors=False, force_raise_errors=True) reaches the end of all six converted pages with no answer output visible (chap07 setup only).",
   "verdict": "confirmed",
   "reasoning": "I re-ran all six out/all pages myself in the Colab-like stack (Python 3.12.3, IPython 7.34.0, ipykernel 6.17.1) with my own visibility analyzer (verify-jupyter/runall/ra.py). All six reached the end. The only visible output was chap07 cell 5, the setup. Every Answer heading has jp-MarkdownHeadingCollapsed, id == metadata.id, and is listed in colab.collapsed_sections. Caveat: nbclient models only stopping on reply status (client.py:906), not a frontend that might stop on error outputs."
  },
  {
   "fact_id": "prototype:F6",
   "claim": "run_code as get_ipython().run_cell(code) shows the error with status ok, cleaner messages, correct line numbers, no run_code frame, final expression displayed; Colab overrides neither do_execute nor run_cell.",
   "verdict": "confirmed",
   "reasoning": "Reproduced on both stacks. Colab's _kernel.py and _shell.py have no do_execute or run_cell override. Corrections: on IPython 8+ the label is 'Cell In[N+1]', not In[N]. On Colab (7.34) the header reads 'File \"/tmp/ipykernel_N/<hash>.py\", line 2'. The prototype's run_code lacks the KeyboardInterrupt re-raise (Q2-f)."
  },
  {
   "fact_id": "prototype:F7",
   "claim": "In JupyterLab 4.6.4 Run All runs cells in collapsed Answers; outputs stay hidden; expanding shows real errors.",
   "verdict": "confirmed",
   "reasoning": "Independently reproduced (see jupyter:Q1-b): outputs error:SyntaxError and error:ZeroDivisionError stayed in hidden cells after Run All."
  },
  {
   "fact_id": "prototype:F8",
   "claim": "Stepping with Shift+Enter in JupyterLab expands each collapsed Answer.",
   "verdict": "confirmed",
   "reasoning": "Independently reproduced with real key presses (see jupyter:Q1-e)."
  },
  {
   "fact_id": "prototype:F9",
   "claim": "Adapted prep turns each '#### Answer' section into one collapsed dropdown; no h4, no Answer TOC entries, no new warnings.",
   "verdict": "confirmed",
   "reasoning": "I read the prep diff (answer_sections) and the built proto/repo/jb/_build/html/yr/chap05_review.html: 17 dropdown admonitions, only toc-h2 (3 unique, including Credits) and toc-h3 (17) entries, and no #answer or #idN anchors. warn_final.txt lists only the 2 known chap01 and chap02 lexer warnings. I did not rebuild it myself."
  },
  {
   "fact_id": "prototype:F10",
   "claim": "A collapsed heading hides everything up to the next same-or-higher heading, so the credit cell is swallowed without its own heading.",
   "verdict": "confirmed",
   "reasoning": "The collapse-range semantics are confirmed by setHeadingCollapse and findNextParentHeading in actions.tsx, and by my test, where only '## Credits' ended the last section. '## Credits' adds an h2 page-TOC entry (seen in the prototype build)."
  },
  {
   "fact_id": "prototype:F11",
   "claim": "Answer code cell must be byte-identical; an added comment line shifts doctest line numbers.",
   "verdict": "plausible",
   "reasoning": "Not re-run. It is consistent with my observation that every leading line, including the newline after the opening triple quotes, shifts reported line numbers in exec-based variants. Nested run_cell strips leading blank lines but not comment lines."
  },
  {
   "fact_id": "prototype:F17",
   "claim": "%%question magic: Run all reaches end; Pyright flags the magic line and hidden syntax errors.",
   "verdict": "plausible",
   "reasoning": "I confirmed the IPython side (storage, status ok) in jupyter:Q4-a. I did not re-run Pyright. Colab's linting of magic cells is unknown."
  },
  {
   "fact_id": "prototype:F18",
   "claim": "RecursionError tracebacks are thousands of lines on IPython 9.17 (plain and run_cell) but ~18 lines on IPython 7.34.",
   "verdict": "confirmed",
   "reasoning": "k/rec.py: on 9.17, 3920 lines (plain) and 3888 (nested run_cell); on 7.34, 20 and 20. The exact counts depend on the code."
  }
 ],
 "overall_risks": [
  "Colab's frontend is the main unknown. Every 'Run all reaches the end' result (nbclient, JupyterLab) depends on reply status 'ok', and nbclient ignores error outputs (client.py:906). If Colab's Run all also stops on an iopub 'error' message, the run_code design fails there. Test it live first. The fallback should be a run_code that sets ip._showtraceback to print stb2text(stb) to stderr around ip.run_cell(code); I tested that it gives tracebacks identical to normal cells on IPython 7.34 and 9.17, with status ok. Do NOT use the stb2text(structured_traceback(*exc_info())) form: it loses the SyntaxError source line and caret.",
  "If error output moves to stderr, check_review must parse the traceback from stderr. Today it reads only output_type=='error' (L104), so error checks would be silently skipped, which weakens the checks.",
  "Colab pins ipython==7.34.0 and ipykernel==6.17.1 (colabtools setup.py), while local and CI checks run IPython 9.17. Any traceback trick must be tested on 7.34. The linecache plus tb.tb_next variant (repo F6) drops frames on 7.34; a module-level NameError then shows no frame at all, which breaks ch03 Q14's traceback-order answer. Nested run_cell is the only variant I tested that looks like a normal cell on both versions.",
  "Nested run_cell swallows KeyboardInterrupt (status ok), so Stop would not halt Run all. The prototype's run_code lacks the re-raise. Add 'if isinstance(r.error_in_exec, KeyboardInterrupt): raise ...'; note that this prints the interrupt traceback twice unless the display is suppressed.",
  "Nested run_cell labels errors 'Cell In[N+1]' on IPython 8 and later. On Colab (7.34) they read '/tmp/ipykernel_N/hash.py'. Answer text must keep comparing only 'Ename: message' lines, never file or line headers.",
  "exec-based runners lose the last-expression display (ch02 Q4 '12', ch03 Q9 function repr). Nested run_cell keeps it, but check_review never checks execute_result; add that check rather than leave the gap.",
  "On Colab, ModuleNotFoundError (ch02 Q14a) gets Colab's custom NOTE appended. That happens through nested run_cell or a normal cell, not through exec+showtraceback. It is harmless under the substring check, but the live output in Colab differs from the Answer text.",
  "In JupyterLab and Notebook 7, Shift+Enter walks into each collapsed Answer and expands it (independently reproduced). If Colab behaves the same, a student who steps through the page reveals every answer. Test it live; it may need student instructions (use Run all or Ctrl+Enter) or a layout tweak.",
  "VS Code ignores both collapse markers, so every Answer and its live output is visible there after Run all.",
  "Website: myst-nb parses each cell on its own, and mistakes fail silently with no warning: a raw '#### Answer' adds TOC entries (#answer, #id1...), an unclosed ':::' leaves the answer visible, and the stray fence becomes an empty div. prep must merge each Answer section into one dropdown cell. Add a build or prep assertion that every page has 0 h4 'Answer' headings and exactly one dropdown per question. Skipping a heading level (H3→H5) adds a myst.header warning.",
  "The last Answer swallows the credits unless a '## Credits' heading (an extra page-TOC entry) or something similar ends it. Run All also leaves the last cell active, and JupyterLab connects activeCellChanged to expandParent, so a last cell inside a collapsed section may be expanded.",
  "%%question magic: a misspelled name or running before setup gives a UsageError (status error) that stops Run all; prep must strip the %% line; check_notebooks must whitelist it; whether Colab lints magic bodies is unknown.",
  "Tools that exec page code outside IPython (turtle_images, standalone checks) break with a get_ipython()-based run_code unless it has a fallback.",
  "Evidence quality: the jupyter worker's saved classic_codecell.js is a 404 page; I confirmed its claim from nbclassic codecell.js:340 instead. The Notebook 7 and VS Code claims rest on shared code or source reading, not runs.",
  "The user's question about the failed workers: rsync is missing, Playwright in venv-lab expects revision 1243 while only 1194 is installed, jupyter lab refuses to run as root without --allow-root, window.jupyterapp needs --LabApp.expose_app_in_browser, build scripts need git rev-parse, and 'pkill -f'/'pgrep -f | kill' with a pattern that appears in the Bash command kills the calling shell (exit 144; this happened to me twice). All are real environment traps, but that they caused the workers' errors is still unconfirmed; the orchestrator should check their transcripts.",
  "My artifacts are under /tmp/claude-0/-home-user-yrThinkPython/6571a165-f8cc-5e43-8b74-c00357a4a6f6/scratchpad/ultra/verify-jupyter/: k/out_ipy9.txt, k/out_ipy7.txt, k/intr.py, k/stderr2.py, k/rec.py, book/, lab/, jlab/v464/, colab/ and runall/. The browser driver is at jupyter-facts/browser/verify_v.mjs, because it reuses that directory's node_modules. Nothing under /home/user/yrThinkPython was modified."
 ]
}
```
