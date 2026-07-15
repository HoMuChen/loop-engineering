---
name: loop-spec-feature
description: Use to brainstorm, discuss, draft, review, or revise a Product OS feature spec, including moving a needs-discovery or needs-spec feature through design choices to a human-approved spec without implementing it.
---

# Loop Spec Feature

> Paths below use `${CLAUDE_PLUGIN_ROOT}` — this plugin's install directory. Claude Code substitutes it automatically; tools that do not (e.g. Codex) should resolve it as the plugin root, not the target repo.

Turn a feature idea into a reviewed design and written Product OS spec. Treat brainstorming, the written spec, and human approval as separate gates.

## Required Setup

- Confirm `.product/` exists. If missing, use `loop-product-init` first.
- Read repository instructions such as `AGENTS.md`, `CLAUDE.md`, or equivalent when present.
- Read `${CLAUDE_PLUGIN_ROOT}/references/product-os.md`.
- Read `${CLAUDE_PLUGIN_ROOT}/references/product-planning.md`.
- Run `python ${CLAUDE_PLUGIN_ROOT}/scripts/loop_product_os.py validate --root .`.
- Read `.product/product-brief.md` and `.product/roadmap.yaml`.

## Selection Rules

Select one feature only.

Prefer roadmap items in this order:

1. `roadmap.now` with `status: needs-spec`
2. `roadmap.next` with `status: needs-spec`
3. `roadmap.now` with `status: needs-discovery`
4. `roadmap.next` with `status: needs-discovery`

Do not draft specs for `later` or `icebox` unless the user explicitly names the feature.

## Brainstorming

Follow the Brainstorm Gate in `${CLAUDE_PLUGIN_ROOT}/references/product-planning.md` before writing or materially revising the spec.

- Inspect the relevant implementation, tests, recent commits, feedback, decisions, issues, and prior specs before asking detailed questions.
- Check whether the feature is small enough for one spec. If it contains independent subsystems, propose a decomposition and stop until the user chooses the first feature.
- In interactive work, ask one question per message. Prefer a constrained choice when useful.
- Explore two or three viable approaches for material design choices, lead with a recommendation, and explain tradeoffs. Do not invent alternatives when constraints leave only one viable approach.
- Present the resulting design in reviewable sections and confirm material choices before writing a review-ready spec.
- In unattended work, capture unknown decisions in `open_questions` and keep the artifact at `spec-draft`; never simulate user approval.

## Spec Format

Create `.product/feature-specs/{feature-id}.yaml` with:

```yaml
id: feature-id
title: Feature title
status: spec-review
priority: P1
owner: unassigned
problem: |
  Concrete user or product problem.
users:
  - Primary user
approach:
  summary: Chosen design direction.
  rationale: Why this approach fits the constraints.
alternatives_considered:
  - option: Alternative direction
    tradeoffs: Why it was not selected.
scope:
  - Included behavior
non_goals:
  - Explicitly excluded behavior
dependencies: []
acceptance_criteria:
  - Observable, testable outcome
validation:
  - How the outcome will be verified
risk:
  level: medium
  reasons: []
approval:
  before_implementation: true
  before_merge: true
open_questions: []
```

Use `status: spec-draft` when material open questions remain. Use `status: spec-review` only after the design is coherent and the spec passes the Spec Gate self-review. Do not leave placeholder text from the example in a real spec.

## Workflow

1. Select one feature and gather the context required by the Brainstorm Gate.
2. Resolve material choices through brainstorming. If the run is unattended or the user is unavailable, write explicit open questions rather than guessing.
3. Draft or revise the spec with the chosen approach, alternatives, scope, non-goals, dependencies, acceptance criteria, validation, risk, approval requirements, and remaining open questions.
4. Self-review the written artifact using the Spec Gate in `${CLAUDE_PLUGIN_ROOT}/references/product-planning.md`; fix placeholders, contradictions, ambiguity, scope leaks, and untestable criteria inline.
5. Set the spec and matching roadmap item to `spec-draft` when material questions remain, or `spec-review` when the artifact is ready for human review. Do not change roadmap section or priority.
6. Run `python ${CLAUDE_PLUGIN_ROOT}/scripts/loop_product_os.py validate --root .`.
7. Commit the `.product` changes per Committing .product Changes in `${CLAUDE_PLUGIN_ROOT}/references/product-os.md`.
8. Ask the user to review the written spec. Report the path, settled choices, and open questions.
9. If the user requests changes, revise the artifact, repeat self-review, validation, and commit, and keep it in `spec-draft` or `spec-review` as appropriate.
10. Only after the user explicitly approves the written spec, set both the spec and matching roadmap item to `spec-approved`, validate, and commit the approval state.
11. Use `loop-split-feature` next to create the implementation plan when the user asks to continue; do not begin implementation from the spec.

## Boundaries

Do not implement code.

Do not create GitHub Issues in this skill. Issue preparation belongs to `loop-split-feature` after plan approval.

Do not split work items or write an implementation plan in this skill. Use `loop-split-feature` after spec approval.

Do not mark a spec approved based on silence, an earlier design preference, or a request to draft. Approval must refer to the written spec.

Do not silently overwrite an existing feature spec. If a spec exists, update it only when the user asked for revision; otherwise report that it already exists.

Do not move roadmap sections or raise priority without explicit approval.
