---
name: loop-split-feature
description: Use to split a Product OS feature spec with spec-approved or ready-for-build status into small work item YAML files and, when explicitly allowed, prepared GitHub Issues.
---

# Loop Split Feature

> Paths below use `${CLAUDE_PLUGIN_ROOT}` — this plugin's install directory. Claude Code substitutes it automatically; tools that do not (e.g. Codex) should resolve it as the plugin root, not the target repo.

Split an approved feature spec into small, reviewable work items. Product OS work items describe execution units; GitHub Issues remain the source of truth for actual engineering runs.

## Required Setup

- Confirm `.product/` exists. If missing, use `loop-product-init` first.
- Run `gh auth status` only if creating or syncing GitHub Issues.
- Read repository instructions such as `AGENTS.md`, `CLAUDE.md`, or equivalent when present.
- Read `${CLAUDE_PLUGIN_ROOT}/references/product-os.md`.
- Run `python ${CLAUDE_PLUGIN_ROOT}/scripts/loop_product_os.py validate --root .`.
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
6. When creating GitHub Issues, first ensure the feature's milestone exists so every issue can be grouped under it: `python ${CLAUDE_PLUGIN_ROOT}/scripts/loop_gh_milestone.py ensure --title {feature-id} --description "{feature-title}"`. The milestone title is the feature id (see `${CLAUDE_PLUGIN_ROOT}/references/product-os.md`).
7. Create GitHub Issues only when explicitly requested or when syncing existing `ready-for-build` work items. Attach each issue to the feature milestone with `gh issue create --milestone {feature-id}`. Each issue must include the feature id, work item id, definition of done, non-goals, risk, and validation commands. Immediately after each `gh issue create`, record the link back on the work item with `python ${CLAUDE_PLUGIN_ROOT}/scripts/loop_product_os.py work-item --root . --id {work-item-id} --issue {number}` — without the stored link, execution state cannot be derived from the issue later (see Linking Work Items to Issues in `${CLAUDE_PLUGIN_ROOT}/references/product-os.md`).
8. Label generated execution issues with `kind:feature` and `loop:ready` only when the work item is ready, scoped, and verification is clear.
9. Do not add protected labels such as `security`, `data-loss`, `migration`, or `needs-human` to an issue that also has `loop:ready`. `loop-engineer-issue` treats protected labels as a stop condition, so `loop:ready` plus a protected label is an invalid execution state.
10. If a work item has a security-, permission-, credential-, migration-, billing-, or data-loss-sensitive concern but is still approved for loop execution, record the concern in the issue body and use non-blocking labels such as `area:security`, `area:permissions`, or `risk:medium` when the repository uses them. Do not use protected labels for non-blocking risk metadata.
11. If a work item truly requires human handling before implementation, do not mark it `loop:ready`. Use `loop:blocked` plus `loop:needs-human` and add the relevant protected label. When policy `notify_mentions` is non-empty (read `.loop-engineering.yml` through `${CLAUDE_PLUGIN_ROOT}/scripts/loop_repo_policy.py`), @mention every listed username in the issue and assign the first one with `gh issue edit <number> --add-assignee <username>`, so GitHub's native notifications reach a human.
12. Run `python ${CLAUDE_PLUGIN_ROOT}/scripts/loop_product_os.py validate --root .`.
13. Commit the `.product` changes per Committing .product Changes in `${CLAUDE_PLUGIN_ROOT}/references/product-os.md`.
14. Report created work items, skipped duplicates, created issues, the feature milestone, and any items needing human review.

## Boundaries

Do not implement code, create branches, or open pull requests.

Do not approve a feature spec.

Do not bypass GitHub Issues by sending `.product/work-items` directly to `loop-engineer-issue`.

Do not mark high-risk work `loop:ready` without human approval.

Do not combine `loop:ready` with protected labels. If the task should run after approval, keep protected labels off the execution issue and document the risk in the body or non-blocking labels. If the task should not run automatically, omit `loop:ready` and mark it blocked for human handling.
