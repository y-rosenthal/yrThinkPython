---
name: yrIssues
description: Track this project's issues (the yrIssues skill of yrProject) - things to do later without forgetting them. They are the open GitHub issues of the project's repository, with a saved copy in _yrIssues/issues.md, but the user just talks to the agent. Covers the start-of-session count, listing issues on request, adding issues, showing details, working on issues, and closing them.
when_to_use: Use at the start of every session (the SessionStart hook supplies the count), and whenever the user says things like "list issues", "add an issue", "remind me later", "not now, save it for later", "what's open?", "let's work on #12", "change the priority of...", or "#12 is done / no longer needed". Also use when you notice a problem you won't fix right now.
allowed-tools:
  - Bash(bash ${CLAUDE_SKILL_DIR}/scripts/yrIssues.sh *)
  - Bash(gh issue list *)
  - Bash(gh issue view *)
  - Bash(gh issue create *)
  - Bash(gh issue edit *)
  - Bash(gh issue comment *)
  - Bash(gh issue close *)
  - Bash(gh issue reopen *)
---

<!-- Installed by yrProject v0.6.0 (https://github.com/y-rosenthal/yrProject): the templates
     and the tool that give a project one base for AI-assisted work (rules for AI agents, skills, hooks, GitHub
     issues for work to do later, project docs). This file belongs to the tool: do not edit it by hand, and do
     not change it without the tool. "yrProject.sh update" replaces it with each new version (if you change it,
     update leaves it alone, and it gets no newer versions); "yrProject.sh remove" removes it.
     .yrProject/README.md lists every file that yrProject installed, and tells who changes each one. -->

# Issues (yrIssues)

## What it is for

- The user can add issues now and work on them later, so that less important things are not forgotten.
- **At the beginning of every session**, the user is told how many issues are open, and asked whether to list them.
  The full list is not loaded at the start, to save context.
- The issues are GitHub issues, and are called "issues", as on GitHub. The user may not want to use GitHub
  directly: do the GitHub work for them.
- Each issue that you create gets the label `yrIssue`, so that the user can see which issues came from this skill.

## How it works

- Every open issue in the project's GitHub repository (`git remote get-url origin`) counts, unless
  `_yrIssues/config.sh` sets `LABEL` (then only the issues with that label). An issue that you create has:
  - the label `yrIssue`;
  - one category label (the list is `CATEGORIES` in `_yrIssues/config.sh`; after a change, run `setup-labels`);
  - one priority label: `priority: high`, `priority: medium` or `priority: low`.
- `.claude/settings.json` has two hooks:
  - **SessionStart** (when a session starts, and after `/clear`) runs `scripts/yrIssues.sh session-start`. It
    refreshes the saved copy and gives the user and you the count, not the list. Claude Code does not always show
    its message on screen, so you also give the count in your first reply.
  - **PostToolUse** runs `scripts/yrIssues.sh hook-sync` after each `gh issue ...` command. After a command that
    changes an issue (create, edit, close, reopen, delete, transfer), it refreshes the saved copy.
- `_yrIssues/issues.md` is the saved copy of the open issues (for when GitHub can't be reached). The script writes
  it only when an issue changed, so git sees a change only then. Don't edit it.
- **Other agents** (not Claude Code) have no hooks: after each change to an issue, run
  `bash ${CLAUDE_SKILL_DIR}/scripts/yrIssues.sh sync`.
- **`gh` uses this project's repository.** The SessionStart hook makes sure of it (`gh repo set-default`, if no
  default is set), also in a copy of someone else's repository that has an `upstream` remote, so plain
  `gh issue ...` commands never touch the upstream repository. Other agents run
  `bash ${CLAUDE_SKILL_DIR}/scripts/yrIssues.sh setup-labels` once, which does the same.
- `bash ${CLAUDE_SKILL_DIR}/scripts/yrIssues.sh --help` shows every command.

## At the start of a session

In your **first reply**, add one short line with the count and ask whether to list the issues, for example "You
have 12 open issues (3 high). Want me to list them?". Skip it only if the user is already asking about issues.
Answer their actual message as usual.

When they want the list ("list issues", "what's open?", "yes"):

1. Run `bash ${CLAUDE_SKILL_DIR}/scripts/yrIssues.sh list`.
2. Show it under the heading "Issues", one line per issue: `#12 [high] Short title`, highest priority first.
3. Ask whether they want to work on any of them now. They can pick numbers or say "not now".

## Adding an issue

When the user asks you to remember something for later, or you find a problem you won't fix now:

1. Write a short, specific title (under about 70 characters). Name files or sections by name, not by number.
2. Write a body that someone (an agent in a fresh session) can act on without this conversation:

   ```
   **What:** the problem or task, 1-3 sentences.
   **Where:** files (and line numbers or section titles).
   **Why it matters:** the impact.
   **Suggested fix:** concrete steps, with sources/links if facts must be checked.
   **Done when:** how to verify (e.g. tests pass, command works, page renders).
   ```

3. Create the issue (add `--label "$LABEL"` too if `_yrIssues/config.sh` sets another `LABEL`):

   ```bash
   gh issue create --title "..." --body "..." --label yrIssue --label <category> --label "priority: <level>"
   ```

   Default to `priority: medium` unless the user says otherwise or the issue breaks something (`high`). If `gh`
   says that a label is not found, run `bash ${CLAUDE_SKILL_DIR}/scripts/yrIssues.sh setup-labels` once, then retry.
4. Confirm in one line: "Added issue #N: title".

## Working on an issue

1. Run `gh issue view <N>` and read the body and comments.
2. Do the work, following the project's other skills and rules. Verify the result.
3. Tell the user what changed and ask whether to close the issue. Close it once they agree, or right away if they
   asked you to finish it:

   ```bash
   gh issue close <N> --comment "Done: <one-paragraph summary of what changed and how it was verified>"
   ```

4. If the issue is only partly done, add a comment (`gh issue comment <N> --body "..."`) and leave it open.

## Changing or dropping an issue

- **Priority or category:** `gh issue edit <N> --remove-label "priority: low" --add-label "priority: high"`.
- **No longer needed:** `gh issue close <N> --reason "not planned" --comment "<why>"`.
- **Reopen:** `gh issue reopen <N>`.
- Never delete issues.
- Don't commit or push unless the user asks. If they ask you to commit a fix, put `Fixes #N` in the commit message.

## When GitHub can't be reached, or there is no GitHub repository yet

If `gh` isn't installed or logged in, there's no network, or the project has no GitHub remote:

- `yrIssues.sh` falls back to the saved copy in `_yrIssues/issues.md`, and to the queue.
- Record new issues in `_yrIssues/queue.md`, each as a `### [priority] Title` heading followed by the body.
- The next time `gh` works, create those issues and empty the queue file.
- If `gh` isn't logged in, ask the user to run `! gh auth login`. You can't log in for them.
- If there is no GitHub repository, offer to make a private one: `gh repo create --private --source . --push`, then
  `yrIssues.sh setup-labels`. Don't make it without the user's approval.

Never put passwords, API keys or other secrets in an issue: the repository may be public, or become public.
