---
name: loop-engineer-issue
description: "Use when asked to take a GitHub Issue through the full engineering loop: claim, plan, implement, verify, open PR, repair CI or review failures, merge, close, and clean up."
---

# Loop Engineer Issue

Use GitHub Issues as the source of truth. Use `gh` through the helper scripts in `../../scripts/`.

## Required Setup

- Run `gh auth status`.
- Confirm the current directory is a git repository with a GitHub remote.
- Read repository instructions such as `AGENTS.md`, `CLAUDE.md`, or equivalent.
- Read `.loop-engineering.yml` through `scripts/loop_repo_policy.py`. Note `max_concurrent_runs` and `worktree_root`.

## Concurrency

Multiple runs may execute in parallel, each isolated in its own git worktree. GitHub Issue labels are the only shared state — there is no in-memory coordination. The active-run count is the number of open issues currently carrying `loop:claimed`, `loop:in-progress`, or `loop:repairing`.

`max_concurrent_runs` is a soft cap, enforced optimistically. It can briefly overshoot when several runs start in the same instant; per-issue double-claiming is still prevented because each run refuses an already-claimed issue.

## Workflow

1. Read the issue with `scripts/loop_gh_issue_state.py get --issue <number>`.
2. Refuse already-claimed issues unless the user explicitly requests resume or recovery.
3. Stop and mark blocked if requirements are unclear or protected labels are present. A `loop:ready` issue with a protected label is inconsistent; do not treat the ready label as an override.
4. Count active runs (`gh issue list` for the active labels above). If the count is already at or above `max_concurrent_runs`, stop without claiming — another run holds the slot.
5. Claim optimistically: add `loop:claimed`, `loop:in-progress`, and `agent:<name>` to this issue.
6. Re-count active runs. If the count now exceeds `max_concurrent_runs` and another run claimed earlier (lower issue number, or earlier `Started` timestamp), yield: remove the labels just added and stop. Otherwise proceed.
7. Create a branch using the configured branch prefix, then add it as a worktree under `worktree_root`, for example `git worktree add <worktree_root>/<issue> -b <branch>`. Do all implementation and verification inside this worktree. Install dependencies there if verification needs them.
8. Create or update the structured run comment, including the `Worktree` path.
9. Plan the work in the run comment.
10. Implement the smallest scoped change that satisfies the issue.
11. Run configured verification.
12. Open a PR with a body based on `templates/pull-request.md`.
13. Inspect CI and reviews.
14. Repair failures within policy limits.
15. Merge only when repository policy and branch protection allow it.
16. Add a final summary, clean transient labels, add `loop:done`, and close the issue.
17. Remove the worktree (`git worktree remove <worktree_root>/<issue>`). Always clean up the worktree on stop or block as well, so it does not linger as an orphan.

## Stop Conditions

Stop with `loop:blocked` and `loop:needs-human` for any condition listed in `../../references/full-loop-contract.md`.
