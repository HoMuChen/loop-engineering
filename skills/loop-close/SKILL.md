---
name: loop-close
description: Use to finalize a loop engineering issue after its PR has merged by adding a final summary, cleaning labels, and closing the issue.
---

# Loop Close

Finalize completed loop work.

## Workflow

1. Confirm the linked PR is merged.
2. Confirm verification evidence exists in the run comment or PR body.
3. Add a final summary comment using `templates/comments/final-summary.md`.
4. Remove transient labels: `loop:claimed`, `loop:in-progress`, `loop:repairing`, `loop:pr-open`, and `run:stale`.
5. Add `loop:done`.
6. Close the issue when repository policy allows.
