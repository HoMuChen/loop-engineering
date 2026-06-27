from __future__ import annotations

import argparse
import json

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


def next_status_labels(labels: list[str], status: str) -> list[str]:
    if status not in STATE_LABELS:
        raise ValueError(f"Unknown loop status label: {status}")
    kept = [label for label in labels if label not in STATE_LABELS]
    return kept + [status]


def clean_transient_labels(labels: list[str]) -> list[str]:
    kept = [label for label in labels if label not in TRANSIENT_LABELS and label != "loop:done"]
    return kept + ["loop:done"]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["set-status", "clean-transient"])
    parser.add_argument("--labels", required=True, help="JSON array of label names")
    parser.add_argument("--status")
    args = parser.parse_args()
    labels = json.loads(args.labels)

    if args.command == "set-status":
        if not args.status:
            raise SystemExit("--status is required")
        result = next_status_labels(labels, args.status)
    else:
        result = clean_transient_labels(labels)

    print(json.dumps({"labels": result}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
