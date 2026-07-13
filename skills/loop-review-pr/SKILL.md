---
name: loop-review-pr
description: Use to review a PR connected to a loop engineering issue, prioritizing bugs, regressions, missing tests, and issue mismatch, and to merge approved PRs when policy allows.
---

# Loop Review PR

> Paths below use `${CLAUDE_PLUGIN_ROOT}` — this plugin's install directory. Claude Code substitutes it automatically; tools that do not (e.g. Codex) should resolve it as the plugin root, not the target repo.

Review PRs with a bug-first stance. The reviewer, not the author run, owns the merge — `loop-engineer-issue` never merges its own PR, so this skill is the only merge path for loop PRs. When the review passes and policy allows, merge here instead of leaving the PR waiting; otherwise an approved green PR has no owner and the issue sits at `loop:pr-open` indefinitely.

**Every run of this skill must end in exactly one of three terminal outcomes: merged, `loop:repairing` (the worker owes a commit), or `loop:blocked` + `loop:needs-human` (a human owes a decision).** There is no fourth outcome. A run that declines to merge but leaves the issue looking agent-actionable will simply be picked up again, re-reviewed from scratch, and produce a different verdict — that is the failure this skill is built to prevent.

## Required Setup

- Run `gh auth status`.
- Read `.loop-engineering.yml` through `${CLAUDE_PLUGIN_ROOT}/scripts/loop_repo_policy.py`. Note `auto_merge`, `merge_method`, `pr_repair_limit`, and `notify_mentions`.

## Do Not Re-Review An Unchanged Diff

Review verdicts are not deterministic. Re-running a review over the same commits does not double-check the work; it re-rolls the dice, and given enough rolls a passing diff will eventually fail on a finding that is real but not blocking. Three approvals followed by a "changes required, superseding my earlier pass" on an unchanged diff is not diligence — it is a stuck loop, and it burns tokens forever without producing a commit.

So the first thing this skill does is find out whether it has already reviewed this exact code.

1. Read PR state with `${CLAUDE_PLUGIN_ROOT}/scripts/loop_gh_pr_state.py get --pr <number>` and note `head_sha`.
2. Read the most recent `Loop review summary` comment on the PR. It records `Reviewed commit` and `Verdict`.
3. Branch on what you find:

| Last review | Head SHA | What this run does |
| --- | --- | --- |
| none | — | Review it. This is the normal path. |
| `pass` | unchanged | **Do not review again.** The diff already passed. Go straight to Merge, and if Merge is not permitted, take the escalation branch there. Never reopen a passed review on unchanged code. |
| `changes-required` | unchanged | **Do not review again.** The worker has not pushed the fix yet; this is its turn, not yours. Leave the issue at `loop:repairing` and stop. If the issue has been at `loop:repairing` across two runs with no new commit, the worker is not making progress: escalate with `loop:blocked` + `loop:needs-human` and say so plainly. |
| any | changed | Review the new commits. This is a genuine second round; count it against the repair budget below. |

A review that reverses an earlier pass on an unchanged diff is only legitimate when it has found a **correctness defect the earlier pass missed** — a bug, a regression, a security hole. Say which, and say why the earlier pass was wrong. If what you have is a style preference, a naming quibble, a "could be cleaner", or a non-blocking optimization, the earlier pass stands: put it in a follow-up issue and merge.

## Repair Budget

`pr_repair_limit` binds this skill, not just `loop-engineer-issue`. Both sides draw on the same counter, which lives in the `Repairs` line of the run comment (`pr {{ pr_repairs }}/{{ pr_repair_limit }}`).

Every `changes-required` verdict you issue costs one `pr` repair. Read the count before you issue one, and write the incremented count back. **If issuing it would exceed `pr_repair_limit`, do not issue it** — the loop has already had its rounds and is not converging. Escalate instead: `loop:blocked` + `loop:needs-human`, with a comment stating what is still unresolved after N rounds and what you would need from a human to finish.

Bouncing a PR a third time is not persistence. It is the loop failing to notice it is stuck.

## Workflow

1. Do the unchanged-diff check above. It may end the run before any review happens.
2. Confirm the PR links to a GitHub Issue with loop labels or a loop run comment.
3. Inspect the diff.
4. Check for behavior regressions, missing tests, unsafe changes, and mismatch with the issue.
5. Post a review summary using `${CLAUDE_PLUGIN_ROOT}/templates/comments/review-summary.md`. **Fill in `Reviewed commit` with the `head_sha` you read in step 1, and `Verdict` with exactly `pass` or `changes-required`.** The next run depends on both; omitting them re-opens the loop this skill exists to close.
6. Route by outcome — one of exactly three, no others:
   - **Changes required**: mark the issue `loop:repairing`, after checking the repair budget above.
   - **Human judgment required**: mark the issue `loop:blocked` and `loop:needs-human`, then notify per `notify_mentions` (see Notification below).
   - **Review passes**: proceed to Merge.

## The Gate Is The Labels, Not The Prose

**Labels are the gate. Text in an issue body is not a gate.**

An issue body that says "human review required", "Protected: schema migration", "needs sign-off before merge", or similar prose is a *triage instruction that was never applied*. Honor its intent — but honor it by routing, not by refusing.

The trap this rule exists to close: a reviewer reads that sentence, declines to auto-merge, addresses a human in the comment, and leaves the issue at `loop:pr-open` or `loop:repairing`. The human is never notified. The loop re-picks the issue. It re-reviews. Nothing converges, and **the gate can never be satisfied — because prose cannot be removed by an approval the way a label can.** The PR sits green and mergeable for hours while agents talk to each other.

So:

- If the issue carries a **protected label** (`security`, `data-loss`, `migration`, `needs-human`, or whatever `protected_labels` names): do not merge. Take the human branch — `loop:blocked` + `loop:needs-human` + notify. That is a real gate.
- If the issue carries **`loop:human-approved`**: a human has cleared it. Protected labels and prose gates alike are satisfied; merge when the rest of the Merge conditions hold. This is the only thing that lifts a gate.
- If the issue body contains **prose demanding human review but no protected label**: do not silently refuse, and do not merge on the assumption the prose is stale. **Take the human branch once** — `loop:blocked` + `loop:needs-human`, notify, and say exactly what you need: *"the issue body asks for human review of X; add `loop:human-approved` (or a protected label, if it should block) and I will proceed."* Then stop. Do not review it again until a label changes.

A human satisfies any of these by adding `loop:human-approved` (and removing the protected label if the work is genuinely cleared). Both are machine-readable, both are auditable, and both survive the next run — which is the whole point.

## Merge

Merge only when all of these hold:

- The review passed with no required changes — either in this run, or in a prior run whose `Reviewed commit` matches the current `head_sha`.
- Policy `auto_merge` is true.
- CI state from `loop_gh_pr_state.py get` is `passed` — not `pending`. Never merge on pending checks.
- The linked issue carries no protected label, **or** carries `loop:human-approved`.

If every condition holds except `auto_merge`, or a protected label is present without `loop:human-approved`, that is the **human branch** — `loop:blocked` + `loop:needs-human` + notify. It is not a silent no-op.

Then:

1. Re-read PR state immediately before merging. If the PR is already merged (for example by another reviewer run or a human), skip the merge and treat the outcome as success — this race is expected and harmless.
2. If the PR is behind its base branch (merge state `BEHIND`), run `gh pr update-branch <number>` and stop here. Do not merge on checks that ran against a stale base; the refreshed CI is picked up by the next review pass. (The rebase changes `head_sha`, so the next run correctly reviews the updated diff rather than skipping it.)
3. Merge with `${CLAUDE_PLUGIN_ROOT}/scripts/loop_gh_pr_state.py merge --pr <number> --method <merge_method>`.
4. If the merge command fails because the PR was merged concurrently, treat it as success. If it fails because branch protection requires approvals the agent cannot give (a PR author account cannot approve its own PR), mark the issue `loop:blocked` plus `loop:needs-human`, state that a human approval is required, and notify per `notify_mentions`.
5. After a successful merge, leave the issue labels as they are — `loop-close` owns final summary, label cleanup, and closing.

### Sibling PRs that conflict only with each other

Before merging, check whether another open loop PR touches the same generated or append-only artifacts — migration journals and schema snapshots, lockfiles, generated clients, changelogs. Two such PRs can each report `CLEAN` against the base branch while conflicting squarely with each other, because `mergeStateStatus` is computed pairwise against the base and never against a sibling.

Merging both in sequence then produces a silent corruption rather than a conflict: the second merge appends alongside the first instead of on top of it, and the artifact no longer reflects the schema. `git merge-tree` against the sibling's head will show it.

When you find a pair like this, the merge order is not a preference — it decides which PR has to rebase, and only one of them *can*:

- **Merge the hand-authored artifact first.** It cannot be regenerated by a command, so it must keep the identifier it already has.
- **Merge the generated artifact second**, and require it to rebase and re-run its generator rather than hand-editing the file. Renaming a generated artifact by hand is the corruption: a schema snapshot, for instance, is a full snapshot of the state it was taken from, so a renamed one silently omits the change that landed before it.

Say the required order in the review comment, so the other run does not race you into the wrong sequence.

## Notification

When this skill marks an issue `loop:blocked` + `loop:needs-human` and policy `notify_mentions` is non-empty, @mention every listed username in the blocking comment and assign the first one with `gh issue edit <number> --add-assignee <username>`, so GitHub's native notifications reach a human.
