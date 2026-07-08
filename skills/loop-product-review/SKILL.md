---
name: loop-product-review
description: Use to review Product OS state by reading .product, GitHub Issues, pull requests, and loop run metadata, then summarize product progress, blockers, risks, and recommended next steps without changing code.
---

# Loop Product Review

Review product progress from Product OS and the GitHub Issue engineering loop. Produce a factual product status report and recommendations.

## Required Setup

- Run `gh auth status` when GitHub state is needed.
- Confirm the current directory is a git repository with a GitHub remote.
- Read repository instructions such as `AGENTS.md`, `CLAUDE.md`, or equivalent when present.
- Read `../../references/product-os.md`.
- Run `python ../../scripts/loop_product_os.py validate --root .`.
- Run `python ../../scripts/loop_product_os.py status --root . --json`.

## Workflow

1. Read `.product/product-brief.md`.
2. Read `.product/roadmap.yaml`.
3. Read relevant `.product/feature-specs/*.yaml` and `.product/work-items/*.yaml`.
4. Inspect open GitHub Issues with `gh issue list --state open --json number,title,labels,url`.
5. Inspect pull requests with `gh pr list --state all --limit 50 --json number,title,state,labels,url,mergeStateStatus`.
6. Inspect structured loop run comments when needed.
7. Compare roadmap and work item status with issue and PR facts.
8. Report completed work, in-progress work, blockers, stale or inconsistent state, risk, and next recommended action.

## Output

Use this structure:

- Product snapshot
- Completed since last review, when inferable
- Current roadmap status
- Active work items and PRs
- Blockers and risks
- State inconsistencies
- Recommended next steps

Clearly distinguish facts from recommendations.

## Boundaries

Do not modify roadmap priority, scope, or status unless explicitly asked.

Do not create or edit code, branches, pull requests, or GitHub Issues.

Do not approve specs, move features from Next to Now, or mark high-risk work ready for build. Recommend those actions for a human instead.
