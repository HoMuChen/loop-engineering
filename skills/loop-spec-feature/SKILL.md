---
name: loop-spec-feature
description: Use to turn a Product OS roadmap feature with needs-spec or needs-discovery status into a feature spec draft under .product/feature-specs without approving or implementing it.
---

# Loop Spec Feature

Draft a feature spec from Product OS roadmap context. The result should be reviewable by a human and should not be treated as approved by default.

## Required Setup

- Confirm `.product/` exists. If missing, use `loop-product-init` first.
- Read repository instructions such as `AGENTS.md`, `CLAUDE.md`, or equivalent when present.
- Read `../../references/product-os.md`.
- Run `python ../../scripts/loop_product_os.py validate --root .`.
- Read `.product/product-brief.md` and `.product/roadmap.yaml`.

## Selection Rules

Select one feature only.

Prefer roadmap items in this order:

1. `roadmap.now` with `status: needs-spec`
2. `roadmap.next` with `status: needs-spec`
3. `roadmap.now` with `status: needs-discovery`
4. `roadmap.next` with `status: needs-discovery`

Do not draft specs for `later` or `icebox` unless the user explicitly names the feature.

## Spec Format

Create `.product/feature-specs/{feature-id}.yaml` with:

```yaml
id: feature-id
title: Feature title
status: spec-draft
priority: P1
owner: TODO
problem: |
  TODO
users:
  - TODO
scope:
  - TODO
non_goals:
  - TODO
acceptance_criteria:
  - TODO
risk:
  level: medium
  reasons: []
approval:
  before_implementation: true
  before_merge: true
open_questions:
  - TODO
```

## Workflow

1. Select the feature.
2. Gather existing context from product brief, roadmap, feedback, decisions, and related issues when available.
3. Draft the spec with explicit scope, non-goals, acceptance criteria, risk, approval requirements, and open questions.
4. Keep status as `spec-draft` unless the user explicitly approved the spec in the current request.
5. Run `python ../../scripts/loop_product_os.py validate --root .`.
6. Summarize what was drafted and what needs human review.

## Boundaries

Do not implement code.

Do not create GitHub Issues unless explicitly asked.

Do not silently overwrite an existing feature spec. If a spec exists, update it only when the user asked for revision; otherwise report that it already exists.

Do not move roadmap sections or raise priority without explicit approval.
