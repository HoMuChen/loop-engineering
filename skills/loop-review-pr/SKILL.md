---
name: loop-review-pr
description: Use to review a PR connected to a loop engineering issue, prioritizing bugs, regressions, missing tests, and issue mismatch.
---

# Loop Review PR

> Paths below use `${CLAUDE_PLUGIN_ROOT}` — this plugin's install directory. Claude Code substitutes it automatically; tools that do not (e.g. Codex) should resolve it as the plugin root, not the target repo.

Review PRs with a bug-first stance.

## Workflow

1. Read PR state with `${CLAUDE_PLUGIN_ROOT}/scripts/loop_gh_pr_state.py get --pr <number>`.
2. Confirm the PR links to a GitHub Issue with loop labels or a loop run comment.
3. Inspect the diff.
4. Check for behavior regressions, missing tests, unsafe changes, and mismatch with the issue.
5. Post a review summary using `${CLAUDE_PLUGIN_ROOT}/templates/comments/review-summary.md`.
6. If changes are required, mark the issue `loop:repairing`.
7. If human judgment is required, mark the issue `loop:blocked` and `loop:needs-human`.
