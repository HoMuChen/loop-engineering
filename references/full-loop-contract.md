# Full Loop Contract

The implementing agent may claim, implement, verify, open PRs, repair failures, and clean up when repository policy allows it. It never merges its own PR: merging belongs to the reviewing run (`loop-review-pr`) after an independent review passes, and closing belongs to `loop-close` after the merge. Author and approver are always different runs.

Every run ends in a terminal outcome that says who owes the next move: the agent (an
active state label), the human (`loop:blocked` + `loop:needs-human`, notified), or
nobody (merged/closed). A run that stops without one of these leaves the issue looking
agent-actionable when it is not, so the loop re-picks it, redoes the work, and — since
model output is not deterministic — may reach a different conclusion each time. **An
unbounded re-review is not diligence; it is a stuck loop that never produces a commit.**
Reviews are therefore keyed to the reviewed commit and never re-run against an
unchanged diff, and `pr_repair_limit` binds the reviewing run as well as the
implementing one.

Gates are labels. Prose in an issue body is not a gate — an agent that meets one
escalates once so a human can convert it, rather than refusing forever against a
sentence no approval can remove. See `references/labels.md`.

The agent must stop for human input when:

- Issue information is insufficient.
- The working tree cannot be safely isolated.
- A protected label is present without `loop:human-approved`.
- An issue body demands human review but carries no matching label (escalate once, so
  the gate can be converted into a label and then satisfied).
- The task needs secrets, production data, or manual external access.
- Local verification fails beyond the configured limit.
- CI or review repair fails beyond the configured limit.
- The required change is materially larger than the issue.
- The change may cause data loss, security risk, destructive migration, or irreversible effects.
- Branch protection requires human review.
- The agent lacks permission.
