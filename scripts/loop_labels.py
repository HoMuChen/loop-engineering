from __future__ import annotations

import argparse
import json
import subprocess
from typing import Callable

STATE_LABELS = {
    "loop:ready",
    "loop:claimed",
    "loop:in-progress",
    "loop:blocked",
    "loop:pr-open",
    "loop:repairing",
    "loop:done",
}

TRANSIENT_LABELS = {
    "loop:ready",
    "loop:claimed",
    "loop:in-progress",
    "loop:blocked",
    "loop:pr-open",
    "loop:repairing",
    "run:stale",
}

# Canonical set of labels the loop relies on. `ensure` upserts these so a fresh
# repository does not fail the first `gh issue edit --add-label` call.
LABEL_CATALOG: list[dict[str, str]] = [
    {"name": "loop:ready", "color": "0e8a16", "description": "Issue is actionable by an agent."},
    {"name": "loop:claimed", "color": "1d76db", "description": "An agent has claimed the issue."},
    {"name": "loop:in-progress", "color": "0052cc", "description": "An agent is implementing or verifying."},
    {"name": "loop:pr-open", "color": "5319e7", "description": "A pull request exists for this issue."},
    {"name": "loop:repairing", "color": "d93f0b", "description": "An agent is repairing CI or review failures."},
    {"name": "loop:blocked", "color": "b60205", "description": "Agent cannot continue without human input."},
    {"name": "loop:done", "color": "0e4429", "description": "Work is complete."},
    {"name": "loop:needs-human", "color": "fbca04", "description": "Human decision required."},
    # Signal, not state: coexists with any state label and is deliberately NOT
    # transient, so it survives `loop-close` as a durable record that a human
    # actually looked. It is the only way to satisfy a gate — prose in an issue
    # body cannot be lifted, a label can.
    {"name": "loop:human-approved", "color": "0e8a16", "description": "A human reviewed and cleared this; agents may proceed and merge."},
    {"name": "run:stale", "color": "e99695", "description": "Recovery detected a stale run."},
    {"name": "agent:claude", "color": "d4c5f9", "description": "Claude owns or owned the current run."},
    {"name": "agent:codex", "color": "c5def5", "description": "Codex owns or owned the current run."},
    {"name": "kind:bug", "color": "d73a4a", "description": "A defect or incorrect behavior."},
    {"name": "kind:feature", "color": "a2eeef", "description": "New functionality."},
    {"name": "kind:refactor", "color": "fbca04", "description": "Internal change without behavior change."},
    {"name": "kind:docs", "color": "0075ca", "description": "Documentation only."},
    {"name": "kind:chore", "color": "cfd3d7", "description": "Maintenance or tooling."},
    {"name": "security", "color": "b60205", "description": "Protected: security-sensitive; route to a human."},
    {"name": "data-loss", "color": "b60205", "description": "Protected: risk of data loss; route to a human."},
    {"name": "migration", "color": "d93f0b", "description": "Protected: destructive or schema migration; route to a human."},
    {"name": "needs-human", "color": "fbca04", "description": "Protected: requires human handling before the loop runs."},
]

Runner = Callable[[list[str]], None]


def _subprocess_runner(command: list[str]) -> None:
    subprocess.run(command, check=True)


def next_status_labels(labels: list[str], status: str) -> list[str]:
    if status not in STATE_LABELS:
        raise ValueError(f"Unknown loop status label: {status}")
    kept = [label for label in labels if label not in STATE_LABELS]
    return kept + [status]


def clean_transient_labels(labels: list[str]) -> list[str]:
    kept = [label for label in labels if label not in TRANSIENT_LABELS and label != "loop:done"]
    return kept + ["loop:done"]


def ensure_labels(runner: Runner = _subprocess_runner) -> list[str]:
    ensured: list[str] = []
    for label in LABEL_CATALOG:
        runner(
            [
                "gh",
                "label",
                "create",
                label["name"],
                "--color",
                label["color"],
                "--description",
                label["description"],
                "--force",
            ]
        )
        ensured.append(label["name"])
    return ensured


def main() -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    set_status_parser = subparsers.add_parser("set-status")
    set_status_parser.add_argument("--labels", required=True, help="JSON array of label names")
    set_status_parser.add_argument("--status", required=True)

    clean_parser = subparsers.add_parser("clean-transient")
    clean_parser.add_argument("--labels", required=True, help="JSON array of label names")

    subparsers.add_parser("catalog")
    subparsers.add_parser("ensure")

    args = parser.parse_args()

    if args.command == "set-status":
        result = next_status_labels(json.loads(args.labels), args.status)
        print(json.dumps({"labels": result}, indent=2, sort_keys=True))
        return 0

    if args.command == "clean-transient":
        result = clean_transient_labels(json.loads(args.labels))
        print(json.dumps({"labels": result}, indent=2, sort_keys=True))
        return 0

    if args.command == "catalog":
        print(json.dumps(LABEL_CATALOG, indent=2, sort_keys=True))
        return 0

    if args.command == "ensure":
        ensured = ensure_labels()
        print(json.dumps({"ensured": ensured}, indent=2, sort_keys=True))
        return 0

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
