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

## Selection

When the user names a specific issue, use it. When the prompt is open ("take the next issue"), select in this priority order so in-flight work finishes before new work starts:

1. **Resume a repair.** An open `loop:repairing` issue whose latest run comment is not being actively updated by another agent (its `Updated` is older than `stale_after_minutes`, or the newest activity is the review that requested changes). `loop-review-pr` sets `loop:repairing` but does not itself repair, so without this step a review fix waits for the `loop-recover` watchdog and stalls for a full stale window. Repairing an existing PR clears work-in-progress and is cheaper than opening new work.
2. **Start a fresh issue.** The lowest-numbered open `loop:ready` issue with no protected label.

Do not exceed `pr_repair_limit` when resuming a repair. If the recorded repair count has already reached the limit, stop and mark `loop:blocked` plus `loop:needs-human` instead of repairing again.

## Run Comment Heartbeat

`loop-recover` judges staleness from the run comment's `Updated` timestamp. A long but healthy run (large change, dependency install, slow test suite) that never updates its comment looks abandoned and can be reassigned mid-flight — two agents on one issue is worse than a slow one. Treat the heartbeat as a contract: update `Updated` (and the relevant `Plan` / `Verification` / `Repairs` section) after each major step — claim, plan, implement, verify, PR open, and each repair attempt. Keep `stale_after_minutes` comfortably above your slowest expected step.

## Workflow

1. Read the issue with `scripts/loop_gh_issue_state.py get --issue <number>`.
2. Refuse issues already claimed by a live run (`loop:claimed` / `loop:in-progress` whose run comment is fresh) unless the user explicitly requests resume or recovery. A `loop:repairing` issue selected per the Selection rules is a resume, not a refusal.
3. Stop and mark blocked if requirements are unclear or protected labels are present. A `loop:ready` issue with a protected label is inconsistent; do not treat the ready label as an override.
4. Count active runs (`gh issue list` for the active labels above). If the count is already at or above `max_concurrent_runs`, stop without claiming — another run holds the slot.
5. Claim optimistically: add `loop:claimed`, `loop:in-progress`, and `agent:<name>` to this issue.
6. Re-read this issue and re-count active runs to resolve races optimistically:
   - **Same-issue race:** re-read this issue's run comments. If another agent already posted a run comment for this issue with an earlier `Started` timestamp (or a lower `Run` id when timestamps tie), yield: remove the labels you just added and stop. Adding a label is not atomic, so this comment check is what actually prevents two agents from building the same issue.
   - **Slot race:** if the active-run count now exceeds `max_concurrent_runs` and another run claimed a different issue earlier (lower issue number, or earlier `Started`), yield the same way.
   - Otherwise proceed.
7. For a fresh issue, create a branch using the configured branch prefix, then add it as a worktree under `worktree_root`, for example `git worktree add <worktree_root>/<issue> -b <branch>`. When resuming a `loop:repairing` issue, reuse the existing branch and worktree recorded in the run comment (recreate the worktree from the branch if it was pruned) instead of starting a new branch. Do all implementation and verification inside this worktree. Install dependencies there if verification needs them.
8. Create or update the structured run comment from `templates/comments/run.md`, including the `Worktree` path and the `Repairs` line. When resuming a `loop:repairing` or stale issue, read the existing run comment first and carry its `Repairs` counts forward — never reset them.
9. Plan the work in the run comment.
10. Implement the smallest scoped change that satisfies the issue.
11. Run verification. If `required_verification` is non-empty, run exactly those commands. If it is empty, infer the repository's standard checks (for example test / typecheck / lint / build from `package.json` scripts, `pyproject.toml`, a `Makefile`, or CI config) and run what you find. If no verification exists and none can be inferred, do not imply the change is verified: state "no verification configured or discoverable" in both the run comment `Verification` section and the PR `Risk` section.
12. Open a PR with a body based on `templates/pull-request.md`.
13. Inspect CI and reviews.
14. Repair failures within policy limits. Read the current counts from the run comment `Repairs` line, increment `local` for each local-verification repair and `pr` for each CI or review repair, and write the updated line back on every attempt. Stop when a count would exceed `local_repair_limit` or `pr_repair_limit`: mark `loop:blocked` plus `loop:needs-human` instead of repairing again. Because the counts live in the run comment, they survive a stale-and-reassign hand-off, so a resumed run cannot silently restart the repair budget.
15. Merge only when repository policy and branch protection allow it.
16. Add a final summary, clean transient labels, add `loop:done`, and close the issue.
17. Remove the worktree (`git worktree remove <worktree_root>/<issue>`). Always clean up the worktree on stop or block as well, so it does not linger as an orphan.

## Stop Conditions

Stop with `loop:blocked` and `loop:needs-human` for any condition listed in `../../references/full-loop-contract.md`.
