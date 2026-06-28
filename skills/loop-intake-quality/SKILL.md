---
name: loop-intake-quality
description: Use to scan a repository for quality and safety findings (security, vulnerabilities, dependency health, bugs, UI/UX, accessibility) and file them as deduplicated, ready-to-work GitHub Issues without changing code.
---

# Loop Intake Quality

Generate work for the loop from the codebase itself. This skill is the source of quality-driven issues: it scans, then files well-scoped issues that the rest of the loop can pick up. It is reactive to evidence, not to product strategy — for feature ideas use a product intake instead.

## Required Setup

- Run `gh auth status`.
- Confirm the current directory is a git repository with a GitHub remote.
- Read repository instructions such as `AGENTS.md`, `CLAUDE.md`, or equivalent.
- Read `.loop-engineering.yml` through `scripts/loop_repo_policy.py`. Note `intake_issue_limit`.

## Scan Categories

Use whatever tooling the repository already provides, plus reading the code. Cover:

- **Security and vulnerabilities**: SAST output, secret leaks, injection or auth flaws, unsafe deserialization.
- **Dependency health**: known CVEs, abandoned or pinned-vulnerable packages (e.g. `gh`/`npm audit`/`pip-audit`/dependabot alerts).
- **Bugs and correctness**: crashes, unhandled errors, race conditions, obvious logic defects, `TODO`/`FIXME` that mark real defects.
- **UI/UX and accessibility**: WCAG/contrast/keyboard failures, broken responsive layout, confusing flows (e.g. lighthouse/axe output).

## Workflow

1. List existing open issues with `gh issue list --state open --json number,title,labels,url`.
2. Run the scans above and collect candidate findings.
3. **Deduplicate**: drop any finding that matches an existing open issue by area and root cause. Never refile a finding that is already tracked.
4. Rank the remaining findings by severity and impact. Keep at most `intake_issue_limit` for this run.
5. For each kept finding, create an issue with `gh issue create` containing:
   - A clear problem statement and evidence (`file:line`, tool output, repro).
   - A proposed fix direction and acceptance criteria.
   - Suggested verification commands.
6. Label each issue:
   - A `kind:` label matching `loop-triage` taxonomy (`kind:bug`, `kind:refactor`, `kind:chore`, etc.).
   - Topical/area labels when the choice is clear.
   - `loop:ready` only when the finding is self-justifying with concrete acceptance criteria and verification; otherwise `loop:needs-human`.
   - A protected label (e.g. `security`) for findings with real exploitability or data risk, so `loop-engineer-issue` routes them to a human instead of auto-fixing.
7. If findings were dropped by `intake_issue_limit` or dedup, leave a short summary comment or log noting what was deferred. Do not silently truncate.

## Boundaries

Do not edit code, create branches, open PRs, merge, or close issues. This skill only files prepared issues.
