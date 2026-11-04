<!-- Written by yrProject.sh. Do not edit: "yrProject.sh update" writes this file again. No "#" title:
docs/PROJECT-SETUP.qmd includes this file, and gives the title. -->

**Project setup by yrProject.sh.** `yrProject.sh`, the tool of yrProject (https://github.com/y-rosenthal/yrProject), set up this project. yrProject is the templates and the tool that give a project one base for AI-assisted work (rules for AI agents, skills, hooks, GitHub issues for work to do later, project docs). The tool installed the files below, and `yrProject.sh update` keeps them up to date. Every file that it installed starts with a comment that names yrProject and its version, and says whether the file belongs to the tool or to the project. Read this page before you change one of them.

| | |
|---|---|
| Template version | v0.9.2 |
| Parts | rules, yrIssues, subjexts |
| Set up by | `yrProject.sh update` (an existing folder) |
| Last change | 2026-11-04 |

## If you do not know yrProject

This repository uses yrProject. Some files here come from yrProject; the rest belong to this repository. How to tell them apart:

- **What yrProject is:** the templates and the tool that give a project one base for AI-assisted work (rules for AI agents, skills, hooks, GitHub issues for work to do later, project docs). Its repository: https://github.com/y-rosenthal/yrProject. If the link does not open, the repository is private: ask the owner of this project.
- **The version and the parts installed here:** run `bash .claude/skills/yrProject/scripts/yrProject-notice.sh facts` (bash and git only; the tool is not needed).
- **Whole files from yrProject:** the table "The files" below. Every file that yrProject installed starts with a comment that names yrProject and its version: "Installed by yrProject" for a file of the tool, "Added by yrProject" for a starting file that this project now owns.
- **Blocks inside files of this repository:** in `AGENTS.md`, `README.md` and `.gitignore`, the text from a line that starts with `<!-- begin yrProject`, `# begin yrProject` or `<!-- begin shared rules` to its end line comes from yrProject. Everything outside those blocks belongs to this repository.
- **Hooks in `.claude/settings.json`:** JSON has no comments. A hook whose command runs a script under `.claude/skills/yrProject/`, `.claude/skills/yrIssues/` or `.claude/skills/yrUpdateDocsSkillsRulesEtc/` comes from yrProject; the other settings belong to this repository.
- **`.yrProject/`:** the record of the setup (this page, `manifest.json`, `setup.env`), written by the tool.
- **The tool** `yrProject.sh` runs on the owner's computer. Without it, all these files are ordinary files: see "How to change things" below.

## The parts

- **rules**: the rules for every AI agent: `AGENTS.md`, with a copy of the shared rules (their source is `templates/v0.9.2/AGENTS-shared-rules.md` in yrProject: the shared rules of this template version), and `CLAUDE.md`, which imports it; and the `yrProject` skill, which checks, updates and removes this setup for you (ask the agent), with the notice script `yrProject-notice.sh`. A SessionStart hook runs it: it shows the facts of this setup at the start of each Claude Code session, and the agent gives them in its first reply. The Claude Code status line can show the version `yrProject VERSION [latest ...]` (`yrProject.sh statusline-setup`, once on each computer). Also the `yrUpdateDocsSkillsRulesEtc` skill: before a push, and before you leave a chat, the agent updates the docs, the skills and the rules to reflect what was done and decided in the chat, and records the review (a marker in `.git/`); a PreToolUse hook refuses `git push` until it did, and a SessionStart hook names the earlier chat to read after `/clear`.
- **yrIssues**: work to do later is the GitHub issues of the project. The `yrIssues` skill manages them (its settings: `_yrIssues/config.sh`; the issues that it creates get the label `yrIssue`), a SessionStart hook shows how many are open, and a PostToolUse hook keeps the saved copy `_yrIssues/issues.md` up to date.
- **subjexts**: the subjexts teaching overlay for this book (labels, a table of contents by label, in-place edits, the tutor): its include file `subjexts-v001.html` and its page `subjexts-labels-v001.qmd` in a Quarto book, or the page `jb/subjexts-labels.md` in a Jupyter Book (their content is the platform's, from `book-files/` in the yrS4 repository; only the package name is this book's), and the `subjexts` skill, which explains them and, through its script `yrS4-skill.sh`, refers to the subjexts procedures in the yrS4 repository (apply a note packet, mark the book, register it) instead of carrying copies.

## The files

| File | Part | Who changes it |
|---|---|---|
| `AGENTS.md` | rules | You: the project rules. The tool: only its two blocks, "yrProject setup" and "shared rules" |
| `CLAUDE.md` | rules | You. The tool only keeps the line `@AGENTS.md` |
| `.claude/settings.json` | rules, yrIssues | You. The tool only adds its hooks, and removes the hooks of older versions |
| `README.md` |  | You. The tool only writes its block "yrProject setup" at the end |
| `.gitignore` | yrIssues | You. The tool only writes its block "yrProject" (the files that git ignores) |
| `.claude/skills/subjexts/SKILL.md` | subjexts | The tool: `update` replaces it with each new version. If you change it, `update` leaves it alone |
| `.claude/skills/subjexts/scripts/yrS4-skill.sh` | subjexts | The tool: `update` replaces it with each new version. If you change it, `update` leaves it alone |
| `.claude/skills/yrIssues/SKILL.md` | yrIssues | The tool: `update` replaces it with each new version. If you change it, `update` leaves it alone |
| `.claude/skills/yrIssues/scripts/yrIssues.sh` | yrIssues | The tool: `update` replaces it with each new version. If you change it, `update` leaves it alone |
| `.claude/skills/yrProject/SKILL.md` | rules | The tool: `update` replaces it with each new version. If you change it, `update` leaves it alone |
| `.claude/skills/yrProject/scripts/yrProject-notice.sh` | rules | The tool: `update` replaces it with each new version. If you change it, `update` leaves it alone |
| `.claude/skills/yrUpdateDocsSkillsRulesEtc/SKILL.md` | rules | The tool: `update` replaces it with each new version. If you change it, `update` leaves it alone |
| `.claude/skills/yrUpdateDocsSkillsRulesEtc/scripts/yrUpdateDocsSkillsRulesEtc.sh` | rules | The tool: `update` replaces it with each new version. If you change it, `update` leaves it alone |
| `_yrIssues/config.sh` | yrIssues | You. The tool added it once, and does not change it |
| `jb/subjexts-labels.md` | subjexts | The tool: `update` replaces it with each new version. If you change it, `update` leaves it alone |
| `.yrProject/` |  | The tool only: `manifest.json` (the record), `README.md` (this page), `setup.env` (the facts, for the scripts). Do not edit |

## How to change things

- **Project rules:** edit `AGENTS.md`, outside the two blocks of the tool.
- **Shared rules:** they belong to the template version. A change to them comes in a new yrProject version: `yrProject.sh update` brings it to this project.
- **A file of the tool** (a skill, a guide): you can change it. Then `update` leaves it alone, and the file gets no newer versions. `yrProject.sh status` lists such files.
- **The blocks of the tool** (in `AGENTS.md`, `README.md` and `.gitignore`): do not edit them. `yrProject.sh update` writes them again, with the current version. If you change a block, `update` leaves that block alone and reports it. To get the new block: move your text out of the block, delete the block (from its begin line to its end line), and run `update` again.
- **To take yrProject out of this project:** ask the agent, or run `yrProject.sh remove` (it shows what would go, and asks).
- **Without `yrProject.sh`** (for example, a collaborator): all these files are ordinary files. Change the files of the tool only if you must, and tell the project owner.

## Commands

You do not need them: ask the agent, for example "check the project setup" or "update the project" (the `yrProject` skill). The commands that it runs:

```bash
yrProject.sh check              # is the project set up correctly for its version?
yrProject.sh status             # is the project up to date? which files were changed by hand?
yrProject.sh update --dry-run   # what update would change (changes nothing)
yrProject.sh update             # update the project (shows the changes, then asks)
yrProject.sh remove --dry-run   # what remove would take out (changes nothing)
yrProject.sh projects           # the list of projects that use yrProject, from any folder
```

`yrProject.sh` is in the Dropbox tools folder of the project owner. `yrProject.sh --help` explains it.

## History

| Date | Command | Template | Parts |
|---|---|---|---|
| 2026-10-12 | set up (no history before v0.4.0) |  |  |
| 2026-10-12 | update | v0.4.0 | rules |
| 2026-10-18 | update | v0.5.0 | rules, yrIssues |
| 2026-10-18 | update | v0.5.0 | rules, yrIssues |
| 2026-10-18 | update | v0.5.1 | rules, yrIssues |
| 2026-10-28 | update | v0.5.2 | rules, yrIssues, subjexts |
| 2026-10-29 | update | v0.6.0 | rules, yrIssues, subjexts |
| 2026-10-29 | update | v0.6.0 | rules, yrIssues, subjexts |
| 2026-10-29 | update | v0.6.1 | rules, yrIssues, subjexts |
| 2026-10-29 | update | v0.7.0 | rules, yrIssues, subjexts |
| 2026-10-29 | update | v0.7.1 | rules, yrIssues, subjexts |
| 2026-10-30 | update | v0.7.2 | rules, yrIssues, subjexts |
| 2026-11-03 | update | v0.7.4 | rules, yrIssues, subjexts |
| 2026-11-03 | update | v0.7.5 | rules, yrIssues, subjexts |
| 2026-11-04 | update | v0.8.0 | rules, yrIssues, subjexts |
| 2026-11-04 | update | v0.8.1 | rules, yrIssues, subjexts |
| 2026-11-04 | update | v0.9.1 | rules, yrIssues, subjexts |
| 2026-11-04 | update | v0.9.2 | rules, yrIssues, subjexts |
