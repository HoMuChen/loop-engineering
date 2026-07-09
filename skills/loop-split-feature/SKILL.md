---
name: loop-split-feature
description: Use to split a Product OS feature spec with spec-approved or ready-for-build status into small work item YAML files and, when explicitly allowed, prepared GitHub Issues.
---

# Loop Split Feature

Split an approved feature spec into small, reviewable work items. Product OS work items describe execution units; GitHub Issues remain the source of truth for actual engineering runs.

## Required Setup

- Confirm `.product/` exists. If missing, use `loop-product-init` first.
- Run `gh auth status` only if creating or syncing GitHub Issues.
- Read repository instructions such as `AGENTS.md`, `CLAUDE.md`, or equivalent when present.
- Read `../../references/product-os.md`.
- Run `python ../../scripts/loop_product_os.py validate --root .`.
- Read `.product/product-brief.md`, `.product/roadmap.yaml`, and the target feature spec.

## Selection Rules

Select one feature only.

Allowed feature statuses:

- `spec-approved`: create work item drafts or reviewed work items.
- `ready-for-build`: create or sync execution-ready work items.

Do not split `idea`, `needs-spec`, `spec-draft`, `spec-review`, `blocked`, `done`, or `deprecated` features unless the user explicitly asks for analysis only.

## Work Item Format

Create `.product/work-items/{work-item-id}.yaml` with:

```yaml
id: wi-feature-id-001
feature_id: feature-id
title: Short implementation task
type: backend
status: needs-review
risk: medium
definition_of_done:
  - TODO
constraints:
  - TODO
validation:
  - TODO
links:
  issues: []
  prs: []
```

Use `status: needs-review` by default. Use `status: ready-for-build` only when the feature is already `ready-for-build` or the user explicitly approves the work items for build.

## Workflow

1. Read the feature problem, scope, non-goals, acceptance criteria, and risk.
2. Split into small tasks that can each be implemented in one loop run.
3. Keep high-risk work smaller and mark approval requirements clearly.
4. Avoid duplicate work items by comparing existing `.product/work-items/*.yaml`.
5. Create or update work item YAML files.
6. Create GitHub Issues only when explicitly requested or when syncing existing `ready-for-build` work items. Each issue must include the feature id, work item id, definition of done, non-goals, risk, and validation commands.
7. Label generated execution issues with `kind:feature` and `loop:ready` only when the work item is ready, scoped, and verification is clear.
8. Do not add protected labels such as `security`, `data-loss`, `migration`, or `needs-human` to an issue that also has `loop:ready`. `loop-engineer-issue` treats protected labels as a stop condition, so `loop:ready` plus a protected label is an invalid execution state.
9. If a work item has a security-, permission-, credential-, migration-, billing-, or data-loss-sensitive concern but is still approved for loop execution, record the concern in the issue body and use non-blocking labels such as `area:security`, `area:permissions`, or `risk:medium` when the repository uses them. Do not use protected labels for non-blocking risk metadata.
10. If a work item truly requires human handling before implementation, do not mark it `loop:ready`. Use `loop:blocked` plus `loop:needs-human` and add the relevant protected label.
11. Run `python ../../scripts/loop_product_os.py validate --root .`.
12. Report created work items, skipped duplicates, created issues, and any items needing human review.

## Boundaries

Do not implement code, create branches, or open pull requests.

Do not approve a feature spec.

Do not bypass GitHub Issues by sending `.product/work-items` directly to `loop-engineer-issue`.

Do not mark high-risk work `loop:ready` without human approval.

Do not combine `loop:ready` with protected labels. If the task should run after approval, keep protected labels off the execution issue and document the risk in the body or non-blocking labels. If the task should not run automatically, omit `loop:ready` and mark it blocked for human handling.
