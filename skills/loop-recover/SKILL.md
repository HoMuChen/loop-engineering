---
name: loop-recover
description: Use to find stale loop engineering issues or PRs, compare issue labels with branch, PR, CI, and review state, then resume, reassign, or block.
---

# Loop Recover

> Paths below use `${CLAUDE_PLUGIN_ROOT}` — this plugin's install directory. Claude Code substitutes it automatically; tools that do not (e.g. Codex) should resolve it as the plugin root, not the target repo.

Recover stale or inconsistent loop runs, and return resolved blocked issues to the queue.

## Stale Run Recovery

1. List open issues with active labels: `loop:claimed`, `loop:in-progress`, `loop:pr-open`, or `loop:repairing`.
2. Parse the latest structured run comment, including its `Worktree` path.
3. Compare the run comment with branch, PR, CI, and review state.
4. Add `run:stale` when `Updated` is older than policy `stale_after_minutes`.
5. Resume when the next action is clear.
6. Reassign when the original run is abandoned but state is safe. Preserve the existing run comment, including its `Repairs` counts, so the resuming run continues the repair budget instead of restarting it.
7. Block when state is ambiguous or human decision is needed. When policy `notify_mentions` is non-empty (read `.loop-engineering.yml` through `${CLAUDE_PLUGIN_ROOT}/scripts/loop_repo_policy.py`), fill the blocked comment's cc line by @mentioning every listed username and assign the first one with `gh issue edit <number> --add-assignee <username>`, so GitHub's native notifications reach a human.
8. Remove orphaned worktrees under `worktree_root` whose owning run is stale, abandoned, or resolved (`git worktree remove`, then `git worktree prune`). A lingering worktree wrongly counts against `max_concurrent_runs`, so freeing it returns the slot.

## Blocked Issue Recovery

`loop:blocked` is otherwise a dead end: no other skill revisits it, so a human who answers the blocking question but forgets the label surgery leaves the issue stuck forever. Sweep it here.

9. List open issues with `loop:blocked`.
10. For each, read the latest blocking comment (from `${CLAUDE_PLUGIN_ROOT}/templates/comments/blocked.md` or `triage-question.md`) and identify what human input it requested.
11. Check for a newer comment from a human (not an `agent:*` run comment) posted after the block that supplies the requested input or decision.
12. When the blocker is an information or question gap that a human has now answered, and no protected label remains on the issue, return it to the queue: remove `loop:blocked` and `loop:needs-human`, then add `loop:ready` (use `${CLAUDE_PLUGIN_ROOT}/scripts/loop_labels.py set-status`). Leave a short comment noting it was unblocked from the human reply.
13. Do not auto-unblock when a protected label (for example `security`, `data-loss`, `migration`, `needs-human`) is still present, when the decision requires approval the human has not given, or when the human reply is ambiguous. Report these as still blocked so a human can act.
