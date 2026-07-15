---
name: loop-roadmap-update
description: Use to apply explicit user-approved changes to .product/roadmap.yaml, such as moving features between Now/Next/Later/Icebox, changing feature status, adding roadmap items, or recording roadmap decisions.
---

# Loop Roadmap Update

> Paths below use `${CLAUDE_PLUGIN_ROOT}` — this plugin's install directory. Claude Code substitutes it automatically; tools that do not (e.g. Codex) should resolve it as the plugin root, not the target repo.

Update Product OS roadmap state when the user gives explicit product direction. Treat `.product/roadmap.yaml` as product state, not as an execution queue. GitHub Issues remain the source of truth for build execution.

## Required Setup

- Confirm `.product/` exists. If missing, use `loop-product-init` first.
- Read repository instructions such as `AGENTS.md`, `CLAUDE.md`, or equivalent when present.
- Read `${CLAUDE_PLUGIN_ROOT}/references/product-os.md`.
- Read `${CLAUDE_PLUGIN_ROOT}/references/product-planning.md` when changing a planning status from `needs-discovery` through `ready-for-build`.
- Run `python ${CLAUDE_PLUGIN_ROOT}/scripts/loop_product_os.py validate --root .`.
- Read `.product/product-brief.md` and `.product/roadmap.yaml`.
- Read relevant `.product/feature-specs/*.yaml`, `.product/work-items/*.yaml`, decisions, feedback, GitHub Issues, and PRs when the update depends on current facts.

## Trigger Rules

Apply roadmap changes when the user gives explicit direction, for example:

- "Move `line-inbox-v1` to Now."
- "Add `human-handoff` to Next as `needs-spec`."
- "I reviewed and approve the written spec for `line-inbox-v1`; mark it `spec-approved`."
- "I reviewed and approve the work-item plan for `line-inbox-v1`; mark it `ready-for-build`."
- "Mark `role-permission-v1` released."
- "Move analytics dashboard to Later."

Produce recommendations only, without editing files, when the request is exploratory, for example:

- "How should we update the roadmap?"
- "What should move to Now?"
- "Review roadmap priorities."

For exploratory requests, use `loop-product-review` behavior and clearly label output as recommendations.

## Approval Rules

Explicit user approval is required before applying changes that:

- Move a feature into `roadmap.now`.
- Raise priority.
- Expand MVP scope.
- Mark a feature `spec-approved` or `ready-for-build`.
- Start or unblock high-risk work.
- Affect auth, permission, billing, data retention, production data, infrastructure, or compliance direction.

If the user's latest message already explicitly requests one of those changes, treat that as approval for the named change. If the request is ambiguous, ask for confirmation instead of editing.

Artifact gates still apply to explicit requests:

- Before `spec-approved`, require a matching written feature spec that passed self-review and confirmation that the user reviewed that artifact. Update the spec status with the roadmap status; use `loop-spec-feature` behavior when revisions are needed.
- Before `ready-for-build`, require a matching `spec-approved` feature spec plus a complete work-item plan. Require confirmation that the user reviewed the written work items, then update the approved work items to `ready-for-build` with the roadmap item; use `loop-split-feature` behavior when a plan is missing or incomplete.
- Do not use a direct roadmap edit to bypass brainstorming, spec review, or plan review.

## Workflow

1. Parse the requested roadmap changes.
2. Validate that target sections are one of `now`, `next`, `later`, or `icebox`.
3. Validate that feature statuses are defined in `${CLAUDE_PLUGIN_ROOT}/references/product-os.md`.
4. For `spec-approved` or `ready-for-build`, validate the required artifact and approval gate above. If the artifact is missing, report the correct next skill instead of applying the status.
5. Preserve existing roadmap item fields such as `id`, `title`, `priority`, `status`, `progress`, `prs`, and `next_recommended_work_item`.
6. Apply only the requested changes to `.product/roadmap.yaml` and any explicitly gate-coupled spec or work-item status updates.
7. When adding a new roadmap item, include at least:

```yaml
id: feature-id
title: Human readable title
priority: P1
status: needs-spec
```

8. Add or update `.product/decisions/{yyyy-mm-dd}-roadmap-update.md` when the change affects priority, scope, Now/Next/Later placement, or release status.
9. Run `python ${CLAUDE_PLUGIN_ROOT}/scripts/loop_product_os.py validate --root .`.
10. Commit the `.product` changes per Committing .product Changes in `${CLAUDE_PLUGIN_ROOT}/references/product-os.md`.
11. Summarize exact changes, artifact gates checked, any decision file written, validation warnings, and follow-up work such as spec drafting or work item planning.

## Boundaries

Do not implement code, create branches, open pull requests, or create GitHub Issues.

Do not edit feature specs or work items unless the user explicitly asks for those files to be updated too, except the matching status updates required by an explicitly approved spec or plan gate.

Do not silently delete roadmap items. Move unwanted items to `icebox` or `deprecated` only when explicitly requested.

Do not infer product strategy beyond the user's instruction. If the request needs product judgment, recommend options and wait for a clear choice.
