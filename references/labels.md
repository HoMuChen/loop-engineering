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

## Classification Labels

Applied by `loop-triage` and `loop-intake-quality`, orthogonal to state:

- `kind:*`: `kind:bug`, `kind:feature`, `kind:refactor`, `kind:docs`, `kind:chore`.
- Topical/area labels as the repository defines them.
- Protected labels (e.g. `security`) mark findings that must go to a human; `loop-engineer-issue` refuses to auto-fix them.

## Protected vs Non-Blocking Risk Labels

Protected labels are stop signals. Do not combine them with `loop:ready`.

- Use protected labels such as `security`, `data-loss`, `migration`, or
  `needs-human` only when the issue should not be implemented by the loop before
  human intervention.
- Use `loop:blocked` plus `loop:needs-human` for issues carrying protected
  labels.
- For approved work that merely touches a sensitive area but is intended to be
  implemented by the loop, document the risk in the issue body and use
  repository-defined non-blocking labels such as `area:security`,
  `area:permissions`, or `risk:medium` instead of protected labels.
