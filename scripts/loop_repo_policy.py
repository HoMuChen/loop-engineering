from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml

DEFAULT_POLICY: dict[str, Any] = {
    "default_agent": "codex",
    "branch_prefix": "loop/",
    "merge_method": "squash",
    "stale_after_minutes": 120,
    "required_verification": [],
    "protected_labels": ["needs-human", "security", "data-loss", "migration"],
    "auto_merge": False,
    "auto_close": True,
    "local_repair_limit": 3,
    "pr_repair_limit": 2,
}


def load_policy(path: Path = Path(".loop-engineering.yml")) -> dict[str, Any]:
    policy = dict(DEFAULT_POLICY)
    if not path.exists():
        return policy

    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    configured = raw.get("loop_engineering", {})
    if not isinstance(configured, dict):
        raise ValueError("loop_engineering must be a mapping")

    for key in DEFAULT_POLICY:
        if key in configured:
            policy[key] = configured[key]

    if policy["merge_method"] not in {"merge", "squash", "rebase"}:
        raise ValueError("merge_method must be merge, squash, or rebase")
    if not isinstance(policy["required_verification"], list):
        raise ValueError("required_verification must be a list")
    if not isinstance(policy["protected_labels"], list):
        raise ValueError("protected_labels must be a list")
    return policy


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", default=".loop-engineering.yml")
    args = parser.parse_args()
    print(json.dumps(load_policy(Path(args.path)), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
