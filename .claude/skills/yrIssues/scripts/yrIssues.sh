#!/usr/bin/env bash
# yrIssues.sh - helper for the yrIssues skill of yrProject: work to do later, kept as GitHub issues.
#
# The project's work to do later is the open GitHub issues of its repository (the "origin" remote). The user
# never has to use GitHub directly: the agent adds, lists and closes issues with the `gh` command (see SKILL.md).
# Each issue that the agent creates gets the label yrIssue, which shows that it came from this skill.
#
# Usage: bash yrIssues.sh COMMAND
#   session-start   JSON for the SessionStart hook: makes gh use this project's repository (see below), refreshes
#                   the saved copy (COPY), shows the user how many
#                   issues are open (by priority), and tells the agent to offer to list them. The list itself is
#                   not loaded, to save context
#   list            the open issues, one per line, highest priority first (the default command)
#   sync            refresh the saved copy (COPY) from GitHub. It writes the file only if an issue changed
#   hook-sync       for the PostToolUse hook: reads the hook's JSON on stdin, and runs sync if the command was a
#                   gh command that changes issues (create, edit, close, reopen, delete, transfer). Prints nothing
#   setup-labels    create or update the labels: yrIssue, the categories and the priorities (safe to repeat).
#                   It renames the label pending-work (before v0.5.0) to yrIssue, so its issues keep it
#   -h, --help      show this help and stop
#
# Files in the project folder:
#   _yrIssues/config.sh   the project's settings (the project owns this file; this script reads it):
#                         CATEGORIES  the category labels, "name|color|description" (default: fix, improvement,
#                                     decision, recheck)
#                         LABEL       if set, only the open issues with this label count, for example yrIssue
#                                     (default: "", every open issue)
#   _yrIssues/issues.md   COPY: the saved copy of the open issues, for when GitHub can't be reached. Don't edit it
#   _yrIssues/queue.md    QUEUE: issues written while GitHub could not be reached (headings "### [priority] Title")
#
# gh and this project's repository: in a clone that also has an "upstream" remote (for example a copy of someone
# else's repository), gh uses the upstream repository unless a default is set. So session-start and setup-labels
# set gh's default to the origin repository (gh repo set-default), if no default is set yet. That changes only
# this folder's git config, nothing on GitHub; then every plain gh command uses this project's repository.
#
# Only bash and gh are needed (gh has jq built in), so this also works in Git Bash on Windows.
# If gh is missing, not logged in, or GitHub can't be reached, session-start and list use COPY and QUEUE.

set -uo pipefail
case "${1:-}" in -h|--help) sed -n '2,/^[^#]/{/^#/s/^# \{0,1\}//p}' "$0"; exit 0 ;; esac

MARK="yrIssue"                  # the label of the issues that this skill creates
OLD_MARK="pending-work"         # its name before v0.5.0
COPY="_yrIssues/issues.md"
QUEUE="_yrIssues/queue.md"
CONFIG="_yrIssues/config.sh"

here="$(cd "$(dirname "$0")" && pwd)"
root="${CLAUDE_PROJECT_DIR:-}"
[ -n "$root" ] && [ -d "$root" ] || root="$(git -C "$here" rev-parse --show-toplevel 2>/dev/null || pwd)"
copy="$root/$COPY"
queue="$root/$QUEUE"

# The defaults; _yrIssues/config.sh can change them.
CATEGORIES=(
  "fix|D93F0B|Something is wrong and needs fixing"
  "improvement|0E8A16|New or better content or features"
  "decision|5319E7|Needs the owner's decision"
  "recheck|1D76DB|Time-sensitive fact to re-verify"
)
LABEL=""
# shellcheck source=/dev/null
[ -f "$root/$CONFIG" ] && . "$root/$CONFIG"

# owner/repo from the git remote (no network needed)
remote_url="$(git -C "$root" remote get-url origin 2>/dev/null || true)"
repo="$(printf '%s' "$remote_url" | sed -E 's#(\.git)?/*$##; s#^.*github\.com[:/]##')"
case "$remote_url" in *github.com*) ;; *) repo="" ;; esac

gh_bin="$(command -v gh || true)"
[ -z "$gh_bin" ] && [ -x /snap/bin/gh ] && gh_bin=/snap/bin/gh

run_gh() {
  if [ -z "$gh_bin" ] || [ -z "$repo" ]; then return 127; fi
  if command -v timeout >/dev/null 2>&1; then
    timeout 20 "$gh_bin" "$@"
  else
    "$gh_bin" "$@"
  fi
}

# Make plain gh commands use the origin repository, if gh has no default repository here yet.
ensure_gh_default() {
  [ -n "$gh_bin" ] && [ -n "$repo" ] || return 0
  if [ -z "$(cd "$root" && "$gh_bin" repo set-default --view 2>/dev/null)" ]; then
    (cd "$root" && "$gh_bin" repo set-default "$repo" >/dev/null 2>&1) || true
  fi
}

# A jq string literal for a shell string (gh's --jq has no --arg option).
jq_lit() { printf '"%s"' "$(printf '%s' "$1" | sed 's/\\/\\\\/g; s/"/\\"/g')"; }

# Which issues count: every open issue, or only those with LABEL.
filter=(--state open --limit 200)
[ -n "$LABEL" ] && filter+=(--label "$LABEL")

# jq helpers shared by the commands below (gh's built-in jq)
JQ_DEFS='
def prio: ([.labels[].name | select(startswith("priority: ")) | ltrimstr("priority: ")] | first) // "-";
def rank: ({"high": 0, "medium": 1, "low": 2}[prio]) // 3;
def cats: [.labels[].name | select(. != '"$(jq_lit "$MARK")"' and . != '"$(jq_lit "$OLD_MARK")"' and (startswith("priority: ") | not))] | join(", ");
def ordered: sort_by([rank, .number]);
'

# What the agent is told at the start of a session. COUNT is replaced by the count line.
INSTRUCTIONS='Instructions for the agent: the list itself was not loaded, to save context. The user may not have seen the count on screen (Claude Code does not always show this message, for example after /clear), so in your FIRST reply add one short line, for example "You have COUNT. Want me to list them?". Skip it only if the user is already asking about issues. Do not list the issues unless the user asks; then run `bash .claude/skills/yrIssues/scripts/yrIssues.sh list` and show one line per issue (number, priority, title). The user just talks to you: do the GitHub work for them. To see details, add, change or close issues, follow the yrIssues skill (.claude/skills/yrIssues/SKILL.md).'

saved_list() {
  # Print the open issues from the saved copy, and the issues queued offline.
  local found=0
  if [ -f "$copy" ]; then
    grep -E '^### #[0-9]+' "$copy" | sed -E 's/^### //' && found=1
  fi
  if [ -f "$queue" ]; then
    grep -E '^### ' "$queue" | sed -E 's/^### /(not yet on GitHub) /' && found=1
  fi
  [ "$found" -eq 1 ]
}

# "N open issues (H high, M medium, L low)" from lines like "#12 [high] Title"
count_line() {
  awk '
    { n++; if (match($0, /\[[a-z-]+\]/)) p[substr($0, RSTART + 1, RLENGTH - 2)]++ }
    END {
      if (n == 0) { print "no open issues"; exit }
      s = n " open issue" (n == 1 ? "" : "s"); d = ""
      split("high medium low", order, " ")
      for (i = 1; i <= 3; i++) if (p[order[i]]) d = d (d ? ", " : "") p[order[i]] " " order[i]
      print s (d ? " (" d ")" : "")
    }'
}

# Refresh the saved copy from GitHub (one request). It writes the file only if its text changes, so an unchanged
# list leaves git clean. Sets $synced to "updated" or "unchanged"; status 1 if GitHub could not be read.
synced=""
sync_copy() {
  local body text which=""
  body="$(run_gh issue list --repo "$repo" "${filter[@]}" --json number,title,labels,body,createdAt,url \
    --jq "$JQ_DEFS"'
      "## Open issues (\(length))\n\n" +
      (ordered | map("### #\(.number) [\(prio)] \(.title)\n\nCategory: \(cats) · Opened: \(.createdAt[0:10]) · \(.url)\n\n\(.body)\n\n---\n") | join("\n"))' \
    2>/dev/null | tr -d '\r')" || return 1
  [ -n "$body" ] || return 1
  [ -n "$LABEL" ] && which=", only the issues with the label \`$LABEL\`"
  text="# Issues

<!-- Written by .claude/skills/yrIssues/scripts/yrIssues.sh (sync). Don't edit it: the next sync replaces it. -->

This is a saved copy of the open GitHub issues of this project (repository \`$repo\`$which).
It is refreshed at the start of each Claude Code session and after each change to an issue, and it is used
when GitHub can't be reached. You never need to use GitHub yourself: tell the agent, for example
\"add an issue: ...\", \"list issues\", \"let's work on #12\", or \"#12 is no longer needed\".

$body"
  if [ -f "$copy" ] && [ "$(cat "$copy")" = "$text" ]; then
    synced=unchanged
    return 0
  fi
  mkdir -p "$(dirname "$copy")"
  printf '%s\n' "$text" > "$copy"
  synced=updated
}

cmd="${1:-list}"
case "$cmd" in

  session-start)
    ensure_gh_default
    note=""
    if ! sync_copy; then
      if [ -n "$repo" ]; then
        note=" GitHub could not be reached, so the count comes from the saved copy ($COPY) and may be out of date."
      else
        note=" This project has no GitHub repository yet, so the count comes from $QUEUE."
      fi
    fi
    if [ -f "$queue" ] && grep -qE '^### ' "$queue"; then
      note="$note Some issues are in $QUEUE and not yet on GitHub: when gh works, create them (yrIssues skill)."
    fi
    count="$(saved_list | count_line)"
    if [ "$count" = "no open issues" ]; then
      user_msg="No open issues."
      context="Issues of this project: none open.$note If the user mentions something to do later, offer to add it as an issue (yrIssues skill)."
    else
      user_msg="$count. Say \"list issues\" to see them."
      context="ISSUES: this project has $count (GitHub issues${repo:+ in $repo}).$note ${INSTRUCTIONS//COUNT/$count}"
    fi
    printf '{"systemMessage": %s, "hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": %s}}\n' \
      "$(jq_lit "$user_msg")" "$(jq_lit "$context")"
    ;;

  list)
    out="$(run_gh issue list --repo "$repo" "${filter[@]}" --json number,title,labels \
      --jq "$JQ_DEFS"' ordered | .[] | "#\(.number) [\(prio)] \(.title)  (\(cats))"' 2>/dev/null)"
    status=$?
    if [ $status -eq 0 ] && [ -n "$out" ]; then
      printf '%s\n' "$out"
    elif [ $status -eq 0 ]; then
      echo "No open issues."
      if [ -f "$queue" ]; then grep -E '^### ' "$queue" | sed -E 's/^### /(not yet on GitHub) /'; fi
    else
      if [ -n "$repo" ]; then echo "(GitHub unreachable - showing the saved copy in $COPY)"
      else echo "(no GitHub repository - showing the issues queued in $QUEUE)"; fi
      saved_list || echo "(no saved list found)"
    fi
    ;;

  sync)
    if ! sync_copy; then
      echo "sync: could not read the issues from GitHub; $copy was not changed." >&2
      exit 1
    fi
    echo "$COPY: $synced"
    ;;

  hook-sync)
    input="$(cat)"
    if printf '%s' "$input" | grep -Eq 'gh issue (create|new|edit|close|reopen|delete|transfer)\b'; then
      sync_copy >/dev/null 2>&1 || true
    fi
    exit 0
    ;;

  setup-labels)
    if [ -z "$repo" ]; then echo "setup-labels: no GitHub repository (git remote origin)" >&2; exit 1; fi
    ensure_gh_default
    names="$(run_gh label list --repo "$repo" --limit 500 --json name --jq '.[].name')" || {
      echo "setup-labels: could not read the labels from GitHub" >&2; exit 1; }
    mark_desc="Made by the yrIssues skill (yrProject)"
    if grep -qx "$OLD_MARK" <<< "$names" && ! grep -qx "$MARK" <<< "$names"; then
      run_gh label edit "$OLD_MARK" --repo "$repo" --name "$MARK" --color "FBCA04" --description "$mark_desc" &&
        echo "renamed the label $OLD_MARK to $MARK (its issues keep it)"
    else
      run_gh label create "$MARK" --repo "$repo" --color "FBCA04" --description "$mark_desc" --force
    fi
    if [ -n "$LABEL" ] && [ "$LABEL" != "$MARK" ]; then
      run_gh label create "$LABEL" --repo "$repo" --color "FBCA04" --description "Counted at the start of each Claude Code session" --force
    fi
    for c in "${CATEGORIES[@]}"; do
      IFS='|' read -r name color desc <<< "$c"
      run_gh label create "$name" --repo "$repo" --color "$color" --description "$desc" --force
    done
    run_gh label create "priority: high"   --repo "$repo" --color "B60205" --description "Do soon" --force
    run_gh label create "priority: medium" --repo "$repo" --color "FBCA04" --description "Normal priority" --force
    run_gh label create "priority: low"    --repo "$repo" --color "C2E0C6" --description "When there's time" --force
    ;;

  *)
    echo "usage: bash yrIssues.sh {session-start|list|sync|hook-sync|setup-labels|--help}" >&2
    exit 2
    ;;
esac
