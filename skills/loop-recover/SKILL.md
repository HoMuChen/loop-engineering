---
name: loop-recover
description: Use to find stale loop engineering issues or PRs, compare issue labels with branch, PR, CI, and review state, then resume, reassign, or block.
---

# Loop Recover

Recover stale or inconsistent loop runs.

## Workflow

1. List open issues with active labels: `loop:claimed`, `loop:in-progress`, `loop:pr-open`, or `loop:repairing`.
2. Parse the latest structured run comment, including its `Worktree` path.
3. Compare the run comment with branch, PR, CI, and review state.
4. Add `run:stale` when `Updated` is older than policy `stale_after_minutes`.
5. Resume when the next action is clear.
6. Reassign when the original run is abandoned but state is safe.
7. Block when state is ambiguous or human decision is needed.
8. Remove orphaned worktrees under `worktree_root` whose owning run is stale, abandoned, or resolved (`git worktree remove`, then `git worktree prune`). A lingering worktree wrongly counts against `max_concurrent_runs`, so freeing it returns the slot.
