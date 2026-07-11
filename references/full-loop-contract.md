# Full Loop Contract

The implementing agent may claim, implement, verify, open PRs, repair failures, and clean up when repository policy allows it. It never merges its own PR: merging belongs to the reviewing run (`loop-review-pr`) after an independent review passes, and closing belongs to `loop-close` after the merge. Author and approver are always different runs.

The agent must stop for human input when:

- Issue information is insufficient.
- The working tree cannot be safely isolated.
- A protected label is present.
- The task needs secrets, production data, or manual external access.
- Local verification fails beyond the configured limit.
- CI or review repair fails beyond the configured limit.
- The required change is materially larger than the issue.
- The change may cause data loss, security risk, destructive migration, or irreversible effects.
- Branch protection requires human review.
- The agent lacks permission.
