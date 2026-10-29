---
name: yrProject
description: Look after this project's yrProject setup for the user (a yrProject is a project set up with the yrProject.sh tool), so that they never need to learn the tool - check that the yrProject setup is correct, show its version and whether a newer one exists, update or migrate it (with the user's approval), remove it, list all the yrProjects, and make a new yrProject. Also the version line "(yrProject vX.Y.Z [latest ...])" that every reply starts with.
when_to_use: Use when the user clearly means yrProject - they say "yrProject", the yrProject setup, its shared rules, skills, hooks or template version - for example "check the yrProject setup", "is this yrProject up to date?", "update yrProject", "migrate to the newest yrProject version", "remove yrProject", "the shared rules changed", "which of my projects use yrProject?", "make a new yrProject", or "set up this folder with yrProject". Also use when a session-start notice or "yrProject.sh check" reports a problem, or before you change a file that yrProject installed. If the user only says "project" (for example "update the project", "make a new project"), do not assume that they mean a yrProject: ask first.
allowed-tools:
  - Bash(yrProject.sh check*)
  - Bash(yrProject.sh status*)
  - Bash(yrProject.sh projects)
  - Bash(yrProject.sh projects --check)
  - Bash(yrProject.sh update --dry-run*)
  - Bash(yrProject.sh remove --dry-run*)
  - Bash(yrProject.sh new * --dry-run*)
  - Bash(yrProject.sh list)
  - Bash(yrProject.sh --help)
  - Bash(bash ${CLAUDE_SKILL_DIR}/scripts/yrProject-notice.sh *)
---

<!-- Installed by yrProject v0.6.0 (https://github.com/y-rosenthal/yrProject): the templates
     and the tool that give a project one base for AI-assisted work (rules for AI agents, skills, hooks, GitHub
     issues for work to do later, project docs). This file belongs to the tool: do not edit it by hand, and do
     not change it without the tool. "yrProject.sh update" replaces it with each new version (if you change it,
     update leaves it alone, and it gets no newer versions); "yrProject.sh remove" removes it.
     .yrProject/README.md lists every file that yrProject installed, and tells who changes each one. -->

# The yrProject setup of this project (yrProject skill)

`yrProject.sh` set up this project: the rules for AI agents (`AGENTS.md`, `CLAUDE.md`), the skills in
`.claude/skills/`, the hooks in `.claude/settings.json`, the block in `.gitignore`, and the record in
`.yrProject/`. Every file that it installed starts with a comment that names yrProject and its version. The user
does not need to know the tool: they ask you, and you run it, explain the result in plain words, and ask before
you change anything.

## The version line at the start of every reply

Every reply of yours starts with the line `(yrProject vX.Y.Z [latest])`, `(yrProject vX.Y.Z [latest vA.B.C])` or
`(yrProject vX.Y.Z [latest UNKNOWN])`: the version of yrProject in this project, and whether a newer one exists.
In Claude Code, a hook gives you the exact line at every prompt. In another agent, run
`bash ${CLAUDE_SKILL_DIR}/scripts/yrProject-notice.sh version` once at the start of a session and use its
output. In the first reply of a session, add one more line, from
`bash ${CLAUDE_SKILL_DIR}/scripts/yrProject-notice.sh facts`: the type, the installed parts and the parts not
installed (and, in the yrProject repository itself, the projects that use yrProject). Both lines, then the answer.

## Rules

- **"Project" does not mean yrProject.** A yrProject is a project set up with `yrProject.sh`; the word "project"
  alone can mean many other things (the code, the book, a GitHub project, a class project). Use this skill only
  when the user says yrProject (or the yrProject setup, the tool, its shared rules or skills), or the context makes
  it obvious. Otherwise ask, for example: "Do you mean the yrProject setup (the rules, skills and hooks that
  yrProject.sh installed), or something else?" "Make a new project" is not "make a new yrProject" until the user
  says so.

- **Commands that change nothing** (`check`, `status`, `projects`, `list`, `update --dry-run`, `remove --dry-run`,
  `new ... --dry-run`, the notice script) you can run at any time.
- **Commands that change files or GitHub** (`update -y`, `remove -y`, `new -y`, `projects --scan`, `yrIssues.sh
  setup-labels`, a commit): first show the user what will happen, in plain words, and run them only after the user
  agrees. The tool cannot ask the user itself (you have no terminal for its question), so always run
  `--dry-run` first, then `-y` after the user agrees.
- Never edit the tool's blocks in `AGENTS.md`, `README.md` and `.gitignore` (between a `begin yrProject` line and
  its `end yrProject` line, or `begin shared rules` and `end shared rules`), or the files in `.yrProject/`: the
  tool writes them.
- Before you change a file that the tool installed, read `.yrProject/README.md`: it says who changes each file.
- Don't commit or push unless the user asks.
- Speak of "the yrProject setup", "the shared rules", "the yrIssues skill"; give the commands only if the user asks
  for them.

## Find the tool

Run `yrProject.sh --help`. If the command is not found, try `bash ~/Dropbox/tools/yrProject.sh --help` and use
that path below. If neither works, the tool is not on this computer: it is in the Dropbox of the project's owner
(`_yrAiCoding/yrProject`, and the `tools` folder on `PATH`). Tell the user that only the owner, on a computer
with that Dropbox, can check, update or remove the setup; everything else in the project works without it.

## Check the setup ("is the yrProject setup correct?")

1. Run `yrProject.sh check`. Add `--online` if the user asks about GitHub or the issues (it checks that `gh` is
   logged in, the repository, the labels, and that the issues can be read).
2. Tell the user the result in one or two sentences:
   - "OK" lines: the setup is correct for its version.
   - `!` lines are problems. Most of them are fixed by an update (below); say which ones need work by hand.
   - `~` lines are notes, not problems: usually a file that someone changed on purpose (the tool leaves it alone).
   - `i` lines: for example, a newer version exists. Offer to update.

## Update or migrate the yrProject ("update yrProject", "a new yrProject version came out", "the shared rules changed")

1. Run `yrProject.sh update --dry-run`. Read the plan:
   - `+ add`, `~ change`, `- remove`: the files that it would add, replace or delete;
   - `= keep`: files that it leaves alone, because someone changed them;
   - `note:` lines: things to do by hand;
   - the diffs of `AGENTS.md`, `CLAUDE.md`, `.gitignore`, `.claude/settings.json` and `README.md`.
   If it says "Nothing to do", tell the user that the project is up to date, and stop.
2. Summarize the plan for the user in plain words: the version now and after; what is new for them (for example a
   new or renamed skill); what goes away; what they must decide or do by hand. If it lists files with uncommitted
   changes, say so, and offer to commit them first, so that the update can be undone.
3. Ask: "Shall I apply it?" Only after the user agrees, run `yrProject.sh update -y`.
4. The update ends with a check. Tell the user the result.
5. Then deal with what the output asks for, with the user's agreement:
   - **Notes to do by hand** (for example, the project's own rules in `AGENTS.md` still name an old skill, an old
     folder still has files that someone changed, or `_yrIssues/issues.md` is still tracked by git and should be
     taken out of the index with `git rm --cached`): offer to make the change yourself, and show it.
   - **"Migration ..." lines** say what changed between the versions and what to run once, for example
     `bash .claude/skills/yrIssues/scripts/yrIssues.sh setup-labels`, which renames or makes labels on GitHub.
     Explain it and run it only if the user agrees.
   - Run `yrProject.sh check` again until it says OK, or until only notes are left that the user wants to keep.
6. Offer to commit the changes (`git status` shows them). The tool commits nothing in the project. It does commit
   the project's entry in its own list of projects, in the yrProject repository.

Other options, only when the user asks for them: `--with-docs` (also add the project-docs book in `docs/`),
`--no-yrIssues` (no issues skill), `--version VER` (a version other than the newest).

## Remove yrProject from this project ("remove yrProject", "I don't want yrProject here any more")

1. Run `yrProject.sh remove --dry-run`. It lists what would go: the tool's files that nobody changed (the skills
   and their scripts, `docs/PROJECT-SETUP.qmd`), its blocks in `AGENTS.md`, `README.md` and `.gitignore` (the
   shared rules too), its hooks in `.claude/settings.json`, `.yrProject/`, and the `_yrIssues/` folder; and what
   stays: the project's own files, the docs book and its guides, files of the tool that were changed by hand, and
   everything on GitHub (the issues and the labels).
2. **If it refuses** because `_yrIssues/queue.md` has issues that are not yet on GitHub, tell the user which ones
   (the output lists them), and offer to create them on GitHub first (the yrIssues skill), then run the dry run
   again. Run `remove --force` only if the user says, in so many words, to delete those issues anyway.
3. Summarize the plan in plain words, and ask: "Shall I remove it?" Only after the user agrees, run
   `yrProject.sh remove -y` (with `--force` only as in step 2).
4. Tell the user what was removed, what was left (the output says), and that nothing was committed. Offer to
   commit. The project's entry in the list of projects is kept, marked as removed on that date.

## The list of yrProjects ("which of my projects use yrProject?", "which ones are out of date?")

1. Run `yrProject.sh projects` (with `--check`, also check each project on this computer). It works from any
   folder on the owner's computer, not only in a yrProject. In the yrProject repository itself, the notice at the
   start of a session lists the projects too.
2. Show the list: each project, its version, and its state (up to date; older; not on this computer; removed).
3. To update another project, the user can open it and ask there, or you can run the update with that project's
   folder as the PATH (`yrProject.sh update PATH --dry-run`, then as above).
4. If the user thinks that a project is missing: `yrProject.sh projects --scan FOLDER` finds the projects with a
   record under the folder and adds them to the list (it commits the list in the yrProject repository). Ask
   first.

## A new yrProject ("make a new yrProject")

1. Ask for what you need: the folder (for example `~/Dropbox/_yrAiCoding/NAME`), the title, one sentence that says
   what it is for, the type (`work`, or `book` for a Quarto book), and whether to make a private GitHub repository.
2. Run `yrProject.sh new PATH --title "..." --description "..." [--type book] [--github] --dry-run`, and tell the
   user what it would make.
3. After the user agrees, run the same command with `-y` in place of `--dry-run`.
4. Tell the user how to open it: start Claude Code in the new folder.

To set up an existing folder that was never set up, use the update steps above with that folder as the PATH.

## The state, in short ("what yrProject version is this on?")

`yrProject.sh status` prints the version and, for each part, what an update would do. `.yrProject/README.md`
has the version, the parts, the files and the history. `.yrProject/setup.env` has the same facts for scripts.
