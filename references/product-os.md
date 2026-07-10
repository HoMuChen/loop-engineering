# Product OS

Product OS adds a product-management layer above the GitHub Issue engineering loop.

`.product/` is the product source of truth. GitHub Issues remain the execution source of truth for implementation. Do not let agents implement directly from roadmap entries or feature specs; turn approved work into scoped GitHub Issues before using `loop-engineer-issue`.

## Directory

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

## Initialization

Initialize Product OS in two phases:

1. Run the deterministic init helper to create the safe `.product/` skeleton without overwriting existing files.
2. Inspect the codebase and existing project materials, then discuss a proposed product brief and roadmap with the user before writing product strategy.

The init helper should not infer strategy by itself. The agent using `loop-product-init` should cite repo evidence, separate assumptions, ask clarifying questions, and write non-placeholder product content only after explicit approval.

## Authority Boundary

Human owners decide why, what, priority, scope, tradeoffs, and approval for high-risk work.

Agents may draft specs, split approved specs into work items, update implementation status from facts, produce release notes, summarize feedback, and suggest roadmap changes.

Agents must not independently move features into Now, raise priority, expand MVP scope, approve high-risk features, change billing or permission direction, or deploy to production.

Use `loop-roadmap-update` for explicit user-approved roadmap edits. Vague requests such as "what should we do next?" should produce recommendations rather than direct file edits.

## Roadmap Sections

- `now`: Current product focus. Only approved or ready features in this section may move toward build.
- `next`: Likely upcoming work. Agents may draft specs, but must not implement directly.
- `later`: Lower-priority ideas. Agents may organize only.
- `icebox`: Deferred ideas. Agents may organize only.

## Feature Statuses

- `idea`: Organize only.
- `needs-discovery`: Research and collect questions.
- `needs-spec`: Draft a feature spec.
- `spec-draft`: Improve the draft and list open questions.
- `spec-review`: Wait for human review.
- `spec-approved`: Split into work items.
- `ready-for-build`: May create execution issues for ready work items.
- `in-progress`: Track active issue or PR progress.
- `blocked`: Explain blocker; do not force implementation.
- `in-review`: Wait for review.
- `released`: Produce release notes.
- `measuring`: Summarize feedback and metrics.
- `done`: Do not proactively change except bug or approved follow-up.
- `deprecated`: Do not continue development.

## Work Item Statuses

`.product/` is the source of truth for intent; GitHub Issues are the source of truth for execution. Work item YAML therefore stores only intent states and the terminal state:

- `draft`: Proposed task.
- `needs-review`: Waiting for human approval.
- `ready-for-build`: May become a `loop:ready` GitHub Issue.
- `done`: Completed and released or merged. Written back by `loop-close` (terminal, so it cannot drift).

The execution states are **derived, never stored**. Read them from the linked issue (`links.issues`) at report time — `loop:claimed`/`loop:in-progress`/`loop:repairing` labels mean in-progress, `loop:blocked` means blocked, `loop:pr-open` means in-review. `loop_product_os.py` warns on stored derived statuses and refuses to write them:

- `in-progress`: Linked issue or PR is active.
- `blocked`: Requires human input or external state.
- `in-review`: PR is open or review is pending.

Deriving instead of mirroring is what keeps the two sides from needing synchronization: a stored copy of live execution state is stale the moment it is written.

## Linking Work Items to Issues

The link must be bidirectional from the moment an issue is created: the issue body carries the work item id (`wi-...`), and the work item's `links.issues` carries the issue number (`loop-split-feature` records it right after `gh issue create` via `loop_product_os.py work-item --id {work-item-id} --issue {number}`). Without the stored link, derived status cannot be computed and `loop-close`'s write-back depends on fragile text matching.

## Committing .product Changes

Skills that write `.product/` (`loop-product-init`, `loop-roadmap-update`, `loop-spec-feature`, `loop-split-feature`, `loop-close`, `loop-recover` reconciliation) must commit what they wrote, or cron-driven runs leave a permanently dirty tree and write-backs can be lost:

1. Update the local default branch first (`git pull --rebase`) — loop merges happen on the remote, so the local default branch is often behind.
2. Stage only the product paths: `git add .product`.
3. Commit with a concise message describing the product state change, then push. If the push is rejected, `git pull --rebase` and push again.

## Build Rule

Only one work item should be built per agent run. A builder should receive product brief context, the feature spec, one work item, non-goals, risk, definition of done, and verification commands.

## Milestones

GitHub Milestones map to Product OS features. One milestone represents one feature, and the milestone title is the feature id. This gives every feature a first-class grouping of its work-item issues plus free completion progress from GitHub.

- Labels remain the workflow state machine. Milestones express feature membership and completion, not state. The two are orthogonal and must not be conflated.
- `loop-split-feature` ensures a milestone named after the feature id exists, then attaches every generated work-item issue to it.
- `loop-product-review` reads milestone progress (open vs closed issues) as a fact instead of recomputing feature completion by hand.
- `loop-close` checks the milestone after the last issue closes. A milestone with all issues closed is a signal that its feature is a candidate to move to `released` and to produce release notes.
- Advancing a roadmap feature is a human-owned decision (see Authority Boundary). Agents recommend based on milestone completion; they do not auto-advance roadmap status.

Use `${CLAUDE_PLUGIN_ROOT}/scripts/loop_gh_milestone.py` (the plugin's install directory; see the skill files' path note):

- `ensure --title {feature-id} [--description ...]`: find or create a milestone.
- `get --title {feature-id}`: read one milestone's completion progress.
- `list [--state all|open|closed]`: list milestones with progress.
