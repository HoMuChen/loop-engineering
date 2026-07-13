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

`local_repair_limit` and `pr_repair_limit` cap how many times a failure may be retried before the loop stops and asks a human — local verification failures for the first, CI or review failures for the second.

**`pr_repair_limit` binds both sides of the review.** `loop-engineer-issue` counts a repair each time it responds to a bounced review; `loop-review-pr` counts one each time it *issues* a `changes-required` verdict, and must escalate instead of bouncing the PR again once the budget is spent. The count lives in the `Repairs` line of the run comment, so both runs read and write the same number and it survives a hand-off. Without the reviewer honoring it, the review side is unbounded: a PR can be reviewed indefinitely, and because review verdicts are not deterministic, one of those passes will eventually reverse an earlier approval on an unchanged diff. Bouncing a PR a third time is not persistence — it is the loop failing to notice it is stuck.

`max_concurrent_runs` defaults to 1 (effectively serial). Raise it to allow that many `loop-engineer-issue` runs to work in parallel, each in its own git worktree. It is a soft cap counted from the active loop labels, so it can briefly overshoot when runs start simultaneously; per-issue claiming stays exclusive.

`worktree_root` is where parallel runs create their isolated worktrees (default `.loop/worktrees`, which should be gitignored). `loop-recover` cleans orphaned worktrees here.

`intake_issue_limit` caps how many issues `loop-intake-quality` files per scan (default 10), so a scan cannot flood the backlog. Findings beyond the cap are reported, not silently dropped.

`notify_mentions` lists GitHub usernames to notify when a skill needs human input (default empty, meaning no notification). Skills that add `loop:needs-human` @mention these users in the blocking comment and assign the first one to the issue, so GitHub's native email and mobile notifications reach a human without extra infrastructure. Without this key, blocked issues wait silently until someone happens to look.
