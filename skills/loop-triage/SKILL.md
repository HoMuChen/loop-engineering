---
name: loop-triage
description: Use to classify open GitHub Issues, add loop labels, mark ready issues, and ask for missing information without changing code.
---

# Loop Triage

> Paths below use `${CLAUDE_PLUGIN_ROOT}` — this plugin's install directory. Claude Code substitutes it automatically; tools that do not (e.g. Codex) should resolve it as the plugin root, not the target repo.

Scan open GitHub Issues and prepare them for agent work.

## Required Setup

- Run `gh auth status`.
- Ensure the loop label set exists with `python ${CLAUDE_PLUGIN_ROOT}/scripts/loop_labels.py ensure`. This is an idempotent upsert; a repository that has never run the loop otherwise fails the first `--add-label` call.
- Read `.loop-engineering.yml` through `${CLAUDE_PLUGIN_ROOT}/scripts/loop_repo_policy.py`. Note `notify_mentions`.

## Workflow

1. Use `gh issue list --state open --json number,title,labels,assignees,url`.
2. Classify each issue as `kind:bug`, `kind:feature`, `kind:refactor`, `kind:docs`, or `kind:chore`.
3. Add priority and area labels when the issue text makes the choice clear.
4. Add `loop:ready` only when the issue has enough information for implementation and verification.
5. Add `loop:needs-human` when information is missing.
6. Ask one concrete question using `${CLAUDE_PLUGIN_ROOT}/templates/comments/triage-question.md`. When `notify_mentions` is non-empty, fill the template's cc line by @mentioning every listed username and assign the first one with `gh issue edit <number> --add-assignee <username>`, so GitHub's native notifications reach a human; drop the cc line when `notify_mentions` is empty.

Do not edit code, create branches, open PRs, merge, or close issues.
