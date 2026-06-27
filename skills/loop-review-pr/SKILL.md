---
name: loop-review-pr
description: Use to review a PR connected to a loop engineering issue, prioritizing bugs, regressions, missing tests, and issue mismatch.
---

# Loop Review PR

Review PRs with a bug-first stance.

## Workflow

1. Read PR state with `scripts/loop_gh_pr_state.py get --pr <number>`.
2. Confirm the PR links to a GitHub Issue with loop labels or a loop run comment.
3. Inspect the diff.
4. Check for behavior regressions, missing tests, unsafe changes, and mismatch with the issue.
5. Post a review summary using `templates/comments/review-summary.md`.
6. If changes are required, mark the issue `loop:repairing`.
7. If human judgment is required, mark the issue `loop:blocked` and `loop:needs-human`.
