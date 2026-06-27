# Loop Engineering Labels

## State Labels

- `loop:ready`: Issue is actionable.
- `loop:claimed`: An agent has claimed the issue.
- `loop:in-progress`: An agent is implementing or verifying.
- `loop:blocked`: Agent cannot continue without human input.
- `loop:pr-open`: A pull request exists.
- `loop:repairing`: Agent is repairing CI or review failures.
- `loop:done`: Work is complete.

Only one state label should be active at a time, except `loop:needs-human`, which can coexist with blocked states.

## Signal Labels

- `loop:needs-human`: Human decision required.
- `run:stale`: Recovery detected stale run state.
- `agent:codex`: Codex owns or owned the current run.
- `agent:claude`: Claude owns or owned the current run.
