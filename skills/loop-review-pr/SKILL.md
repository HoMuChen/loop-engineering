---
name: loop-review-pr
description: Use to review a PR connected to a loop engineering issue, prioritizing bugs, regressions, missing tests, and issue mismatch, and to merge approved PRs when policy allows.
---

# Loop Review PR

> Paths below use `${CLAUDE_PLUGIN_ROOT}` — this plugin's install directory. Claude Code substitutes it automatically; tools that do not (e.g. Codex) should resolve it as the plugin root, not the target repo.

Review PRs with a bug-first stance. The reviewer, not the author run, owns the merge: when the review passes and policy allows, merge here instead of leaving the PR waiting. Without this, an approved green PR has no owner — the author run has already ended, and the issue would sit at `loop:pr-open` until the `loop-recover` stale window.

## Required Setup

- Run `gh auth status`.
- Read `.loop-engineering.yml` through `${CLAUDE_PLUGIN_ROOT}/scripts/loop_repo_policy.py`. Note `auto_merge`, `merge_method`, and `notify_mentions`.

## Workflow

1. Read PR state with `${CLAUDE_PLUGIN_ROOT}/scripts/loop_gh_pr_state.py get --pr <number>`.
2. Confirm the PR links to a GitHub Issue with loop labels or a loop run comment.
3. Inspect the diff.
4. Check for behavior regressions, missing tests, unsafe changes, and mismatch with the issue.
5. Post a review summary using `${CLAUDE_PLUGIN_ROOT}/templates/comments/review-summary.md`.
6. Route by outcome:
   - **Changes required**: mark the issue `loop:repairing`.
   - **Human judgment required**: mark the issue `loop:blocked` and `loop:needs-human`, then notify per `notify_mentions` (see Notification below).
   - **Review passes**: proceed to Merge.

## Merge

Merge only when all of these hold:

- The review passed with no required changes.
- Policy `auto_merge` is true.
- CI state from `loop_gh_pr_state.py get` is `passed` — not `pending`. Never merge on pending checks.
- The linked issue carries no protected label.

Then:

1. Re-read PR state immediately before merging. If the PR is already merged (for example by the author run or another reviewer), skip the merge and treat the outcome as success — this race is expected and harmless.
2. If the PR is behind its base branch (merge state `BEHIND`), run `gh pr update-branch <number>` and stop here. Do not merge on checks that ran against a stale base; the refreshed CI is picked up by the next review pass.
3. Merge with `${CLAUDE_PLUGIN_ROOT}/scripts/loop_gh_pr_state.py merge --pr <number> --method <merge_method>`.
4. If the merge command fails because the PR was merged concurrently, treat it as success. If it fails because branch protection requires approvals the agent cannot give (a PR author account cannot approve its own PR), mark the issue `loop:blocked` plus `loop:needs-human`, state that a human approval is required, and notify per `notify_mentions`.
5. After a successful merge, leave the issue labels as they are — `loop-close` owns final summary, label cleanup, and closing.

## Notification

When this skill marks an issue `loop:blocked` + `loop:needs-human` and policy `notify_mentions` is non-empty, @mention every listed username in the blocking comment and assign the first one with `gh issue edit <number> --add-assignee <username>`, so GitHub's native notifications reach a human.
