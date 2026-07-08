# Product OS

Product OS adds a product-management layer above the GitHub Issue engineering loop.

`.product/` is the product source of truth. GitHub Issues remain the execution source of truth for implementation. Do not let agents implement directly from roadmap entries or feature specs; turn approved work into scoped GitHub Issues before using `loop-engineer-issue`.

## Directory

```text
.product/
  product-os.yaml
  product-brief.md
  roadmap.yaml
  feature-specs/
  work-items/
  decisions/
  feedback/
  metrics.md
  release-notes/
```

## Initialization

Initialize Product OS in two phases:

1. Run the deterministic init helper to create the safe `.product/` skeleton without overwriting existing files.
2. Inspect the codebase and existing project materials, then discuss a proposed product brief and roadmap with the user before writing product strategy.

The init helper should not infer strategy by itself. The agent using `loop-product-init` should cite repo evidence, separate assumptions, ask clarifying questions, and write non-placeholder product content only after explicit approval.

## Authority Boundary

Human owners decide why, what, priority, scope, tradeoffs, and approval for high-risk work.

Agents may draft specs, split approved specs into work items, update implementation status from facts, produce release notes, summarize feedback, and suggest roadmap changes.

Agents must not independently move features into Now, raise priority, expand MVP scope, approve high-risk features, change billing or permission direction, or deploy to production.

## Roadmap Sections

- `now`: Current product focus. Only approved or ready features in this section may move toward build.
- `next`: Likely upcoming work. Agents may draft specs, but must not implement directly.
- `later`: Lower-priority ideas. Agents may organize only.
- `icebox`: Deferred ideas. Agents may organize only.

## Feature Statuses

- `idea`: Organize only.
- `needs-discovery`: Research and collect questions.
- `needs-spec`: Draft a feature spec.
- `spec-draft`: Improve the draft and list open questions.
- `spec-review`: Wait for human review.
- `spec-approved`: Split into work items.
- `ready-for-build`: May create execution issues for ready work items.
- `in-progress`: Track active issue or PR progress.
- `blocked`: Explain blocker; do not force implementation.
- `in-review`: Wait for review.
- `released`: Produce release notes.
- `measuring`: Summarize feedback and metrics.
- `done`: Do not proactively change except bug or approved follow-up.
- `deprecated`: Do not continue development.

## Work Item Statuses

- `draft`: Proposed task.
- `needs-review`: Waiting for human approval.
- `ready-for-build`: May become a `loop:ready` GitHub Issue.
- `in-progress`: Linked issue or PR is active.
- `blocked`: Requires human input or external state.
- `in-review`: PR is open or review is pending.
- `done`: Completed and released or merged.

## Build Rule

Only one work item should be built per agent run. A builder should receive product brief context, the feature spec, one work item, non-goals, risk, definition of done, and verification commands.
