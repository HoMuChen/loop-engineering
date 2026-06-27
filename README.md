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

## Primary Skill

Use `loop-engineer-issue` to take one issue through the full loop: intake, claim, plan, implement, verify, PR, repair, merge, close.
