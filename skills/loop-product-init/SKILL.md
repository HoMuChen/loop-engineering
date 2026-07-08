---
name: loop-product-init
description: Use to initialize or repair the .product Product OS directory for a repository, including product brief, roadmap, feature spec, work item, decision, feedback, metrics, and release note structure.
---

# Loop Product Init

Initialize the Product OS layer for a product repository. Treat `.product/` as the product source of truth and GitHub Issues as the execution source of truth.

## Required Setup

- Confirm the current directory is the target product repository.
- Confirm the repository is under git.
- Read repository instructions such as `AGENTS.md`, `CLAUDE.md`, or equivalent when present.
- Read `../../references/product-os.md`.

## Workflow

1. Run `python ../../scripts/loop_product_os.py init --root .`.
2. If the product owner is known, pass `--owner <name>`.
3. Preserve existing `.product/` files. The init command is idempotent and only creates missing directories or files.
4. Run `python ../../scripts/loop_product_os.py validate --root .`.
5. Report created files, preserved files, validation warnings, and next required human inputs.

## Boundaries

Do not overwrite an existing product brief, roadmap, feature spec, work item, decision, feedback file, metric, or release note without explicit user approval.

Do not infer product strategy beyond TODO placeholders during initialization.

Do not create GitHub Issues, branches, pull requests, or code changes. This skill only initializes or repairs the Product OS structure.
