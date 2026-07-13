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
- `loop:human-approved`: A human reviewed and cleared this; agents may proceed and merge.
- `run:stale`: Recovery detected stale run state.
- `agent:codex`: Codex owns or owned the current run.
- `agent:claude`: Claude owns or owned the current run.

`loop:human-approved` is the **only** way to satisfy a gate. It coexists with any
state label, and it is deliberately not transient — `loop-close` leaves it in place,
so the record that a human actually looked survives the issue being closed.

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

## The Gate Is The Labels, Not The Prose

**A gate is a label. Prose in an issue body is not a gate.**

Issue bodies frequently end with a line like *"Protected: schema migration → human
review"* or *"touches secret handling — human review required"*. Written by a human or
by intake, it reads like a rule. It is not one: it is a triage instruction that was
never applied.

Agents must not enforce it by refusing. An agent that reads such a sentence, declines
to merge a green PR, addresses a human in a comment, and leaves the issue in an
agent-actionable state has created a trap:

- The human is never notified, because no `loop:needs-human` was set.
- The loop re-picks the issue, re-reviews the same diff, and — reviews being
  non-deterministic — eventually reverses its own earlier approval.
- **The gate can never be satisfied.** A label can be removed; a sentence cannot.
  No approval, comment, or sign-off will change what the body says, so the next run
  refuses again, forever.

The correct response to a prose gate is to **convert it or route it**:

- `loop-triage` and `loop-intake-quality` must turn a prose protection notice into an
  actual protected label at intake, so the body and the labels cannot disagree.
- An agent that meets a prose gate with no matching label escalates **once** —
  `loop:blocked` + `loop:needs-human` — and states what it needs: a protected label if
  the work should really stop, or `loop:human-approved` if it is cleared. Then it stops
  reviewing until a label changes.
- A human clears any gate by adding `loop:human-approved` (and removing the protected
  label, if the concern is genuinely resolved). Striking the sentence out of the body
  is good hygiene, but the **label** is what the loop reads.
