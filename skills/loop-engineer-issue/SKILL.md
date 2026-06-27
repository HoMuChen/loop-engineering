---
name: loop-engineer-issue
description: Use when asked to take a GitHub Issue through the full engineering loop: claim, plan, implement, verify, open PR, repair CI or review failures, merge, close, and clean up.
---

# Loop Engineer Issue

Use GitHub Issues as the source of truth. Use `gh` through the helper scripts in `../../scripts/`.

## Required Setup

- Run `gh auth status`.
- Confirm the current directory is a git repository with a GitHub remote.
- Read repository instructions such as `AGENTS.md`, `CLAUDE.md`, or equivalent.
- Read `.loop-engineering.yml` through `scripts/loop_repo_policy.py`.

## Workflow

1. Read the issue with `scripts/loop_gh_issue_state.py get --issue <number>`.
2. Refuse already-claimed issues unless the user explicitly requests resume or recovery.
3. Stop and mark blocked if requirements are unclear or protected labels are present.
4. Create a branch using the configured branch prefix.
5. Add `loop:claimed`, `loop:in-progress`, and `agent:<name>`.
6. Create or update the structured run comment.
7. Plan the work in the run comment.
8. Implement the smallest scoped change that satisfies the issue.
9. Run configured verification.
10. Open a PR with a body based on `templates/pull-request.md`.
11. Inspect CI and reviews.
12. Repair failures within policy limits.
13. Merge only when repository policy and branch protection allow it.
14. Add a final summary, clean transient labels, add `loop:done`, and close the issue.

## Stop Conditions

Stop with `loop:blocked` and `loop:needs-human` for any condition listed in `../../references/full-loop-contract.md`.
