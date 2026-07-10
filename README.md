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
- GitHub Milestones (one per feature) that group a feature's work-item issues and track completion progress.

## Requirements

- Python 3.11+
- GitHub CLI installed and authenticated with `gh auth status`
- A git repository with a GitHub remote

## Skills

- `loop-product-init`: initialize or repair `.product/`, inspect the repo, and guide the first product brief / roadmap draft.
- `loop-product-review`: summarize product progress, blockers, risks, and next steps.
- `loop-roadmap-update`: apply explicit user-approved changes to `.product/roadmap.yaml`.
- `loop-spec-feature`: draft feature specs from roadmap items.
- `loop-split-feature`: split approved specs into work items and optionally prepared issues.
- `loop-intake-quality`: scan the repo and file quality/safety findings as ready issues.
- `loop-triage`: classify and prepare issues.
- `loop-engineer-issue`: full issue loop from claim through close.
- `loop-review-pr`: review loop PRs and merge approved ones when policy allows.
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

## Helper script paths

The skills invoke the bundled helper scripts, references, and templates through `${CLAUDE_PLUGIN_ROOT}` — the absolute path to this plugin's install directory. This matters because the loop operates on a **target** repository: the working directory is that repo, not the plugin, so a bare `scripts/...` path would not resolve.

- **Claude Code** substitutes `${CLAUDE_PLUGIN_ROOT}` inline in skill content before the agent runs, so the commands resolve to the installed plugin directory automatically. This is the [documented plugin path variable](https://code.claude.com/docs/en/plugins-reference).
- **Codex** and other tools that do not substitute the variable should treat it as this plugin's root directory (where the `skills/`, `scripts/`, and `templates/` folders live) and resolve the same relative path there. Codex has no equivalent placeholder, so the skills state this convention explicitly.

When developing inside this repository (not running it as an installed plugin against another repo), the plugin root is the repo root, so the `python scripts/...` commands in [Local Verification](#local-verification) run as written.

## Usage

The skills are activated by natural language. Once installed in either tool, describe the task and the matching skill loads automatically. You can run prompts interactively, or non-interactively from a scheduler:

```bash
claude -p "Review the current Product OS status"
codex exec "Review the current Product OS status"
```

### Skill triggers

| Goal | Prompt | Skill |
| --- | --- | --- |
| Initialize Product OS | `Initialize Product OS for this repo and draft it from the codebase` | `loop-product-init` |
| Review product progress | `Review the current Product OS status` | `loop-product-review` |
| Update roadmap | `Update Product OS roadmap: move line-inbox-v1 to now and set status to ready-for-build` | `loop-roadmap-update` |
| Draft a feature spec | `Draft the next Product OS feature spec` | `loop-spec-feature` |
| Split an approved feature | `Split the approved feature into work items` | `loop-split-feature` |
| Generate quality/safety issues from the code | `Scan this repo for quality and security issues` | `loop-intake-quality` |
| Prepare new issues for agents | `Triage open loop engineering issues` | `loop-triage` |
| Run an issue end-to-end | `Take GitHub issue #123 through the loop` | `loop-engineer-issue` |
| Review an open loop PR | `Review loop engineering PR #45` | `loop-review-pr` |
| Resume or unblock stuck runs | `Recover stale loop engineering runs` | `loop-recover` |
| Finalize merged work | `Close loop engineering issue #123` | `loop-close` |

### Operating cycle

Use the plugin as a product-to-PR pipeline:

1. `loop-product-init` creates `.product/` for product-driven repositories.
2. `loop-product-init` inspects the codebase, drafts product brief / roadmap content, and asks a human to confirm assumptions.
3. A human approves or corrects `.product/product-brief.md` and `.product/roadmap.yaml`.
4. `loop-roadmap-update` applies explicit human-approved roadmap changes.
5. `loop-spec-feature` drafts specs for roadmap items with `needs-spec`.
6. A human reviews the spec and changes its status to `spec-approved` or `ready-for-build`.
7. `loop-split-feature` splits approved specs into small work items and, when allowed, GitHub Issues.
8. `loop-triage` scans open issues, applies `kind:*` / priority / area labels, and marks actionable issues `loop:ready`.
9. `loop-engineer-issue` claims one `loop:ready` issue, plans, implements, verifies, opens a PR, repairs CI or review failures, then merges when policy allows.
10. `loop-review-pr` reviews the PR bug-first, merges it when the review passes, CI is green, and `auto_merge` allows, or routes it back to repair or to a human when needed.
11. `loop-recover` reconciles issue labels against branch, PR, CI, and review state for stale runs, and reconciles `.product` work items against closed issues so a missed close cannot leave permanent drift.
12. `loop-close` adds a final summary, cleans transient labels, and closes completed issues.
13. `loop-product-review` summarizes product progress, blockers, risks, and recommended next steps.

### Recommended cadence

| Skill | Trigger | Suggested cadence | Writes |
| --- | --- | --- | --- |
| `loop-product-init` | `Initialize Product OS for this repo and draft it from the codebase` | Once per repo, then only when repairing missing Product OS files | `.product/` skeleton, then approved product brief / roadmap content |
| `loop-product-review` | `Review the current Product OS status` | Daily or weekly; also before planning sessions | Report only by default |
| `loop-roadmap-update` | `Update Product OS roadmap: move line-inbox-v1 to now` | On demand after explicit product direction | `.product/roadmap.yaml`, optional decision note |
| `loop-spec-feature` | `Draft the next Product OS feature spec` | Daily or on demand while roadmap has `needs-spec` items | `.product/feature-specs/*.yaml` |
| `loop-split-feature` | `Split the approved feature into work items` | After human spec approval | `.product/work-items/*.yaml`, optional GitHub Issues |
| `loop-intake-quality` | `Scan this repo for quality and security issues` | Nightly or weekly | GitHub Issues |
| `loop-triage` | `Triage open loop engineering issues` | Every 15-30 minutes, or before build runs | GitHub labels/comments |
| `loop-engineer-issue` | `Take the next ready or repairing loop engineering issue through the loop` | Every 5-15 minutes, capped by `max_concurrent_runs` | Branches, PRs, labels/comments |
| `loop-review-pr` | `Review open loop engineering PRs` | Every 10-30 minutes | PR review comments, labels, merges when `auto_merge` allows |
| `loop-recover` | `Recover stale loop engineering runs` | Every 30-60 minutes | Labels/comments, worktree cleanup, `.product` work-item reconciliation |
| `loop-close` | `Close completed loop engineering issues` | Every 30-60 minutes, or after merge | Issue comments/labels/close |

### First-time setup for a product repo

After installing the plugin in Claude Code or Codex, go to the target product repository and run:

```bash
claude -p "Initialize Product OS for this repo and draft it from the codebase"
```

or:

```bash
codex exec "Initialize Product OS for this repo and draft it from the codebase"
```

The init agent first creates the `.product/` skeleton, then inspects the codebase and existing docs to propose initial content for:

```text
.product/product-brief.md
.product/roadmap.yaml
```

It should separate repo-backed facts from assumptions, ask you to confirm target users / MVP scope / non-goals when unclear, and only write non-placeholder product strategy after approval.

Set roadmap items to statuses such as `needs-spec`, `spec-approved`, or `ready-for-build`. Product OS skills can draft and split work, but humans should approve product priority, MVP scope, and high-risk features.

The loop relies on a set of labels (`loop:*`, `kind:*`, `agent:*`, `run:stale`, and the protected labels). `loop-triage` and `loop-intake-quality` ensure them automatically on each run, so a brand-new repository does not fail its first labeling call. To pre-create them yourself, run the helper from the plugin's own directory (see [Helper script paths](#helper-script-paths)):

```bash
python "$CLAUDE_PLUGIN_ROOT/scripts/loop_labels.py" ensure
```

To change roadmap state through conversation, use an explicit instruction:

```bash
claude -p "Update Product OS roadmap: move line-inbox-v1 to now and set status to ready-for-build"
codex exec "Update Product OS roadmap: add human-handoff to next as needs-spec"
```

Exploratory prompts such as "what should we do next?" should produce recommendations, not direct roadmap edits.

### Typical product development flow

```bash
# 1. Draft a spec from roadmap.needs-spec
claude -p "Draft the next Product OS feature spec"

# 2. Apply an explicit human-approved roadmap change when needed
claude -p "Update Product OS roadmap: move line-inbox-v1 to now"

# 3. After human review and approval, split the feature
claude -p "Split the approved feature into work items"

# 4. Prepare GitHub Issues for execution
claude -p "Triage open loop engineering issues"

# 5. Build one ready issue
claude -p "Take the next ready or repairing loop engineering issue through the loop"

# 6. Review and recover
claude -p "Review open loop engineering PRs"
claude -p "Recover stale loop engineering runs"

# 7. Summarize product state
claude -p "Review the current Product OS status"
```

Codex equivalent:

```bash
codex exec "Draft the next Product OS feature spec"
codex exec "Update Product OS roadmap: move line-inbox-v1 to now"
codex exec "Split the approved feature into work items"
codex exec "Triage open loop engineering issues"
codex exec "Take the next ready or repairing loop engineering issue through the loop"
codex exec "Review open loop engineering PRs"
codex exec "Recover stale loop engineering runs"
codex exec "Review the current Product OS status"
```

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

The helper script only creates and validates structure. The `loop-product-init` skill is responsible for repo discovery, user discussion, and approved product content updates.

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
  intake_issue_limit: 10
  notify_mentions:
    - your-github-username
```

See [references/repo-policy.md](references/repo-policy.md) for what each key does and its default.

## Running on a Schedule

The skills are stages of a Product OS plus label-driven state machine, so they can run as independent scheduled jobs. `.product/` stores product context, while GitHub Issue labels are the shared execution state.

Claude Code example:

```cron
# Product review (daily)
0 9 * * *      cd /path/to/repo && claude -p "Review the current Product OS status"
# Draft feature specs while roadmap has needs-spec items (daily)
15 9 * * *     cd /path/to/repo && claude -p "Draft the next Product OS feature spec"
# Split approved specs into work items / prepared issues (hourly)
0 * * * *      cd /path/to/repo && claude -p "Split the approved feature into work items"
# Generate quality/safety issues from the codebase (nightly is plenty)
0 3 * * *     cd /path/to/repo && claude -p "Scan this repo for quality and security issues"
# Prepare new issues
*/15 * * * *  cd /path/to/repo && claude -p "Triage open loop engineering issues"
# Work ready issues (parallel-safe via worktrees + max_concurrent_runs)
*/7  * * * *  cd /path/to/repo && claude -p "Take the next ready or repairing loop engineering issue through the loop"
# Review open loop PRs
*/10 * * * *  cd /path/to/repo && claude -p "Review open loop engineering PRs"
# Watchdog: recover stale runs and clean orphaned worktrees
*/30 * * * *  cd /path/to/repo && claude -p "Recover stale loop engineering runs"
# Close completed merged work
*/45 * * * *  cd /path/to/repo && claude -p "Close completed loop engineering issues"
```

Codex example:

```cron
0 9 * * *      cd /path/to/repo && codex exec "Review the current Product OS status"
15 9 * * *     cd /path/to/repo && codex exec "Draft the next Product OS feature spec"
0 * * * *      cd /path/to/repo && codex exec "Split the approved feature into work items"
0 3 * * *      cd /path/to/repo && codex exec "Scan this repo for quality and security issues"
*/15 * * * *   cd /path/to/repo && codex exec "Triage open loop engineering issues"
*/7  * * * *   cd /path/to/repo && codex exec "Take the next ready or repairing loop engineering issue through the loop"
*/10 * * * *   cd /path/to/repo && codex exec "Review open loop engineering PRs"
*/30 * * * *   cd /path/to/repo && codex exec "Recover stale loop engineering runs"
*/45 * * * *   cd /path/to/repo && codex exec "Close completed loop engineering issues"
```

### Concurrency model

`loop-engineer-issue` runs are parallel-safe: each works in its own git worktree under `worktree_root`, so concurrent runs never share a working tree. `max_concurrent_runs` caps how many run at once. It is a **soft cap** counted from the active loop labels (`loop:claimed`, `loop:in-progress`, `loop:repairing`), enforced optimistically — it can briefly overshoot when runs start in the same instant, but per-issue claiming stays exclusive, so no two runs ever touch the same issue.

For a hard guarantee that only one run executes at a time (e.g. limited resources or shared state), keep `max_concurrent_runs: 1` and wrap the cron line in `flock`:

```cron
*/7 * * * * flock -n /tmp/loop-engineer.lock sh -c 'cd /path/to/repo && claude -p "Take the next ready or repairing loop engineering issue through the loop"'
```

`loop-recover` removes orphaned worktrees left by crashed or stale runs, which also frees their slot against the cap.
