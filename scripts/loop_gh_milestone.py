from __future__ import annotations

import argparse
import json
import subprocess
from typing import Any, Callable

Runner = Callable[[list[str]], str]


def _subprocess_runner(command: list[str]) -> str:
    completed = subprocess.run(command, check=True, capture_output=True, text=True)
    return completed.stdout


def run_gh(args: list[str], runner: Runner = _subprocess_runner) -> Any:
    output = runner(["gh", *args]).strip()
    if not output:
        return None
    return json.loads(output)


def normalize_milestone(raw: dict[str, Any]) -> dict[str, Any]:
    open_issues = raw.get("open_issues", 0) or 0
    closed_issues = raw.get("closed_issues", 0) or 0
    total = open_issues + closed_issues
    closed_percent = round(closed_issues / total * 100) if total else 0
    return {
        "number": raw.get("number"),
        "title": raw.get("title"),
        "state": raw.get("state"),
        "description": raw.get("description"),
        "open_issues": open_issues,
        "closed_issues": closed_issues,
        "total_issues": total,
        "closed_percent": closed_percent,
        "complete": total > 0 and open_issues == 0,
        "url": raw.get("html_url"),
    }


def list_milestones(state: str = "all", runner: Runner = _subprocess_runner) -> list[dict[str, Any]]:
    raw = run_gh(
        [
            "api",
            "--method",
            "GET",
            "--paginate",
            "repos/{owner}/{repo}/milestones",
            "-f",
            f"state={state}",
            "-f",
            "per_page=100",
        ],
        runner=runner,
    )
    if not raw:
        return []
    return [normalize_milestone(item) for item in raw]


def find_milestone(title: str, runner: Runner = _subprocess_runner) -> dict[str, Any] | None:
    for milestone in list_milestones(state="all", runner=runner):
        if milestone["title"] == title:
            return milestone
    return None


def create_milestone(title: str, description: str | None = None, runner: Runner = _subprocess_runner) -> dict[str, Any]:
    args = [
        "api",
        "--method",
        "POST",
        "repos/{owner}/{repo}/milestones",
        "-f",
        f"title={title}",
    ]
    if description:
        args.extend(["-f", f"description={description}"])
    raw = run_gh(args, runner=runner)
    return normalize_milestone(raw or {})


def ensure_milestone(title: str, description: str | None = None, runner: Runner = _subprocess_runner) -> dict[str, Any]:
    existing = find_milestone(title, runner=runner)
    if existing is not None:
        return {"milestone": existing, "created": False}
    created = create_milestone(title, description, runner=runner)
    return {"milestone": created, "created": True}


def main() -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    ensure_parser = subparsers.add_parser("ensure")
    ensure_parser.add_argument("--title", required=True)
    ensure_parser.add_argument("--description")

    get_parser = subparsers.add_parser("get")
    get_parser.add_argument("--title", required=True)

    list_parser = subparsers.add_parser("list")
    list_parser.add_argument("--state", default="all", choices=["all", "open", "closed"])

    args = parser.parse_args()

    if args.command == "ensure":
        result = ensure_milestone(args.title, args.description)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0

    if args.command == "get":
        milestone = find_milestone(args.title)
        if milestone is None:
            print(json.dumps({"error": f"milestone not found: {args.title}"}, indent=2, sort_keys=True))
            return 1
        print(json.dumps(milestone, indent=2, sort_keys=True))
        return 0

    if args.command == "list":
        print(json.dumps(list_milestones(args.state), indent=2, sort_keys=True))
        return 0

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
