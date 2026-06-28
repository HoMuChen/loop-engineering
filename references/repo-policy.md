# Repository Policy

Repositories may create `.loop-engineering.yml`.

```yaml
loop_engineering:
  default_agent: codex
  branch_prefix: loop/
  merge_method: squash
  stale_after_minutes: 120
  required_verification:
    - pnpm typecheck
    - pnpm test
  protected_labels:
    - needs-human
    - security
  auto_merge: true
  auto_close: true
  local_repair_limit: 3
  pr_repair_limit: 2
  max_concurrent_runs: 1
  worktree_root: .loop/worktrees
```

`auto_merge` defaults to false. Repositories must opt in to automatic merging.

`max_concurrent_runs` defaults to 1 (effectively serial). Raise it to allow that many `loop-engineer-issue` runs to work in parallel, each in its own git worktree. It is a soft cap counted from the active loop labels, so it can briefly overshoot when runs start simultaneously; per-issue claiming stays exclusive.

`worktree_root` is where parallel runs create their isolated worktrees (default `.loop/worktrees`, which should be gitignored). `loop-recover` cleans orphaned worktrees here.
