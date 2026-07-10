---
name: loop-close
description: Use to finalize a loop engineering issue after its PR has merged by adding a final summary, cleaning labels, and closing the issue.
---

# Loop Close

> Paths below use `${CLAUDE_PLUGIN_ROOT}` — this plugin's install directory. Claude Code substitutes it automatically; tools that do not (e.g. Codex) should resolve it as the plugin root, not the target repo.

Finalize completed loop work.

## Workflow

1. Confirm the linked PR is merged.
2. Confirm verification evidence exists in the run comment or PR body.
3. Add a final summary comment using `${CLAUDE_PLUGIN_ROOT}/templates/comments/final-summary.md`.
4. Remove transient labels: `loop:claimed`, `loop:in-progress`, `loop:repairing`, `loop:pr-open`, and `run:stale`.
5. Add `loop:done`.
6. Close the issue when repository policy allows.
7. Write execution facts back into Product OS so `.product/` does not drift. When `.product/` exists and the issue maps to a work item (the work item's `links.issues` contains this issue, the issue body or run comment references a `wi-...` id, or the feature milestone identifies the feature), mark that work item done and record the links: `python ${CLAUDE_PLUGIN_ROOT}/scripts/loop_product_os.py work-item --root . --id {work-item-id} --status done --issue {issue} --pr {pr}`. Then commit the write-back per Committing .product Changes in `${CLAUDE_PLUGIN_ROOT}/references/product-os.md`. Skip this step for repositories without `.product/` or issues with no work item (for example quality-intake findings).
8. If the issue belongs to a feature milestone, check its progress after closing: `python ${CLAUDE_PLUGIN_ROOT}/scripts/loop_gh_milestone.py get --title {feature-id}`. If the milestone is complete (all issues closed), report that the feature is a candidate to move to `released` and to produce release notes. Do not change roadmap status automatically; recommend it for a human (see `${CLAUDE_PLUGIN_ROOT}/references/product-os.md`).
