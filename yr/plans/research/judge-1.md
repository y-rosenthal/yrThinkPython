# judge:1

```json
{
 "scores": [
  {
   "plan_index": 0,
   "correctness": 8,
   "student_experience": 9,
   "maintainability": 7,
   "risk_handling": 8,
   "total": 32,
   "strengths": "It answers the user's worker question correctly, and I checked this. In journal.jsonl, workers 3 and 4 (af37ec9a, a1fdadad) both end at 17:20:58.398Z with '[Request interrupted by user]'. The run resumed at 17:24:00, and replacement agents a20fcc3e and a24699395 finished it. The plan also says plainly that the environment traps were not the cause. On the design, it is the strongest for students. Multi-part answers are interleaved: each part's explanation is followed by its own live cell. Decision D7 keeps the website looking the same by having prep turn the question-code cells back into code cells. It has a detailed table of wording edits. Its check rule 6 (a cell uses run_code exactly when it raises) is the strongest per-cell guard against M1. The full-line reverse rule ('every XxxError line in the Answer is produced') also closes M1. It forbids ATX, setext and HTML headings inside Answers. L3 is a link to the prototype chap05 already pushed on origin/yr-runall-research, so the professor can test in Colab today. I confirmed the file is on that branch; the branch head has since moved from e68aa02 to 6ec87ba. Facts are labelled VERIFIED / BELIEVED / UNKNOWN throughout. It handles Stop by re-raising KeyboardInterrupt, gives run_code a plain-Python fallback, and adds a prep guard plus a single merge to prevent version skew.",
   "weaknesses": "Deciding where run_code is needed means executing the page during sync. So the 'is everything in sync' state cannot be fully checked statically by check_notebooks, and the tools need the venv. The single source is the 'question-code' cell tag. Whether Colab keeps tags when it saves is untested, and if it drops them the source marker is lost (the check fails closed, but the professor is left with friction). There is no guard against '>>>' lines inside run_code strings. I confirmed that IPython 9.17's doctest PromptStripper strips them unless the text before the opening quote is only a string prefix, and 'run_code(r' is not. It is safe today only because ch07 Q14 does not raise. Plan B (closed HTML details) is described but not built. The plan slightly overclaims Notebook 7 as VERIFIED. The run_code definition stays visible in the setup cell on the website."
  },
  {
   "plan_index": 1,
   "correctness": 6,
   "student_experience": 7,
   "maintainability": 9,
   "risk_handling": 6,
   "total": 28,
   "strengths": "Its idea is the most maintainable. The rule 'check = normalize is a no-op' is a static, stdlib-only DRY check, with no parsing of run cells. The %%run_question cell magic takes the code verbatim, so there is no quoting, no raw strings and no doctest stripping. I confirmed in the IPython 9.17 source that docstrings inside a magic body keep their '>>>' lines, while 'run_code(r'''' loses them. One function (render_run_cell) is the only place that knows how run cells are built. The '```python run' fence marker survives any editor, including a Colab save that might drop tags. Pictures become derived content: turtle_images --check runs in review.sh check. The managed run_question cell is tagged remove-cell, so the website never shows the tooling. It commits a 19-mutation selftest. Verification was strong: all 103 questions were compared before and after conversion on both IPython 9.17 and 7.34 with 0 differences, and one real gap was found (ch02 Q4 is missing its 12 text block). It also found the IPython 9 doctest problem that string wrapping causes.",
   "weaknesses": "It does not answer the user's first question. It says it cannot see the workers' transcripts, yet they are readable at subagents/workflows/wf_f52e2176-172/agent-*.jsonl and show a user interrupt. Instead it lists environment traps as likely causes, which is misleading. Check B5 matches only the exception NAME ('^[A-Z]\\w*(Error|...)'), so M1 on ch05 Q8 part a would pass because part b also raises SyntaxError. Its claim to catch M1 there is doubtful. It adds a new untested Colab dependency: a custom cell magic, against Colab's 'unsupported_magics_check' flag and its history of linting magic bodies. Fallback (b) is unverified and brings back the string problems. Run cells sit at the end of the Answer rather than interleaved. How the 'python run' info string renders in Colab is untested. Students must run two setup cells. There is no HTML-heading rule. Some details are sloppy ('ch07 Q? cell 25').",
   "plan_index_note": "n/a"
  },
  {
   "plan_index": 2,
   "correctness": 9,
   "student_experience": 7,
   "maintainability": 7,
   "risk_handling": 10,
   "total": 33,
   "strengths": "Its worker diagnosis is the most precise, and I verified every detail. The main session queued the message 'Is Claude Code running on my laptop faster...' at 17:20:53. At 17:20:58.405 the pending claude-code-guide Agent call was rejected with '[Request interrupted by user for tool use]', in the same instant both workers were interrupted. The run resumed with resumeFromRunId at 17:24:00. Its advice on avoiding a repeat is actionable. Its risk handling is the best of the three: the smoke notebooks test which metadata Colab really needs (full markers, top-level id only, JupyterLab key only); variants A and B are compared side by side for red badges; a Stop test; and editor tests E1-E7. Fallback C (run_hidden, an HTML details box, with exact values attached in display metadata so check_review need not parse HTML) is built and verified on both stacks. The rollout is staged and gated, with dual-format tools during the transition and per-page revert. Its checks are sound: a refusal for '>>>' lines inside run_code (verified real); a full-line reverse error rule; stderr-traceback parsing so fallback B cannot blind the check; execute_result and turtle-display checks. It hardens turtle_images so the run fails when an example picture's code raises, which stops silent PNG rewrites. It adds a CI lint step; I confirmed the CI uses Python 3.12. A remove-cell help cell keeps Colab-only instructions off the site.",
   "weaknesses": "Dual-format tools during Stages 2-4 are throwaway complexity, and page-by-page merges to v3 mean several publish cycles. Run cells come last in the Answer, not interleaved. Multi-part run cells get a '# Part x' comment, a special case the check must strip, which adds a line to plain cells. Like Plan 0 it depends on a tag-based marker, whether Colab keeps on save is untested, and sync must execute the page. The check does not explicitly enforce 'wrapped exactly when it raises' per cell; it relies on the reverse rule. The website shows question code as markdown blocks instead of code cells. The run_code definition is visible in the setup cell on the site. It slightly overclaims Notebook 7 as VERIFIED. Its turtle picture rule (draw the question's last question-code block) guesses in multi-part questions."
  }
 ],
 "best_ideas_to_graft": [
  "Explain the worker errors with Plan 2's evidence (verified in the journal and transcripts). Workers 3 and 4 (af37ec9a, a1fdadad) were cut off at 17:20:58.398Z by '[Request interrupted by user]'. That interrupt came from the pending claude-code-guide tool call being rejected 5 seconds after the user's queued message. The run was already resumed at 17:24:00 (replacement agents a20fcc3e and a24699395 finished), so nothing needs fixing. The environment traps were not the cause.",
  "From Plan 1: make the DRY check static. 'normalize/sync would change nothing' should be verifiable by check_notebooks without running the page, as far as possible. Treat turtle pictures as derived content (turtle_images --check inside review.sh check).",
  "From Plan 1: hide the run_code/run_question helper from the website (a remove-cell managed cell, or prep stripping the helper lines), so the site's setup cell does not show tooling.",
  "From Plan 1: add a verification gate that compares, for all 103 questions, stdout, error lines, last-expression values and turtle displays between the old and new pages on both IPython 9.17 and 7.34 (plan-maint/exp.py).",
  "From Plan 1: commit the mutation selftest (yr/tools/selftest_review.py via review.sh selftest) so later sessions cannot silently weaken the checks.",
  "From Plan 1, as a marker-robustness test: add a Colab check (C10) of whether Colab keeps cell tags on save. If it drops them, use a visible marker (the '```python run' fence) instead of the 'question-code' tag.",
  "From Plan 0: interleave multi-part Answers (explanation of part a, live cell a, explanation of part b, live cell b).",
  "From Plan 0: decision D7, where prep turns question-code markdown back into code cells so the website looks exactly as today; and strip '## Credits' on the site.",
  "From Plan 0: check rule 6 (run_code exactly when the cell raises) as a per-cell guard. Pair it with a full-line reverse rule (every 'XxxError: ...' line in the Answer is produced), not Plan 1's name-only B5, which would miss M1 on ch05 Q8.",
  "From Plan 0: forbid HTML <h1>-<h6> as well as ATX and setext headings inside questions and Answers.",
  "From Plan 0: give the professor the already-pushed prototype link (origin/yr-runall-research, yr/plans/research/prototype/out/all/chap05_review.ipynb) for an immediate Colab test before pushing anything new.",
  "From Plan 0: use the exact table of wording edits, with a must-match-once check and a grep afterwards for leftover 'cell' / 'run it' wording.",
  "From Plan 2: smoke notebooks that test metadata variants (full markers / top-level id only / jp key only), variant A vs B side by side for red badges, a Stop test, and editor tests E1-E7, all in one Colab session.",
  "From Plan 2: refuse '>>>' lines inside run_code strings (IPython >=8's doctest PromptStripper strips them unless only a string prefix comes before the opening quote; confirmed in the IPython 9.17 source).",
  "From Plan 2: fallback C (run_hidden with an HTML details box, exact values attached in display metadata for the checker), already built and verified on both stacks.",
  "From Plan 2: turtle_images exits 1 without writing when an example picture's code raises, which prevents silent PNG rewrites under version skew.",
  "From Plan 2: staged, gated rollout with a per-page revert path; add the check_notebooks step to deploy-book.yml; add review.sh check --colab-like on the IPython 7.34 / ipykernel 6.17.1 venv.",
  "All plans: make the run_code KeyboardInterrupt re-raise standard, and add a prep guard that fails the build if any '#### Answer' heading or run cell survives prep."
 ]
}
```
