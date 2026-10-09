---
name: yrpublish
description: Publish this repo's book to GitHub Pages (https://y-rosenthal.github.io/yrThinkPython/) end to end - run the checks, merge the current topic branch into v3, push, watch the deploy-book workflow, and verify the live site (chapter outputs, review pages). Use when asked to publish, release, go live, deploy the changes, or "yrpublish".
user-invocable: true
argument-hint: [branch to publish (default: current branch)] [--skip-build]
---

# Publish the site (yrpublish)

The site is built by `.github/workflows/deploy-book.yml` on every push to `v3` and served from
`gh-pages`. Publishing = getting the work onto `v3` safely, then confirming the deploy worked.
Invoking this skill is the user's go-ahead to merge into `v3` and push; confirm first only if
something unexpected shows up (uncommitted changes you did not make, failing checks, v3 has
diverged, a merge conflict).

**Always pass `-R y-rosenthal/yrThinkPython` to `gh`** (the `upstream` remote would otherwise be
picked and gh reports "workflow not found").

Current state:
!`git -C "${CLAUDE_PROJECT_DIR}" status --short --branch | head -15`

## 1. Pre-flight (on the branch being published)

1. Working tree clean (`git status --short` empty). If there are uncommitted changes, ask
   whether to commit them; never commit files you did not create or review.
2. Static checks: `python3 .claude/skills/check-notebooks/check_notebooks.py` must print `OK`.
3. Review pages: `yr/tools/review.sh selftest` must print `SELFTEST OK` (the tools work), and
   `yr/tools/review.sh check yr/*.ipynb` must print `OK` for each page.
4. Unless `--skip-build`: `.claude/skills/build-book/build_book.sh` must end with
   "no new warnings" and no `WARNING: ... not executed` lines (same steps as the workflow,
   including running the chapters).
5. Push the branch so it is backed up: `git push -u origin <branch>`.

## 2. Merge into v3 and push

```bash
BR=$(git branch --show-current)          # or the branch named in the arguments
git fetch origin
git switch v3
git merge --ff-only origin/v3            # bring local v3 up to date; stop if this fails
git merge --no-ff "$BR" -m "Merge $BR: <one line on what changes on the site>"
git push origin v3
git switch "$BR"
```

If `git merge` conflicts, stop and report (for notebooks, see the sync-upstream skill's advice);
do not force anything. Never `push --force` to `v3`.

## 3. Watch the deploy

```bash
sleep 5   # let GitHub register the push
ID=$(gh run list -R y-rosenthal/yrThinkPython --workflow deploy-book.yml --branch v3 --limit 1 --json databaseId -q '.[0].databaseId')
gh run watch -R y-rosenthal/yrThinkPython --exit-status "$ID"
gh run view  -R y-rosenthal/yrThinkPython "$ID" --log | grep -E "::warning::|WARNING:|not executed" || true
```

(If the foreground `sleep` is blocked, just list the runs and pick the one whose head SHA is the
merge commit: `gh run list ... --json databaseId,headSha`.)

A run takes about 2-3 minutes (installing packages, executing the chapters, building). Report
any warnings from `execute_notebooks.py` (a chapter that could not run is published without
outputs). On failure: `gh run view -R y-rosenthal/yrThinkPython "$ID" --log-failed`; common
causes are in the deploy-book skill. To redeploy without a new commit:
`gh workflow run deploy-book.yml -R y-rosenthal/yrThinkPython --ref v3`.

## 4. Verify the live site

GitHub Pages updates a minute or two after the run finishes. Then:

```bash
python3 ${CLAUDE_SKILL_DIR}/verify_live.py
```

It fetches the home page, every chapter page and every yr/ review page in the TOC, and checks
that each loads, that chapter pages show code outputs (and section 5.9's stack diagram), and
that review pages have their concept lists, answers and pictures. It retries for a few minutes
while Pages catches up. To confirm a specific change, also grep for it:
`curl -s https://y-rosenthal.github.io/yrThinkPython/<page>.html | grep -c "<changed text>"`.

## 5. Report

The merge commit, the run URL and result, any execution warnings, the verify_live.py result,
and the links to the changed pages. Leave the topic branch in place (the user can delete it).
