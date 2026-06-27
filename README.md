# Loop Engineering

Loop Engineering is a portable plugin for agentic software work managed through GitHub Issues.

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

## Local Verification

```bash
python -m pytest -q
python -m json.tool .codex-plugin/plugin.json
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
