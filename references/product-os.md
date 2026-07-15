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

## Planning Flow

Product planning uses three gates before engineering begins. Read `references/product-planning.md` for the full interaction and self-review rules.

1. **Brainstorm** (`loop-spec-feature`): inspect context, resolve material choices one question at a time, compare viable approaches, and confirm the design direction.
2. **Spec** (`loop-spec-feature`): write and self-review `.product/feature-specs/{feature-id}.yaml`, then wait for explicit human approval of the written artifact.
3. **Plan** (`loop-split-feature`): map file responsibilities and split the approved spec into ordered `.product/work-items/*.yaml`, then wait for separate plan approval.

Do not collapse these approvals. Choosing an approach is not approval of the written spec, and approving the spec is not approval of newly generated work items.

## Roadmap Sections

- `now`: Current product focus. Only approved or ready features in this section may move toward build.
- `next`: Likely upcoming work. Agents may draft specs, but must not implement directly.
- `later`: Lower-priority ideas. Agents may organize only.
- `icebox`: Deferred ideas. Agents may organize only.

## Feature Statuses

- `idea`: Organize only.
- `needs-discovery`: Research context and resolve material product choices through brainstorming.
- `needs-spec`: The feature is coherent enough to draft a written spec.
- `spec-draft`: Improve the written artifact and resolve its material open questions.
- `spec-review`: The self-reviewed written spec awaits human review.
- `spec-approved`: The human approved the written spec; create a work-item plan next.
- `ready-for-build`: The human approved the work-item plan; ready work items may become execution issues.
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

Only one work item should be built per agent run. A work item is one independently testable and reviewable issue-to-PR unit, not a tiny coding step. A builder should receive product brief context, the feature spec, one work item, non-goals, risk, file paths, dependencies, interfaces, traced spec criteria, definition of done, and verification commands with expected results.

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
