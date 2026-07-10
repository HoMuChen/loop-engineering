---
name: loop-product-review
description: Use to review Product OS state by reading .product, GitHub Issues, pull requests, and loop run metadata, then summarize product progress, blockers, risks, and recommended next steps without changing code.
---

# Loop Product Review

> Paths below use `${CLAUDE_PLUGIN_ROOT}` — this plugin's install directory. Claude Code substitutes it automatically; tools that do not (e.g. Codex) should resolve it as the plugin root, not the target repo.

Review product progress from Product OS and the GitHub Issue engineering loop. Produce a factual product status report and recommendations.

## Required Setup

- Run `gh auth status` when GitHub state is needed.
- Confirm the current directory is a git repository with a GitHub remote.
- Read repository instructions such as `AGENTS.md`, `CLAUDE.md`, or equivalent when present.
- Read `${CLAUDE_PLUGIN_ROOT}/references/product-os.md`.
- Run `python ${CLAUDE_PLUGIN_ROOT}/scripts/loop_product_os.py validate --root .`.
- Run `python ${CLAUDE_PLUGIN_ROOT}/scripts/loop_product_os.py status --root . --json`.

## Workflow

1. Read `.product/product-brief.md`.
2. Read `.product/roadmap.yaml`.
3. Read relevant `.product/feature-specs/*.yaml` and `.product/work-items/*.yaml`.
4. Inspect open GitHub Issues with `gh issue list --state open --json number,title,labels,url`.
5. Inspect pull requests with `gh pr list --state all --limit 50 --json number,title,state,labels,url,mergeStateStatus`.
6. Inspect feature milestones with `python ${CLAUDE_PLUGIN_ROOT}/scripts/loop_gh_milestone.py list` to read per-feature completion progress (a milestone maps to one feature; see `${CLAUDE_PLUGIN_ROOT}/references/product-os.md`).
7. Inspect structured loop run comments when needed.
8. Derive each work item's execution state from its `links.issues` at read time — `loop:claimed`/`loop:in-progress`/`loop:repairing` mean in-progress, `loop:blocked` means blocked, `loop:pr-open` means in-review (see Work Item Statuses in `${CLAUDE_PLUGIN_ROOT}/references/product-os.md`). Work item YAML stores intent (`draft`, `needs-review`, `ready-for-build`) and the terminal `done` only; a stored `in-progress`/`blocked`/`in-review` is itself a state inconsistency to report.
9. Compare roadmap and work item status with issue, PR, and milestone facts.
10. Report completed work, in-progress work, blockers, stale or inconsistent state, risk, and next recommended action.

## Output

Use this structure:

- Product snapshot
- Completed since last review, when inferable
- Current roadmap status, with feature milestone completion progress when available
- Active work items and PRs
- Blockers and risks
- State inconsistencies
- Recommended next steps

Clearly distinguish facts from recommendations.

## Boundaries

Do not modify roadmap priority, scope, or status unless explicitly asked.

Do not create or edit code, branches, pull requests, or GitHub Issues.

Do not approve specs, move features from Next to Now, or mark high-risk work ready for build. Recommend those actions for a human instead.
