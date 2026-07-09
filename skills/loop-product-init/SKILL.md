---
name: loop-product-init
description: Use to initialize or repair the .product Product OS directory for a repository, then inspect the codebase and guide the user through drafting product brief and roadmap content.
---

# Loop Product Init

> Paths below use `${CLAUDE_PLUGIN_ROOT}` — this plugin's install directory. Claude Code substitutes it automatically; tools that do not (e.g. Codex) should resolve it as the plugin root, not the target repo.

Initialize the Product OS layer for a product repository. Treat `.product/` as the product source of truth and GitHub Issues as the execution source of truth.

Initialization has two phases:

1. Bootstrap the safe file structure.
2. Discover product context from the repo, discuss uncertainties with the user, and write product content only after approval.

## Required Setup

- Confirm the current directory is the target product repository.
- Confirm the repository is under git.
- Read repository instructions such as `AGENTS.md`, `CLAUDE.md`, or equivalent when present.
- Read `${CLAUDE_PLUGIN_ROOT}/references/product-os.md`.

## Workflow

1. Run `python ${CLAUDE_PLUGIN_ROOT}/scripts/loop_product_os.py init --root .`.
2. If the product owner is known, pass `--owner <name>`.
3. Preserve existing `.product/` files. The init command is idempotent and only creates missing directories or files.
4. Inspect the repository to infer product context from evidence:
   - `README.md`, docs, marketing copy, screenshots, examples, or demos.
   - `package.json`, `pyproject.toml`, app manifests, routes, API schemas, database schemas, migrations, fixtures, tests, and seed data.
   - Existing GitHub Issues and PRs when GitHub is available.
   - Existing product notes such as `AGENTS.md`, `CLAUDE.md`, planning docs, or changelogs.
5. Draft a short Product OS proposal with:
   - Evidence-backed product summary.
   - Clear assumptions.
   - Open questions.
   - Proposed `.product/product-brief.md`.
   - Proposed `.product/roadmap.yaml` with Now / Next / Later / Icebox.
6. Ask the user to confirm or correct the proposal before replacing TODO content.
7. After approval, update `.product/product-brief.md`, `.product/roadmap.yaml`, and optionally `.product/decisions/{date}-initial-product-os.md`.
8. Run `python ${CLAUDE_PLUGIN_ROOT}/scripts/loop_product_os.py validate --root .`.
9. Report created files, preserved files, written product content, validation warnings, and next required human inputs.

## Discovery Rules

Separate facts from assumptions. Cite concrete repo evidence by file path when explaining why a product statement was inferred.

Prefer asking a few high-impact questions over inventing strategy. At minimum, clarify target users, MVP scope, and non-goals when they are not evident from the codebase.

Keep generated roadmap conservative. Use `needs-spec` for features that require product definition, `spec-approved` only when the user has already approved the spec, and `ready-for-build` only when scope and validation are clear.

If the user explicitly asks for a quick init or repair only, stop after creating or repairing the skeleton and validating it.

## Boundaries

Do not overwrite an existing product brief, roadmap, feature spec, work item, decision, feedback file, metric, or release note without explicit user approval.

Do not write inferred product strategy into `.product/` without explicit user approval.

Do not mark features `spec-approved` or `ready-for-build` unless the user approves that status.

Do not create GitHub Issues, branches, pull requests, or code changes. This skill only initializes or repairs the Product OS structure.
