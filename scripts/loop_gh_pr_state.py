from __future__ import annotations

import argparse
import json
import subprocess
from typing import Any


def run_gh(args: list[str]) -> dict[str, Any]:
    completed = subprocess.run(["gh", *args], check=True, capture_output=True, text=True)
    return json.loads(completed.stdout or "{}")


def ci_summary(checks: list[dict[str, Any]]) -> dict[str, Any]:
    failed = []
    pending = []
    for check in checks:
        conclusion = check.get("conclusion")
        status = check.get("status")
        name = check.get("name") or check.get("workflowName") or "unknown"
        if conclusion in {"FAILURE", "CANCELLED", "TIMED_OUT", "ACTION_REQUIRED"}:
            failed.append(name)
        elif conclusion not in {"SUCCESS", "SKIPPED"} or status in {"QUEUED", "IN_PROGRESS"}:
            pending.append(name)
    if failed:
        state = "failed"
    elif pending:
        state = "pending"
    else:
        state = "passed"
    return {"state": state, "failed": failed, "pending": pending}


def normalize_pr(raw: dict[str, Any]) -> dict[str, Any]:
    checks = raw.get("statusCheckRollup") or []
    return {
        "number": raw.get("number"),
        "title": raw.get("title"),
        "state": raw.get("state"),
        "url": raw.get("url"),
        "merge_state": raw.get("mergeStateStatus"),
        "review_decision": raw.get("reviewDecision"),
        "ci": ci_summary(checks),
    }


def get_pr(pr: str) -> dict[str, Any]:
    raw = run_gh(
        [
            "pr",
            "view",
            pr,
            "--json",
            "number,title,state,url,mergeStateStatus,reviewDecision,statusCheckRollup",
        ]
    )
    return normalize_pr(raw)


def merge_pr(pr: str, method: str) -> None:
    flag = {"merge": "--merge", "squash": "--squash", "rebase": "--rebase"}[method]
    subprocess.run(["gh", "pr", "merge", pr, flag, "--delete-branch"], check=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    get_parser = subparsers.add_parser("get")
    get_parser.add_argument("--pr", required=True)
    merge_parser = subparsers.add_parser("merge")
    merge_parser.add_argument("--pr", required=True)
    merge_parser.add_argument("--method", choices=["merge", "squash", "rebase"], default="squash")
    args = parser.parse_args()

    if args.command == "get":
        print(json.dumps(get_pr(args.pr), indent=2, sort_keys=True))
    elif args.command == "merge":
        merge_pr(args.pr, args.method)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
