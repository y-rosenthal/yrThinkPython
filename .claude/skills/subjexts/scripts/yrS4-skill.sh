#!/usr/bin/env bash
# Installed by yrProject v0.6.0 (https://github.com/y-rosenthal/yrProject): the templates and
# the tool that give a project one base for AI-assisted work (rules for AI agents, skills, hooks, GitHub issues
# for work to do later, project docs). This file belongs to the tool: do not edit it by hand, and do not change
# it without the tool. "yrProject.sh update" replaces it with each new version (if you change it, update leaves
# it alone, and it gets no newer versions); "yrProject.sh remove" removes it. .yrProject/README.md lists every
# file that yrProject installed, and tells who changes each one.
#
# yrS4-skill.sh: find a subjexts skill in the yrS4 repository (the subjexts platform), so that this book repo refers
# to the one copy of each procedure instead of carrying copies that go out of date.
#
# Usage: bash .claude/skills/subjexts/scripts/yrS4-skill.sh [-h|--help] [--cat] [--dir] [NAME]
#
#   NAME     The skill: apply-notes, mark-book, plug-in-book, dev-test or release (the "subjexts-" prefix may be
#            left out). Prints the full path of its SKILL.md; with --cat, prints the file itself.
#   --dir    Print the yrS4 repository's folder and stop.
#   (none)   List the skills that yrS4 has.
#
# Where yrS4 is: $YRS4_DIR if set; else the Dropbox tree this project is in (DROPBOX/_yrAiCoding/yrS4, found by
# walking up from this folder); else ~/Dropbox/_yrAiCoding/yrS4. Exit 1 with a clear message when it is not there:
# then clone https://github.com/subjexts/yrS4 (private) and set YRS4_DIR, or work from a computer that has Dropbox.
set -euo pipefail
case "${1:-}" in -h|--help) sed -n '2,/^[^#]/{/^#/s/^# \{0,1\}//p}' "$0"; exit 0 ;; esac

find_yrs4() {
  if [ -n "${YRS4_DIR:-}" ]; then printf '%s\n' "$YRS4_DIR"; return; fi
  local d; d="$(cd "$(dirname "$0")" && pwd)"
  while [ "$d" != "/" ]; do
    if [ -d "$d/_yrAiCoding/yrS4/skills" ]; then printf '%s\n' "$d/_yrAiCoding/yrS4"; return; fi
    d="$(dirname "$d")"
  done
  printf '%s\n' "$HOME/Dropbox/_yrAiCoding/yrS4"
}
YRS4="$(find_yrs4)"
if [ ! -d "$YRS4/skills" ]; then
  echo "yrS4-skill: the yrS4 repository is not at $YRS4 (no skills/ folder there)." >&2
  echo "  It holds the subjexts procedures this book refers to. Clone git@github.com:subjexts/yrS4.git and set" >&2
  echo "  YRS4_DIR to its folder, or use a computer with the Dropbox tree (DROPBOX/_yrAiCoding/yrS4)." >&2
  exit 1
fi
CAT=0; DIR=0; NAME=""
for a in "$@"; do
  case "$a" in
    --cat) CAT=1 ;;
    --dir) DIR=1 ;;
    -*) echo "yrS4-skill: unknown option $a (try --help)" >&2; exit 2 ;;
    *) NAME="$a" ;;
  esac
done
[ "$DIR" = 1 ] && { printf '%s\n' "$YRS4"; exit 0; }
if [ -z "$NAME" ]; then
  echo "skills in $YRS4/skills:"
  for d in "$YRS4"/skills/subjexts-*/; do
    n="$(basename "$d")"
    printf '  %-26s %s\n' "${n#subjexts-}" "$(sed -n 's/^description: //p' "$d/SKILL.md" | cut -c1-90)"
  done
  exit 0
fi
NAME="${NAME#subjexts-}"
FILE="$YRS4/skills/subjexts-$NAME/SKILL.md"
if [ ! -f "$FILE" ]; then
  echo "yrS4-skill: no skill subjexts-$NAME in $YRS4/skills (run without a name to list them)" >&2
  exit 1
fi
if [ "$CAT" = 1 ]; then cat "$FILE"; else printf '%s\n' "$FILE"; fi
