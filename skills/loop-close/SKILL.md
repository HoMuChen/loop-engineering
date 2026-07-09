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
7. If the issue belongs to a feature milestone, check its progress after closing: `python ../../scripts/loop_gh_milestone.py get --title {feature-id}`. If the milestone is complete (all issues closed), report that the feature is a candidate to move to `released` and to produce release notes. Do not change roadmap status automatically; recommend it for a human (see `../../references/product-os.md`).
