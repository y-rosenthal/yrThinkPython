#!/usr/bin/env bash
# Installed by yrProject v0.9.2 (https://github.com/y-rosenthal/yrProject): the templates and
# the tool that give a project one base for AI-assisted work (rules for AI agents, skills, hooks, GitHub issues
# for work to do later, project docs). This file belongs to the tool: do not edit it by hand, and do not change
# it without the tool. "yrProject.sh update" replaces it with each new version (if you change it, update leaves
# it alone, and it gets no newer versions); "yrProject.sh remove" removes it.
# This repository uses yrProject. What yrProject is, which files come from it and which belong to this repository:
# .yrProject/README.md. The yrProject version and the installed parts, with bash and git only:
#   bash .claude/skills/yrProject/scripts/yrProject-notice.sh facts
#
# yrUpdateDocsSkillsRulesEtc.sh - the hooks of the yrUpdateDocsSkillsRulesEtc skill: the agent updates the
# project's docs, skills and rules before a push and before the user leaves a chat (see SKILL.md). The review is
# recorded as the marker file docs-reviewed in .git/ (never committed); the review is current when no file that
# git does not ignore changed after the marker.
#
# Usage: bash yrUpdateDocsSkillsRulesEtc.sh COMMAND
#   check          for the PreToolUse hook on Bash: reads the hook's JSON on stdin. If the command runs "git push"
#                  and the review is not current, prints why on stderr and exits 2 (Claude Code then refuses the
#                  command and shows the agent the reason). Otherwise prints nothing and exits 0
#   done           record the review now (touch the marker). The skill runs it after its edits
#   status         "current" (exit 0), or "files changed since the docs, skills and rules were last updated" and
#                  the first such file (exit 1)
#   session-start  JSON for the SessionStart hook, when the review is not current: a line for the user, and for
#                  the agent the chat to read: the transcript (in the folder of the current transcript, from the
#                  hook's JSON) that holds one of the last five commit hashes, or else the newest other one.
#                  Prints nothing when the review is current
#   -h, --help     show this help and stop
#
# Only bash and git are needed, so this also works in Git Bash on Windows. Outside a git repository, every
# command prints nothing and exits 0 (there is nothing to track).

set -uo pipefail
case "${1:-}" in -h|--help) sed -n '2,/^[^#]/{/^#/s/^# \{0,1\}//p}' "$0"; exit 0 ;; esac

SKILL=".claude/skills/yrUpdateDocsSkillsRulesEtc/SKILL.md"
NAME="yrUpdateDocsSkillsRulesEtc"
cmd="${1:-status}"
input=""
case "$cmd" in check|session-start) input="$(cat)" ;; esac

here="$(cd "$(dirname "$0")" && pwd)"
root="${CLAUDE_PROJECT_DIR:-}"
[ -n "$root" ] && [ -d "$root" ] || root="$(git -C "$here" rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$root" || exit 0
gitdir="$(git rev-parse --git-dir 2>/dev/null)" || exit 0
marker="$gitdir/docs-reviewed"

json_str() { printf '"%s"' "$(printf '%s' "$1" | sed 's/\\/\\\\/g; s/"/\\"/g' | sed ':a;N;$!ba;s/\n/\\n/g')"; }
field() { printf '%s' "$input" | sed -n "s/.*\"$1\": *\"\([^\"]*\)\".*/\1/p" | head -n 1; }

# The first file that git does not ignore and that changed after the marker; nothing if the review is current.
changed_since() {
  [ -f "$marker" ] || { echo "(no review recorded yet)"; return; }
  git ls-files -co --exclude-standard -z | xargs -0 -r sh -c 'find "$@" -newer "$0" -print -quit 2>/dev/null' "$marker"
}

case "$cmd" in
  status)
    f="$(changed_since)"
    if [ -z "$f" ]; then echo "current: no file changed since the docs, skills and rules were last updated"; exit 0; fi
    echo "files changed since the docs, skills and rules were last updated: $f ..."; exit 1 ;;

  done)
    touch "$marker" && echo "recorded: the docs, skills and rules were reviewed now ($marker)" ;;

  check)
    printf '%s' "$input" | grep -Eq 'git[[:space:]]+push' || exit 0
    [ -n "$(changed_since)" ] || exit 0
    echo "yrProject: files changed since the docs, skills and rules were last updated. Follow the $NAME skill ($SKILL) first, then push again. If the user said to skip the review: bash .claude/skills/yrUpdateDocsSkillsRulesEtc/scripts/yrUpdateDocsSkillsRulesEtc.sh done, then push." >&2
    exit 2 ;;

  session-start)
    [ -n "$(changed_since)" ] || exit 0
    tp="$(field transcript_path)"
    file=""; hash=""
    if [ -n "$tp" ] && [ -d "$(dirname "$tp")" ]; then
      for h in $(git log -5 --format=%h 2>/dev/null); do
        f="$(grep -ls -- "$h" "$(dirname "$tp")"/*.jsonl 2>/dev/null | grep -vF "$tp" | head -n 1)"
        [ -n "$f" ] && { file="$f"; hash="$h"; break; }
      done
    fi
    if [ -n "$file" ]; then
      where="The chat that made commit $hash is $file: /resume brings it back, or read the lines whose \"type\" is \"user\" or \"assistant\" (the text is in message.content)."
      user_msg="yrProject: files changed since the docs, skills and rules were last updated. Say \"update the docs\"; the chat that made commit $hash can be brought back with /resume."
    else
      where="No saved chat holds one of the last five commit hashes (the commits were quiet, or made outside Claude); /resume lists the recent chats."
      user_msg="yrProject: files changed since the docs, skills and rules were last updated. Say \"update the docs\"."
    fi
    context="DOCS: files changed since the docs, skills and rules were last updated (the $NAME skill, $SKILL). In your FIRST reply, offer the review in one short line, unless the user is already asking for it. $where Then follow the skill."
    printf '{"systemMessage": %s, "hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": %s}}\n' \
      "$(json_str "$user_msg")" "$(json_str "$context")" ;;

  *) echo "usage: bash $NAME.sh {check|done|status|session-start|--help}" >&2; exit 2 ;;
esac
