# Product Planning Gates

Use three explicit planning stages before implementation:

| Stage | Loop Engineering owner | Artifact | Human gate |
| --- | --- | --- | --- |
| Brainstorm | `loop-spec-feature` | Validated design direction | Approve the proposed direction |
| Spec | `loop-spec-feature` | `.product/feature-specs/{feature-id}.yaml` | Approve the written spec |
| Plan | `loop-split-feature` | `.product/work-items/{work-item-id}.yaml` | Approve work items for build |

This adapts the [Superpowers](https://github.com/obra/superpowers) brainstorming and writing-plans workflow to Product OS. Preserve Loop Engineering's execution boundary: a plan task is one independently reviewable, testable loop run, not a 2–5 minute coding step.

## Brainstorm Gate

1. Inspect the product brief, roadmap, repository, related product artifacts, and current implementation before proposing a design.
2. Check scope first. If the request contains independent subsystems, propose a decomposition and brainstorm only the first coherent feature.
3. In an interactive run, ask one question per message. Prefer constrained choices when they make the decision easier. Focus on purpose, users, success, scope, constraints, and risk.
4. For each material design choice, present two or three viable approaches with tradeoffs and a recommendation. If only one approach is viable, explain the constraint instead of inventing alternatives.
5. Present the proposed direction in sections sized to the feature's complexity. Confirm material choices before treating the design as settled.
6. In an unattended run, never invent user decisions. Record unresolved decisions as explicit open questions and keep the feature in a draft state.

## Spec Gate

Write a spec only after the feature is coherent enough to review. Do not leave `TODO`, `TBD`, or equivalent placeholders; use explicit open questions for unresolved decisions.

Before requesting review, check:

- Scope: one coherent feature, with non-goals that prevent expansion.
- Consistency: problem, approach, scope, acceptance criteria, and validation agree.
- Ambiguity: requirements have one testable interpretation.
- Completeness: users, dependencies, failure behavior, risk, and approval needs are explicit.
- Testability: every acceptance criterion can be verified.

Use planning statuses as gates:

- `needs-discovery`: material product decisions are still unknown.
- `needs-spec`: enough context exists to begin a spec.
- `spec-draft`: a written artifact still has material open questions or requested revisions.
- `spec-review`: the artifact passed self-review and awaits human review.
- `spec-approved`: the human explicitly approved the written spec.
- `ready-for-build`: the implementation plan, not only the spec, is approved.

Keep the matching roadmap item and feature spec aligned through `spec-approved`. After plan approval, move the roadmap item to `ready-for-build` while leaving the approved spec immutable at `spec-approved`. Do not infer approval from silence, prior roadmap placement, or a request to draft.

## Plan Gate

Map likely file responsibilities before splitting tasks. Then create ordered work items that each:

- Produce one independently testable and reviewable result in a single loop run.
- Trace to one or more spec acceptance criteria.
- Name dependencies and interfaces with neighboring work items.
- Identify exact likely create, modify, and test paths when repository evidence permits.
- Carry concrete definition-of-done statements and exact validation commands with expected results.
- Include risk and constraints needed by an isolated implementing agent.

Fold setup, documentation, configuration, and migrations into the task whose deliverable requires them. Split tasks where a reviewer could reasonably approve one and reject another. Do not create vague scaffolding tasks or microsteps that have no standalone test cycle.

Before requesting plan approval, check:

- Coverage: every spec acceptance criterion maps to at least one work item.
- Boundaries: no work item implements unrelated behavior or crosses independent subsystems.
- Ordering: dependencies are acyclic and each consumed interface is produced earlier or already exists.
- Executability: paths, commands, expected results, and completion conditions are concrete.
- Placeholders: no `TODO`, `TBD`, "handle edge cases", or "add tests" shorthand remains.

New work items stay `needs-review`. Only explicit approval of the plan moves them and the feature to `ready-for-build`. Only approved work items may become `loop:ready` GitHub Issues.
