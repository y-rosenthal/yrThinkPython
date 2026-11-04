---
name: yrUpdateDocsSkillsRulesEtc
description: Bring this project's docs, skills, rules and whatever else the changes touched into line with what was done and decided in this chat, as a careful developer does before handing work over (the yrUpdateDocsSkillsRulesEtc skill of yrProject). Use when the user says "update the docs", "update the docs and skills", "I'm done" or "let's push", before the user clears or leaves the chat, and when a git push was refused with "files changed since the docs, skills and rules were last updated".
allowed-tools:
  - Bash(bash ${CLAUDE_SKILL_DIR}/scripts/yrUpdateDocsSkillsRulesEtc.sh *)
---

<!-- Installed by yrProject v0.8.0 (https://github.com/y-rosenthal/yrProject): the templates
     and the tool that give a project one base for AI-assisted work (rules for AI agents, skills, hooks, GitHub
     issues for work to do later, project docs). This file belongs to the tool: do not edit it by hand, and do
     not change it without the tool. "yrProject.sh update" replaces it with each new version (if you change it,
     update leaves it alone, and it gets no newer versions); "yrProject.sh remove" removes it.
     .yrProject/README.md lists every file that yrProject installed, and tells who changes each one. -->

# Update the docs, skills, rules, etc. (yrUpdateDocsSkillsRulesEtc)

Before a push, and before the user clears or leaves the chat, bring the whole repository into line with what
was done and decided in this chat: the docs, the skills, the rules, and whatever else the changes touched.

1. See what changed: `git status --short` and `git diff --stat @{upstream}` (`git log --stat -5` if there is
   no upstream). Then go back through this conversation: what was built, renamed or removed, and what the user
   decided or asked for from now on.
2. Then do what a careful developer does before handing the work over: bring everything in the repository
   that describes or depends on these changes into line with them. What that is depends on the change; find it
   from the change itself and from the conversation. Two sources, not one:
   - **the changes:** what else names, explains, documents, tests or assumes the thing that changed, anywhere
     in the repository (for example the README and the documents in `docs/`, a skill's `SKILL.md`, a script's
     `--help`, a comment, an example, a configuration that must agree);
   - **the chat:** what the user decided or asked for from now on ("always ...", "never ...", "from now on ...").
     That goes into the project's rules (`AGENTS.md`, outside the yrProject blocks; `CLAUDE.md` for Claude Code
     only), because a chat is cleared and a rule stays.
   Leave the files that yrProject installed alone (their first lines say "Installed by yrProject"). Work left
   for later goes in an issue (the yrIssues skill), not in a document.
3. Tell the user in a few lines what you updated, and what you looked at and left alone.
4. Record the review, last of all, after every edit: `bash ${CLAUDE_SKILL_DIR}/scripts/yrUpdateDocsSkillsRulesEtc.sh done`
   (it touches the marker file `docs-reviewed` in `.git/`). The push hook lets a push through only when no file
   changed after that. If there was nothing to update, say so and record it anyway. Do not record a review that
   you did not do, unless the user says to skip it.
5. Commit and push only if the user asks. Commit without `-q`: the commit line with its hash stays in this chat,
   which is how the next session finds this one after `/clear` (below).

## After `/clear`, or in a new session

A SessionStart hook runs `yrUpdateDocsSkillsRulesEtc.sh session-start`. When files changed after the last
recorded review, it tells you and the user, and names the chat that made one of the last commits (it searches the
session transcripts for the commit hashes). Offer the review in your first reply. If the user agrees and the work
was done in that earlier chat, read it first: `/resume` brings it back whole, or read the lines of the transcript
file whose `"type"` is `"user"` or `"assistant"` (their text is in `message.content`; skip the tool output).
