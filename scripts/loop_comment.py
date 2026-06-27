from __future__ import annotations

import argparse
import json
import re
from typing import Any

START = "<!-- loop-engineering:run v1 -->"
END = "<!-- /loop-engineering:run -->"


def _extract_block(body: str) -> str:
    pattern = re.compile(re.escape(START) + r"(.*?)" + re.escape(END), re.DOTALL)
    matches = pattern.findall(body)
    if not matches:
        raise ValueError("No loop-engineering run comment found")
    return matches[-1].strip()


def _parse_list_section(block: str, heading: str) -> list[str]:
    pattern = re.compile(rf"{re.escape(heading)}:\n(.*?)(?:\n\n[A-Z][A-Za-z ]+:\n|\Z)", re.DOTALL)
    match = pattern.search(block + "\n")
    if not match:
        return []
    lines = []
    for raw_line in match.group(1).splitlines():
        line = raw_line.strip()
        if line.startswith("- "):
            lines.append(line[2:].strip())
    return lines


def parse_run_comment(body: str) -> dict[str, Any]:
    block = _extract_block(body)
    fields = {}
    names = {
        "Run": "run_id",
        "Agent": "agent",
        "Status": "status",
        "Branch": "branch",
        "PR": "pr",
        "Started": "started",
        "Updated": "updated",
    }
    for label, key in names.items():
        match = re.search(rf"^{re.escape(label)}:\s*(.*)$", block, re.MULTILINE)
        if not match:
            raise ValueError(f"Missing required field: {label}")
        fields[key] = match.group(1).strip()
    fields["plan"] = _parse_list_section(block, "Plan")
    fields["verification"] = _parse_list_section(block, "Verification")
    fields["blockers"] = _parse_list_section(block, "Blockers")
    return fields


def _render_items(items: list[str]) -> str:
    if not items:
        return "- none"
    return "\n".join(f"- {item}" for item in items)


def render_run_comment(data: dict[str, Any]) -> str:
    return f"""{START}
Run: {data["run_id"]}
Agent: {data["agent"]}
Status: {data["status"]}
Branch: {data["branch"]}
PR: {data["pr"]}
Started: {data["started"]}
Updated: {data["updated"]}

Plan:
{_render_items(data.get("plan", []))}

Verification:
{_render_items(data.get("verification", []))}

Blockers:
{_render_items(data.get("blockers", []))}
{END}
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    parse_parser = subparsers.add_parser("parse")
    parse_parser.add_argument("--body-file", required=True)
    render_parser = subparsers.add_parser("render")
    render_parser.add_argument("--data", required=True)
    args = parser.parse_args()

    if args.command == "parse":
        with open(args.body_file, "r", encoding="utf-8") as handle:
            print(json.dumps(parse_run_comment(handle.read()), indent=2, sort_keys=True))
    if args.command == "render":
        print(render_run_comment(json.loads(args.data)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
