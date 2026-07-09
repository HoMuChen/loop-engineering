---
name: loop-triage
description: Use to classify open GitHub Issues, add loop labels, mark ready issues, and ask for missing information without changing code.
---

# Loop Triage

Scan open GitHub Issues and prepare them for agent work.

## Required Setup

- Run `gh auth status`.
- Ensure the loop label set exists with `python ../../scripts/loop_labels.py ensure`. This is an idempotent upsert; a repository that has never run the loop otherwise fails the first `--add-label` call.

## Workflow

1. Use `gh issue list --state open --json number,title,labels,assignees,url`.
2. Classify each issue as `kind:bug`, `kind:feature`, `kind:refactor`, `kind:docs`, or `kind:chore`.
3. Add priority and area labels when the issue text makes the choice clear.
4. Add `loop:ready` only when the issue has enough information for implementation and verification.
5. Add `loop:needs-human` when information is missing.
6. Ask one concrete question using `templates/comments/triage-question.md`.

Do not edit code, create branches, open PRs, merge, or close issues.
