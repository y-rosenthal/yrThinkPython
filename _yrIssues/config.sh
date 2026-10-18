# Settings of the yrIssues skill for this project. .claude/skills/yrIssues/scripts/yrIssues.sh reads this file.
# The project owns it: yrProject.sh added it once, and "yrProject.sh update" does not change it.

# The category labels: "name|color|description". Each issue gets one category and one priority.
# After a change, run: bash .claude/skills/yrIssues/scripts/yrIssues.sh setup-labels
CATEGORIES=(
  "fix|D93F0B|Something is wrong and needs fixing"
  "improvement|0E8A16|New or better content or features"
  "decision|5319E7|Needs the owner's decision"
  "recheck|1D76DB|Time-sensitive fact to re-verify"
)

# If set, only the open issues with this label count, for example "yrIssue" (the label of the issues that the
# yrIssues skill creates), in a public repository where other people open issues too. Empty: every open issue
# of the repository counts.
LABEL=""
