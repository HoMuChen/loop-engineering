# Loop Engineering

Loop Engineering is a portable Claude Code and Codex plugin for agentic software work managed through GitHub Issues, with an optional Product OS layer for turning product strategy into scoped engineering work.

The engineering loop uses:

- GitHub Issues as the source of truth.
- Labels for current workflow state.
- Structured issue comments for run metadata.
- GitHub CLI (`gh`) for all GitHub operations.
- Python helper scripts that emit stable JSON.

The Product OS layer adds:

- `.product/` as the product source of truth.
- Roadmap, feature specs, work items, decisions, feedback, metrics, and release notes.
- A guarded path from product intent to ready GitHub Issues.

## Requirements

- Python 3.11+
- GitHub CLI installed and authenticated with `gh auth status`
- A git repository with a GitHub remote

## Skills

- `loop-product-init`: initialize or repair `.product/`.
- `loop-product-review`: summarize product progress, blockers, risks, and next steps.
- `loop-spec-feature`: draft feature specs from roadmap items.
- `loop-split-feature`: split approved specs into work items and optionally prepared issues.
- `loop-intake-quality`: scan the repo and file quality/safety findings as ready issues.
- `loop-triage`: classify and prepare issues.
- `loop-engineer-issue`: full issue loop from claim through close.
- `loop-review-pr`: review loop PRs.
- `loop-recover`: recover stale loop runs.
- `loop-close`: finalize merged work.

The loop is reactive to GitHub Issues. `loop-intake-quality` generates quality-driven work (security, vulnerabilities, bugs, UI/UX). Product OS skills generate product-driven specs and work items, then hand execution to GitHub Issues instead of bypassing the issue loop.

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
| Initialize Product OS | `Initialize Product OS for this repo` | `loop-product-init` |
| Review product progress | `Review the current Product OS status` | `loop-product-review` |
| Draft a feature spec | `Draft the next Product OS feature spec` | `loop-spec-feature` |
| Split an approved feature | `Split the approved feature into work items` | `loop-split-feature` |
| Generate quality/safety issues from the code | `Scan this repo for quality and security issues` | `loop-intake-quality` |
| Prepare new issues for agents | `Triage open loop engineering issues` | `loop-triage` |
| Run an issue end-to-end | `Take GitHub issue #123 through the loop` | `loop-engineer-issue` |
| Review an open loop PR | `Review loop engineering PR #45` | `loop-review-pr` |
| Resume or unblock stuck runs | `Recover stale loop engineering runs` | `loop-recover` |
| Finalize merged work | `Close loop engineering issue #123` | `loop-close` |

A typical full loop:

1. `loop-product-init` creates `.product/` for product-driven repositories.
2. `loop-spec-feature` drafts feature specs from roadmap items that need specs.
3. `loop-split-feature` splits approved specs into small work items and prepared issues.
4. `loop-triage` scans open issues, applies `kind:*` / priority / area labels, and marks ready issues `loop:ready`.
5. `loop-engineer-issue` claims a `loop:ready` issue, plans, implements, verifies, opens a PR, repairs CI or review failures, then merges.
6. `loop-review-pr` reviews the PR bug-first and routes it back to repair or to a human when needed.
7. `loop-recover` reconciles issue labels against branch, PR, CI, and review state for any stale runs.
8. `loop-close` adds a final summary, cleans transient labels, and closes the issue.

## Product OS

Product OS is optional but recommended for autonomous product development. It makes product context explicit before coding starts:

```text
.product/
  product-os.yaml
  product-brief.md
  roadmap.yaml
  feature-specs/
  work-items/
  decisions/
  feedback/
  metrics.md
  release-notes/
```

Use `.product/` as the product source of truth and GitHub Issues as the execution source of truth. Agents may draft specs, split approved specs, update progress from facts, summarize feedback, and recommend roadmap changes. Agents must not independently change product priority, expand MVP scope, approve high-risk work, or implement directly from roadmap entries.

Initialize it with:

```bash
python scripts/loop_product_os.py init --root .
python scripts/loop_product_os.py validate --root .
python scripts/loop_product_os.py status --root . --json
```

Behavior is governed per repository by `.loop-engineering.yml` (see [Repository Policy](#repository-policy)). Before doing anything, the skills run `gh auth status`, confirm a GitHub remote exists, and read repository instructions (`AGENTS.md`, `CLAUDE.md`) plus the policy file.

## Local Verification

```bash
python -m pytest -q
claude plugin validate .
python -m json.tool .codex-plugin/plugin.json
python -m json.tool .agents/plugins/marketplace.json
python scripts/loop_repo_policy.py
python scripts/loop_product_os.py init --root /tmp/loop-product-os-check
python scripts/loop_product_os.py validate --root /tmp/loop-product-os-check
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
  max_concurrent_runs: 1
  worktree_root: .loop/worktrees
```

## Running on a Schedule

The five skills are stages of a label-driven state machine, so they can run as independent scheduled jobs — GitHub Issue labels are the only shared state. A common layout:

```cron
# Generate quality/safety issues from the codebase (nightly is plenty)
0 3 * * *     cd /path/to/repo && claude -p "Scan this repo for quality and security issues"
# Prepare new issues
*/15 * * * *  cd /path/to/repo && claude -p "Triage open loop engineering issues"
# Work ready issues (parallel-safe via worktrees + max_concurrent_runs)
*/7  * * * *  cd /path/to/repo && claude -p "Take the next ready loop engineering issue through the loop"
# Review open loop PRs
*/10 * * * *  cd /path/to/repo && claude -p "Review open loop engineering PRs"
# Watchdog: recover stale runs and clean orphaned worktrees
*/30 * * * *  cd /path/to/repo && claude -p "Recover stale loop engineering runs"
```

### Concurrency model

`loop-engineer-issue` runs are parallel-safe: each works in its own git worktree under `worktree_root`, so concurrent runs never share a working tree. `max_concurrent_runs` caps how many run at once. It is a **soft cap** counted from the active loop labels (`loop:claimed`, `loop:in-progress`, `loop:repairing`), enforced optimistically — it can briefly overshoot when runs start in the same instant, but per-issue claiming stays exclusive, so no two runs ever touch the same issue.

For a hard guarantee that only one run executes at a time (e.g. limited resources or shared state), keep `max_concurrent_runs: 1` and wrap the cron line in `flock`:

```cron
*/7 * * * * flock -n /tmp/loop-engineer.lock sh -c 'cd /path/to/repo && claude -p "Take the next ready loop engineering issue through the loop"'
```

`loop-recover` removes orphaned worktrees left by crashed or stale runs, which also frees their slot against the cap.
