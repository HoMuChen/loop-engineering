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
  intake_issue_limit: 10
  notify_mentions:
    - HoMuChen
```

`auto_merge` defaults to false. Repositories must opt in to automatic merging. It authorizes only `loop-review-pr` — the reviewing run, never the PR's author run — to merge, and only after its own review passes and CI is green. `loop-engineer-issue` always ends at the `loop:pr-open` hand-off, so every PR gets an independent review before it lands.

`max_concurrent_runs` defaults to 1 (effectively serial). Raise it to allow that many `loop-engineer-issue` runs to work in parallel, each in its own git worktree. It is a soft cap counted from the active loop labels, so it can briefly overshoot when runs start simultaneously; per-issue claiming stays exclusive.

`worktree_root` is where parallel runs create their isolated worktrees (default `.loop/worktrees`, which should be gitignored). `loop-recover` cleans orphaned worktrees here.

`intake_issue_limit` caps how many issues `loop-intake-quality` files per scan (default 10), so a scan cannot flood the backlog. Findings beyond the cap are reported, not silently dropped.

`notify_mentions` lists GitHub usernames to notify when a skill needs human input (default empty, meaning no notification). Skills that add `loop:needs-human` @mention these users in the blocking comment and assign the first one to the issue, so GitHub's native email and mobile notifications reach a human without extra infrastructure. Without this key, blocked issues wait silently until someone happens to look.
