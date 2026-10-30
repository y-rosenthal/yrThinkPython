#!/usr/bin/env bash
# Installed by yrProject v0.7.2 (https://github.com/y-rosenthal/yrProject): the templates and
# the tool that give a project one base for AI-assisted work (rules for AI agents, skills, hooks, GitHub issues
# for work to do later, project docs). This file belongs to the tool: do not edit it by hand, and do not change
# it without the tool. "yrProject.sh update" replaces it with each new version (if you change it, update leaves
# it alone, and it gets no newer versions); "yrProject.sh remove" removes it. .yrProject/README.md lists every
# file that yrProject installed, and tells who changes each one.
#
# yrProject-notice.sh - the notice of this project's yrProject setup: the version line that every reply of an
# agent starts with, the facts for the first reply of a session (the type, the installed parts, the parts not
# installed), and the JSON of the two Claude Code hooks (SessionStart and UserPromptSubmit). It reads
# .yrProject/setup.env, which yrProject.sh writes.
#
# Usage: bash yrProject-notice.sh [COMMAND]
#   version        (the default) the line that every reply of an agent starts with, for example
#                  "(yrProject v0.6.0 [latest])", "(yrProject v0.5.2 [latest v0.6.0])" or
#                  "(yrProject v0.5.2 [latest UNKNOWN])"
#   facts          the facts for the first reply of a session, one per line, each starting with "yrProject: ":
#                  the version line, the type with the installed parts and the parts not installed, and how to
#                  look after the setup. In the yrProject repository itself: also the projects that use yrProject
#   latest         the newest version of yrProject, or UNKNOWN (how it is found: below)
#   session-start  the JSON for the SessionStart hook: the facts for the user, the instructions for the agent
#   prompt         the JSON for the UserPromptSubmit hook: the version line, for the user and for the agent
#   -h, --help     show this help and stop
#
# The newest version is the newest version folder in templates/ of the yrProject repository on this computer:
# $YRPROJECT_DIR, else _yrAiCoding/yrProject in the Dropbox folder above this project, else
# ~/Dropbox/_yrAiCoding/yrProject. Without that repository, it is the newest tag templates-vX.Y.Z of the GitHub
# repository (git ls-remote, at most 8 seconds, never a password prompt), kept for a day in
# ~/.cache/yrProject/latest (an hour after a failure). "prompt" runs at every prompt, so it never goes to the
# network: it uses the repository on this computer, or the kept answer, else UNKNOWN.
# Without .yrProject/setup.env (no yrProject setup), session-start and prompt print nothing and exit 0; the other
# commands say so and exit 1. Only bash, git and the usual commands are needed, so this also works in Git Bash on
# Windows.

set -uo pipefail
case "${1:-}" in -h|--help) sed -n '2,/^[^#]/{/^#/s/^# \{0,1\}//p}' "$0"; exit 0 ;; esac

REPO_URL="https://github.com/y-rosenthal/yrProject"
SKILL=".claude/skills/yrProject/SKILL.md"
cache="${XDG_CACHE_HOME:-$HOME/.cache}/yrProject/latest"

here="$(cd "$(dirname "$0")" && pwd)"
root="${CLAUDE_PROJECT_DIR:-}"
[ -n "$root" ] && [ -d "$root" ] || root="$(git -C "$here" rev-parse --show-toplevel 2>/dev/null || pwd)"
env_file="$root/.yrProject/setup.env"
cmd="${1:-version}"

YRPROJECT_VERSION=""; YRPROJECT_TYPE=""; YRPROJECT_PARTS=""; YRPROJECT_PARTS_NOT=""
# shellcheck source=/dev/null
[ -f "$env_file" ] && . "$env_file"
if [ -z "$YRPROJECT_VERSION" ]; then
  case "$cmd" in session-start|prompt) exit 0 ;; esac
  echo "yrProject-notice.sh: $env_file not found: this folder has no yrProject setup (yrProject.sh update sets one up)" >&2
  exit 1
fi

# A JSON string literal for a shell string (also with line breaks).
json_str() { printf '"%s"' "$(printf '%s' "$1" | sed 's/\\/\\\\/g; s/"/\\"/g' | sed ':a;N;$!ba;s/\n/\\n/g')"; }

# The yrProject repository on this computer, or status 1.
yrproject_dir() {
  local d up
  if [ -n "${YRPROJECT_DIR:-}" ] && [ -d "$YRPROJECT_DIR/templates" ]; then printf '%s\n' "$YRPROJECT_DIR"; return 0; fi
  d="$root"
  while [ -n "$d" ]; do
    if [ -d "$d/_yrAiCoding/yrProject/templates" ]; then printf '%s\n' "$d/_yrAiCoding/yrProject"; return 0; fi
    up="$(dirname "$d")"
    [ "$up" = "$d" ] && break
    d="$up"
  done
  if [ -d "$HOME/Dropbox/_yrAiCoding/yrProject/templates" ]; then printf '%s\n' "$HOME/Dropbox/_yrAiCoding/yrProject"; return 0; fi
  return 1
}

newest_of() { grep -E '^v[0-9]+\.[0-9]+\.[0-9]+$' | sort -V | tail -n 1; }

local_latest() {
  local d
  d="$(yrproject_dir)" || return 1
  ls "$d/templates" 2>/dev/null | newest_of
}

# The newest tag on GitHub, from the kept answer if it is younger than $1 seconds ("cached": only the kept
# answer, no network). UNKNOWN if GitHub could not be read.
remote_latest() {
  local max="$1" now v stamp tags
  now="$(date +%s)"
  if [ -f "$cache" ]; then
    read -r v stamp < "$cache" || true
    if [ -n "${v:-}" ] && { [ "$max" = cached ] || [ $((now - ${stamp:-0})) -lt "$max" ]; }; then
      printf '%s\n' "$v"; return 0
    fi
  fi
  [ "$max" = cached ] && { echo UNKNOWN; return 0; }
  if command -v timeout >/dev/null 2>&1; then
    tags="$(GIT_TERMINAL_PROMPT=0 timeout 8 git ls-remote --tags "$REPO_URL.git" 'refs/tags/templates-v*' 2>/dev/null)"
  else
    tags="$(GIT_TERMINAL_PROMPT=0 git ls-remote --tags "$REPO_URL.git" 'refs/tags/templates-v*' 2>/dev/null)"
  fi
  v="$(printf '%s\n' "$tags" | sed -nE 's#.*refs/tags/templates-(v[0-9]+\.[0-9]+\.[0-9]+)$#\1#p' | newest_of)"
  mkdir -p "$(dirname "$cache")" 2>/dev/null || true
  if [ -n "$v" ]; then
    printf '%s %s\n' "$v" "$now" > "$cache" 2>/dev/null || true
  else
    v=UNKNOWN
    printf '%s %s\n' "$v" "$((now - 86400 + 3600))" > "$cache" 2>/dev/null || true   # ask again in an hour
  fi
  printf '%s\n' "$v"
}

latest() {        # $1: the max age of the kept GitHub answer in seconds, or "cached"
  local v
  v="$(local_latest)"
  [ -n "$v" ] || v="$(remote_latest "${1:-86400}")"
  [ -n "$v" ] || v=UNKNOWN
  printf '%s\n' "$v"
}

version_line() {  # $1 as for latest
  local l
  l="$(latest "$1")"
  if [ "$l" = "$YRPROJECT_VERSION" ]; then
    printf '(yrProject %s [latest])\n' "$YRPROJECT_VERSION"
  else
    printf '(yrProject %s [latest %s])\n' "$YRPROJECT_VERSION" "$l"
  fi
}

setup_line() {
  local not="$YRPROJECT_PARTS_NOT"
  printf 'yrProject: type: %s; installed: %s; not installed: %s\n' "$YRPROJECT_TYPE" "$YRPROJECT_PARTS" "${not:-none}"
}

# The projects that use yrProject (projects/*.json), when this project is the yrProject repository itself.
is_yrproject_repo() { [ -f "$root/bin/yrProject.py" ] && [ -d "$root/projects" ]; }

projects_line() {
  local f name version removed l current="" gone=""
  l="$(latest cached)"
  for f in "$root"/projects/*.json; do
    [ -f "$f" ] || continue
    name="$(sed -nE 's/^ *"name": *"(.*)",?$/\1/p' "$f" | head -n 1)"
    version="$(sed -nE 's/^ *"version": *"(.*)",?$/\1/p' "$f" | head -n 1)"
    removed="$(sed -nE 's/^ *"removed": *"(.*)",?$/\1/p' "$f" | head -n 1)"
    if [ -n "$removed" ]; then
      gone="$gone${gone:+, }$name ($version, removed $removed)"
    elif [ "$l" != UNKNOWN ] && [ "$version" != "$l" ]; then
      current="$current${current:+, }$name $version (older)"
    else
      current="$current${current:+, }$name $version"
    fi
  done
  printf 'yrProject: the projects that use yrProject: %s%s\n' "${current:-none}" "${gone:+; removed: $gone}"
}

facts() {         # $1 as for latest
  local v
  v="$(version_line "$1")"
  printf 'yrProject: %s\n' "${v#(yrProject }" | sed 's/)$//'
  setup_line
  echo "yrProject: to check, update or remove the setup, ask the agent. Before you change its files, read .yrProject/README.md."
  is_yrproject_repo && projects_line
  return 0
}

case "$cmd" in
  version) version_line 86400 ;;
  latest)  latest 86400 ;;
  facts)   facts 86400 ;;

  session-start)
    line="$(version_line 86400)"
    user_msg="$(facts cached)"
    context="This project was set up by yrProject.sh (yrProject $YRPROJECT_VERSION; type: $YRPROJECT_TYPE; installed parts: $YRPROJECT_PARTS; not installed: ${YRPROJECT_PARTS_NOT:-none}; the newest version of yrProject: $(latest cached)). The user saw these facts in a notice, but Claude Code does not always show it, so: start EVERY reply with the line \"$line\" (a UserPromptSubmit hook repeats it to you at each prompt), and in your FIRST reply of the session also give, right after that line, one line that starts with \"yrProject:\" with the type, the installed parts and the parts not installed, as the notice has it. .yrProject/README.md lists the files that the tool installed, and tells who changes each one; every such file starts with a comment that names yrProject and its version. Read it before you change AGENTS.md, CLAUDE.md, .gitignore, .claude/settings.json, a file in .claude/skills/, or the docs guides. Do not edit the tool's blocks in AGENTS.md, README.md and .gitignore, or the files in .yrProject/: \"yrProject.sh update\" writes them again. When the user asks to check, update, migrate or remove the yrProject setup, or about the list of yrProjects, follow the yrProject skill ($SKILL); the user does not need to know the commands. The word \"project\" alone does not mean the yrProject setup: unless the user says yrProject or it is obvious, ask what they mean."
    if is_yrproject_repo; then
      context="$context This is the yrProject repository itself. $(projects_line | sed 's/^yrProject: //'). In your first reply, also say which of them are older than the newest version."
    fi
    printf '{"systemMessage": %s, "hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": %s}}\n' \
      "$(json_str "$user_msg")" "$(json_str "$context")"
    ;;

  prompt)
    line="$(version_line cached)"
    user_msg="yrProject: ${line#(yrProject }"
    user_msg="${user_msg%)}"
    context="Start your reply with the line \"$line\" (the yrProject setup of this project; its skill: $SKILL)."
    printf '{"systemMessage": %s, "hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext": %s}}\n' \
      "$(json_str "$user_msg")" "$(json_str "$context")"
    ;;

  *)
    echo "yrProject-notice.sh: unknown command '$cmd' (see --help)" >&2
    exit 2
    ;;
esac
