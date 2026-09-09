---
name: deploy-book
description: Publish the book to GitHub Pages (https://y-rosenthal.github.io/yrThinkPython/) by pushing v3 or re-running the deploy-book workflow, then watch the run and verify the live site. Use when asked to deploy, publish, redeploy, or check whether the site/workflow succeeded.
user-invocable: true
argument-hint: [status | rerun | push]
---

# Deploy the book

The site is built by `.github/workflows/deploy-book.yml` on every push to `v3` and pushed to
the `gh-pages` branch. Nothing is built or pushed from this machine.

**Always pass `-R y-rosenthal/yrThinkPython` to `gh`.** The repo has an `upstream` remote
(AllenDowney/ThinkPython), and without `-R` gh resolves to that repo and reports
"workflow not found". (Alternatively run `gh repo set-default y-rosenthal/yrThinkPython` once.)

Current state:
!`git -C "${CLAUDE_PROJECT_DIR}" status --short --branch | head -15`

## Before pushing

1. Run the `check-notebooks` static check; it must print `OK`.
2. If the change touched notebook text/structure, build locally first (`build-book` skill) so a
   Sphinx error is caught here rather than in CI.
3. Only push when the user asked to deploy/publish/push. Commit on `v3` with a message that
   says what changed in the book (e.g. "chap05: fix exercise 3 wording").

## Publish

```bash
git push origin v3
gh run list  -R y-rosenthal/yrThinkPython --workflow deploy-book.yml --limit 3
gh run watch -R y-rosenthal/yrThinkPython --exit-status $(gh run list -R y-rosenthal/yrThinkPython --workflow deploy-book.yml --limit 1 --json databaseId -q '.[0].databaseId')
```

A successful run takes under a minute. To redeploy without a new commit (`rerun`):

```bash
gh workflow run deploy-book.yml -R y-rosenthal/yrThinkPython --ref v3
```

On failure: `gh run view -R y-rosenthal/yrThinkPython <id> --log-failed`. The usual causes are
a notebook that is not valid JSON, a TOC entry with no file, or a new notebook name that the
workflow's `cp chapters/chap[01][0-9].ipynb jb/` glob does not match.

## Verify the live site

GitHub Pages serves `gh-pages` a minute or two after the run finishes.

```bash
curl -s -o /dev/null -w "%{http_code}\n" https://y-rosenthal.github.io/yrThinkPython/
curl -s https://y-rosenthal.github.io/yrThinkPython/chap03.html | grep -c "phrase you just changed"
```

Report the run URL, its status, and whether the changed text is visible on the live page.
