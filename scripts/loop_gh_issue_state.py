from __future__ import annotations

import argparse
import json
import subprocess
from typing import Any, Callable


def _subprocess_runner(command: list[str]) -> str:
    completed = subprocess.run(command, check=True, capture_output=True, text=True)
    return completed.stdout


def run_gh(args: list[str], runner: Callable[[list[str]], str] = _subprocess_runner) -> dict[str, Any]:
    output = runner(["gh", *args])
    return json.loads(output or "{}")


def normalize_issue(raw: dict[str, Any]) -> dict[str, Any]:
    labels = raw.get("labels", [])
    normalized_labels = [item["name"] if isinstance(item, dict) else str(item) for item in labels]
    return {
        "number": raw.get("number"),
        "title": raw.get("title"),
        "state": raw.get("state"),
        "url": raw.get("url"),
        "labels": normalized_labels,
    }


def get_issue(issue: str) -> dict[str, Any]:
    raw = run_gh(
        [
            "issue",
            "view",
            issue,
            "--json",
            "number,title,state,url,labels,assignees,comments",
        ]
    )
    return normalize_issue(raw) | {
        "assignees": raw.get("assignees", []),
        "comments": raw.get("comments", []),
    }


def add_labels(issue: str, labels: list[str]) -> None:
    if labels:
        subprocess.run(["gh", "issue", "edit", issue, "--add-label", ",".join(labels)], check=True)


def remove_labels(issue: str, labels: list[str]) -> None:
    if labels:
        subprocess.run(["gh", "issue", "edit", issue, "--remove-label", ",".join(labels)], check=True)


def close_issue(issue: str, comment: str | None = None) -> None:
    command = ["gh", "issue", "close", issue]
    if comment:
        command.extend(["--comment", comment])
    subprocess.run(command, check=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    get_parser = subparsers.add_parser("get")
    get_parser.add_argument("--issue", required=True)
    add_parser = subparsers.add_parser("add-labels")
    add_parser.add_argument("--issue", required=True)
    add_parser.add_argument("--labels", required=True)
    remove_parser = subparsers.add_parser("remove-labels")
    remove_parser.add_argument("--issue", required=True)
    remove_parser.add_argument("--labels", required=True)
    close_parser = subparsers.add_parser("close")
    close_parser.add_argument("--issue", required=True)
    close_parser.add_argument("--comment")
    args = parser.parse_args()

    if args.command == "get":
        print(json.dumps(get_issue(args.issue), indent=2, sort_keys=True))
    elif args.command == "add-labels":
        add_labels(args.issue, json.loads(args.labels))
    elif args.command == "remove-labels":
        remove_labels(args.issue, json.loads(args.labels))
    elif args.command == "close":
        close_issue(args.issue, args.comment)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
