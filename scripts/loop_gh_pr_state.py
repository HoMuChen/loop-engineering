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
        # The commit the diff currently resolves to. `loop-review-pr` records this
        # in its review comment and compares it on the next run: an unchanged head
        # means the diff under review is byte-for-byte the one already reviewed, so
        # re-reviewing it can only produce a different verdict by chance, never by
        # evidence. Without this field the reviewer has no way to know it is looking
        # at the same code twice.
        "head_sha": raw.get("headRefOid"),
        "merge_state": raw.get("mergeStateStatus"),
        "review_decision": raw.get("reviewDecision"),
        "ci": ci_summary(checks),
    }


# `headRefOid` is load-bearing, not informational: it is what lets `loop-review-pr`
# recognize a diff it has already reviewed. Removing it from this list would not fail
# anything loudly — the reviewer would just quietly start re-reviewing unchanged code.
GET_PR_JSON_FIELDS = (
    "number,title,state,url,headRefOid,mergeStateStatus,reviewDecision,statusCheckRollup"
)


def get_pr(pr: str) -> dict[str, Any]:
    raw = run_gh(["pr", "view", pr, "--json", GET_PR_JSON_FIELDS])
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
