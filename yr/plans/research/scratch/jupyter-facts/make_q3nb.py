import sys, nbformat as nbf
md, code = nbf.v4.new_markdown_cell, nbf.v4.new_code_cell
Q = "```python\nx = 5\nif x = 5:\n    print('five')\n```\n"
cells = [md("# Variants\n\nTest page."), md("## Questions")]
# V1 raw answer heading
cells += [md("### Question 1 (easy): raw Answer heading\n\nWhat happens?\n\n" + Q),
          md("#### Answer", metadata={"jp-MarkdownHeadingCollapsed": True}),
          code("run_code(\"\"\"\nx = 5\nif x = 5:\n    print('five')\n\"\"\")"),
          md("```text\nSyntaxError: invalid syntax\n```\n\nExplanation of question 1.")]
# V2 answer heading as rubric
cells += [md("### Question 2 (easy): rubric instead of heading\n\n" + Q),
          md("```{rubric} Answer\n```"),
          code("print('q2')"),
          md("```text\nq2\n```")]
# V3 merged dropdown (what prep could generate)
cells += [md("### Question 3 (easy): merged dropdown\n\n" + Q),
          md(":::{admonition} Answer\n:class: dropdown\n\n```python\nprint('q3')\n```\n\n```text\nq3\n```\n\nExplanation of question 3.\n:::\n")]
# V4 hide-cell with custom prompts, with a stored output
c = code("print('q4')"); c.metadata = {"tags": ["hide-cell"], "mystnb": {"code_prompt_show": "Answer", "code_prompt_hide": "Hide answer"}}
c.outputs = [nbf.v4.new_output("stream", name="stdout", text="q4\n")]; c.execution_count = 4
cells += [md("### Question 4 (easy): hide-cell with prompts\n\n```python\nprint('q4')\n```"), c]
# V5 hide-input / hide-output / remove-input default prompts
for i, tag in enumerate(["hide-input", "hide-output", "remove-input"]):
    c = code(f"print('q5{tag}')"); c.metadata = {"tags": [tag]}
    c.outputs = [nbf.v4.new_output("stream", name="stdout", text=f"q5{tag}\n")]; c.execution_count = 10 + i
    cells += [md(f"### Question 5{'abc'[i]} (easy): tag {tag}"), c]
# V6 attempt to span a dropdown across cells
cells += [md("### Question 6 (easy): spanning attempt\n\n" + Q),
          md(":::{admonition} Answer\n:class: dropdown\n\nOpened in this cell."),
          code("print('q6')"),
          md("```text\nq6\n```\n:::")]
# V7 current html details approach (unconverted)
cells += [md("### Question 7 (easy): raw html details\n\n" + Q),
          md("<details>\n<summary>Answer</summary>\n\n```text\nq7\n```\n\n</details>")]
# V8 heading demoted to bold paragraph
cells += [md("### Question 8 (easy): bold paragraph instead of heading\n\n" + Q),
          md("**Answer**"), code("print('q8')")]
cells += [md("Credit line.")]
nb = nbf.v4.new_notebook(cells=cells)
nb.metadata = {"kernelspec": {"name": "python3", "display_name": "Python 3", "language": "python"},
               "language_info": {"name": "python", "pygments_lexer": "ipython3"}}
nbf.write(nb, sys.argv[1])
