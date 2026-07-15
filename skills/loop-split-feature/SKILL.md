---
name: loop-split-feature
description: Use to turn a human-approved Product OS feature spec into an implementation plan of ordered, reviewable work item YAML files and, after plan approval, optionally prepared GitHub Issues.
---

# Loop Split Feature

> Paths below use `${CLAUDE_PLUGIN_ROOT}` — this plugin's install directory. Claude Code substitutes it automatically; tools that do not (e.g. Codex) should resolve it as the plugin root, not the target repo.

Turn an approved feature spec into an implementation plan of small, reviewable work items. Product OS work items describe execution units; GitHub Issues remain the source of truth for actual engineering runs.

## Required Setup

- Confirm `.product/` exists. If missing, use `loop-product-init` first.
- Run `gh auth status` only if creating or syncing GitHub Issues.
- Read repository instructions such as `AGENTS.md`, `CLAUDE.md`, or equivalent when present.
- Read `${CLAUDE_PLUGIN_ROOT}/references/product-os.md`.
- Read `${CLAUDE_PLUGIN_ROOT}/references/product-planning.md`.
- Run `python ${CLAUDE_PLUGIN_ROOT}/scripts/loop_product_os.py validate --root .`.
- Read `.product/product-brief.md`, `.product/roadmap.yaml`, and the target feature spec.
- Inspect the implementation, tests, and recent commits that establish current file responsibilities and interfaces.

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
sequence: 1
depends_on: []
status: needs-review
risk: medium
goal: Independently testable result produced by this work item.
files:
  create: []
  modify:
    - exact/path/to/existing.py
  test:
    - tests/exact/path/to/test_existing.py
interfaces:
  consumes: []
  produces: []
spec_criteria:
  - Exact acceptance criterion from the feature spec
definition_of_done:
  - Observable completion condition
constraints:
  - Relevant non-goal or implementation constraint
validation:
  - command: python -m pytest tests/exact/path/to/test_existing.py -q
    expected: Tests pass.
links:
  issues: []
  prs: []
```

Do not leave placeholder text from the example in real work items. Use exact paths when repository evidence identifies them. If a path genuinely cannot be known before discovery, create one bounded discovery work item with a concrete output instead of making every downstream item vague.

Use `status: needs-review` for a newly written plan. Use `status: ready-for-build` only when the user explicitly approves the written work items, or when syncing unchanged work items that were already approved under a `ready-for-build` feature.

## Planning Rules

- Map likely create, modify, and test paths and their responsibilities before choosing task boundaries.
- Make each work item the smallest unit that has its own test cycle and warrants an independent issue-to-PR review. Do not split it into Superpowers-style 2–5 minute microsteps; `loop-engineer-issue` performs that execution planning inside the loop run.
- Order work items with `sequence` and `depends_on`. Keep dependencies acyclic.
- Name interfaces that later work items consume. An isolated implementing agent must understand neighboring contracts without reading their internals.
- Trace every work item to exact feature acceptance criteria with `spec_criteria`.
- Include exact validation commands and expected results. Avoid vague instructions such as "add tests" or "handle edge cases."
- Fold setup, documentation, configuration, and migrations into the task whose deliverable requires them unless they have a separately reviewable outcome.

## Workflow

1. Read the feature problem, chosen approach, scope, non-goals, dependencies, acceptance criteria, validation, and risk.
2. Check that the spec describes one coherent feature. If it contains independent subsystems, report that the spec needs decomposition instead of producing a misleading plan.
3. Map current file responsibilities and define the intended file and interface boundaries.
4. Split the feature into ordered tasks that each fit one loop run. Keep high-risk work smaller and preserve approval requirements.
5. Avoid duplicate work items by comparing existing `.product/work-items/*.yaml`.
6. Create or update work item YAML files with `status: needs-review`.
7. Self-review the complete plan using the Plan Gate in `${CLAUDE_PLUGIN_ROOT}/references/product-planning.md`. Fix coverage gaps, placeholders, ambiguous completion conditions, dependency cycles, inconsistent interfaces, vague paths, and non-executable validation inline.
8. Run `python ${CLAUDE_PLUGIN_ROOT}/scripts/loop_product_os.py validate --root .`.
9. Commit the `.product` changes per Committing .product Changes in `${CLAUDE_PLUGIN_ROOT}/references/product-os.md`.
10. Present the ordered plan, acceptance-criterion coverage, dependencies, and validation commands, then ask the user to review the written work items.
11. Only after explicit plan approval, set the approved work items and matching roadmap feature to `ready-for-build`, validate, and commit the approval state. Leave the feature spec at `spec-approved`.
12. When creating GitHub Issues, first ensure the feature's milestone exists so every issue can be grouped under it: `python ${CLAUDE_PLUGIN_ROOT}/scripts/loop_gh_milestone.py ensure --title {feature-id} --description "{feature-title}"`. The milestone title is the feature id (see `${CLAUDE_PLUGIN_ROOT}/references/product-os.md`).
13. Create GitHub Issues only from plan-approved `ready-for-build` work items and only when explicitly requested or syncing existing ready work items. Attach each issue to the feature milestone with `gh issue create --milestone {feature-id}`. Each issue must include the feature id, work item id, goal, paths, dependencies, interfaces, spec criteria, definition of done, non-goals, risk, and validation commands with expected results. Immediately after each `gh issue create`, record the link back on the work item with `python ${CLAUDE_PLUGIN_ROOT}/scripts/loop_product_os.py work-item --root . --id {work-item-id} --issue {number}` — without the stored link, execution state cannot be derived from the issue later (see Linking Work Items to Issues in `${CLAUDE_PLUGIN_ROOT}/references/product-os.md`).
14. Label generated execution issues with `kind:feature` and `loop:ready` only when the work item is ready, scoped, and verification is clear.
15. Do not add protected labels such as `security`, `data-loss`, `migration`, or `needs-human` to an issue that also has `loop:ready`. `loop-engineer-issue` treats protected labels as a stop condition, so `loop:ready` plus a protected label is an invalid execution state.
16. If a work item has a security-, permission-, credential-, migration-, billing-, or data-loss-sensitive concern but is still approved for loop execution, record the concern in the issue body and use non-blocking labels such as `area:security`, `area:permissions`, or `risk:medium` when the repository uses them. Do not use protected labels for non-blocking risk metadata.
17. If a work item truly requires human handling before implementation, do not mark it `loop:ready`. Use `loop:blocked` plus `loop:needs-human` and add the relevant protected label. When policy `notify_mentions` is non-empty (read `.loop-engineering.yml` through `${CLAUDE_PLUGIN_ROOT}/scripts/loop_repo_policy.py`), @mention every listed username in the issue and assign the first one with `gh issue edit <number> --add-assignee <username>`, so GitHub's native notifications reach a human.
18. Report created work items, skipped duplicates, review or approval state, created issues, the feature milestone, and any items needing human review.

## Boundaries

Do not implement code, create branches, or open pull requests.

Do not approve a feature spec.

Do not treat spec approval as plan approval. Newly generated work items require their own review gate before they become execution issues.

Do not bypass GitHub Issues by sending `.product/work-items` directly to `loop-engineer-issue`.

Do not mark high-risk work `loop:ready` without human approval.

Do not combine `loop:ready` with protected labels. If the task should run after approval, keep protected labels off the execution issue and document the risk in the body or non-blocking labels. If the task should not run automatically, omit `loop:ready` and mark it blocked for human handling.
