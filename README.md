# Loop Engineering

Loop Engineering is a portable Claude Code and Codex plugin for agentic software work managed through GitHub Issues.

The v1 workflow uses:

- GitHub Issues as the source of truth.
- Labels for current workflow state.
- Structured issue comments for run metadata.
- GitHub CLI (`gh`) for all GitHub operations.
- Python helper scripts that emit stable JSON.

## Requirements

- Python 3.11+
- GitHub CLI installed and authenticated with `gh auth status`
- A git repository with a GitHub remote

## Skills

- `loop-engineer-issue`: full issue loop from claim through close.
- `loop-triage`: classify and prepare issues.
- `loop-review-pr`: review loop PRs.
- `loop-recover`: recover stale loop runs.
- `loop-close`: finalize merged work.

## Claude Code Installation

Register this repository as a local marketplace, then install the plugin:

```bash
claude plugin marketplace add HoMuChen/loop-engineering
claude plugin install loop-engineering@loop-engineering
```

Inside Claude Code, the same flow is available through slash commands:

```text
/plugin marketplace add HoMuChen/loop-engineering
/plugin install loop-engineering@loop-engineering
```

Claude Code loads the plugin manifest from `.claude-plugin/plugin.json` and auto-discovers the skills in `skills/`.

## Codex Installation

Codex discovers the plugin from the agents marketplace defined in `.agents/plugins/marketplace.json`, which points at this repository (`source.path: "."`).

Register this repository as a marketplace source and install the plugin:

```bash
codex plugin marketplace add HoMuChen/loop-engineering
codex plugin install loop-engineering
```

Codex loads the manifest from `.codex-plugin/plugin.json` and auto-discovers the same skills in `skills/`. No code changes are needed to share skills between the two tools — both read the `skills/` directory.

## Usage

The skills are activated by natural language. Once installed in either tool, describe the task and the matching skill loads automatically. Suggested starting prompts:

| Goal | Prompt | Skill |
| --- | --- | --- |
| Prepare new issues for agents | `Triage open loop engineering issues` | `loop-triage` |
| Run an issue end-to-end | `Take GitHub issue #123 through the loop` | `loop-engineer-issue` |
| Review an open loop PR | `Review loop engineering PR #45` | `loop-review-pr` |
| Resume or unblock stuck runs | `Recover stale loop engineering runs` | `loop-recover` |
| Finalize merged work | `Close loop engineering issue #123` | `loop-close` |

A typical full loop:

1. `loop-triage` scans open issues, applies `kind:*` / priority / area labels, and marks ready issues `loop:ready`.
2. `loop-engineer-issue` claims a `loop:ready` issue, plans, implements, verifies, opens a PR, repairs CI or review failures, then merges.
3. `loop-review-pr` reviews the PR bug-first and routes it back to repair or to a human when needed.
4. `loop-recover` reconciles issue labels against branch, PR, CI, and review state for any stale runs.
5. `loop-close` adds a final summary, cleans transient labels, and closes the issue.

Behavior is governed per repository by `.loop-engineering.yml` (see [Repository Policy](#repository-policy)). Before doing anything, the skills run `gh auth status`, confirm a GitHub remote exists, and read repository instructions (`AGENTS.md`, `CLAUDE.md`) plus the policy file.

## Local Verification

```bash
python -m pytest -q
claude plugin validate .
python -m json.tool .codex-plugin/plugin.json
python -m json.tool .agents/plugins/marketplace.json
python scripts/loop_repo_policy.py
```

## Repository Policy

Repositories can define `.loop-engineering.yml`:

```yaml
loop_engineering:
  default_agent: codex
  branch_prefix: loop/
  merge_method: squash
  stale_after_minutes: 120
  required_verification:
    - pnpm typecheck
    - pnpm test
  protected_labels:
    - needs-human
    - security
  auto_merge: true
  auto_close: true
  local_repair_limit: 3
  pr_repair_limit: 2
```
