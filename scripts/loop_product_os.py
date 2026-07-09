from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

PRODUCT_DIR = ".product"
PRODUCT_OS_VERSION = 1

REQUIRED_DIRS = [
    "feature-specs",
    "work-items",
    "decisions",
    "feedback",
    "release-notes",
]

REQUIRED_FILES = [
    "product-os.yaml",
    "product-brief.md",
    "roadmap.yaml",
    "metrics.md",
]

FEATURE_STATUSES = {
    "idea",
    "needs-discovery",
    "needs-spec",
    "spec-draft",
    "spec-review",
    "spec-approved",
    "ready-for-build",
    "in-progress",
    "blocked",
    "in-review",
    "released",
    "measuring",
    "done",
    "deprecated",
}

WORK_ITEM_STATUSES = {
    "draft",
    "needs-review",
    "ready-for-build",
    "in-progress",
    "blocked",
    "in-review",
    "done",
}


def _now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _write_if_missing(path: Path, content: str) -> bool:
    if path.exists():
        return False
    path.write_text(content, encoding="utf-8")
    return True


def _load_yaml(path: Path) -> Any:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _product_root(root: Path) -> Path:
    return root / PRODUCT_DIR


def default_product_os(owner: str | None = None) -> dict[str, Any]:
    return {
        "product_os": {
            "version": PRODUCT_OS_VERSION,
            "schema": "product-os/v1",
            "initialized_at": _now_iso(),
            "owner": owner or "TODO",
            "execution_backend": "github_issues",
        },
        "autonomy": {
            "build_source": "github_issues",
            "product_source": ".product",
            "allowed_feature_statuses_for_build": ["ready-for-build"],
            "requires_approval_for": [
                "roadmap_priority_change",
                "roadmap_now_next_later_change",
                "mvp_scope_change",
                "high_risk_feature",
                "permission_change",
                "billing_change",
                "database_migration",
                "production_deploy",
            ],
            "never_allowed": [
                "delete_production_data",
                "rotate_secrets_without_approval",
                "modify_autonomy_policy_without_approval",
            ],
        },
    }


def default_product_brief() -> str:
    return """# Product Brief

## Product

TODO: Describe what this product is.

## Core Value

TODO: Describe the primary customer value.

## Primary Users

- TODO

## Current Stage

MVP.

## MVP Scope

- TODO

## Non-Goals

- TODO

## Differentiation

TODO: Describe why this product should exist.
"""


def default_roadmap() -> dict[str, Any]:
    return {
        "roadmap": {
            "now": [],
            "next": [],
            "later": [],
            "icebox": [],
        }
    }


def default_metrics() -> str:
    return """# Metrics

Track product signals that should influence roadmap suggestions.

## North Star

TODO

## Supporting Metrics

- TODO
"""


def init_product_os(root: Path = Path("."), owner: str | None = None) -> dict[str, Any]:
    root = root.resolve()
    root.mkdir(parents=True, exist_ok=True)
    product_root = _product_root(root)
    product_root.mkdir(exist_ok=True)

    created: list[str] = []
    preserved: list[str] = []

    for dirname in REQUIRED_DIRS:
        path = product_root / dirname
        if path.exists():
            preserved.append(str(path.relative_to(root)))
        else:
            path.mkdir(parents=True)
            created.append(str(path.relative_to(root)))
        keep = path / ".gitkeep"
        if _write_if_missing(keep, ""):
            created.append(str(keep.relative_to(root)))

    files = {
        "product-os.yaml": yaml.safe_dump(default_product_os(owner), sort_keys=False, allow_unicode=True),
        "product-brief.md": default_product_brief(),
        "roadmap.yaml": yaml.safe_dump(default_roadmap(), sort_keys=False, allow_unicode=True),
        "metrics.md": default_metrics(),
    }

    for filename, content in files.items():
        path = product_root / filename
        if _write_if_missing(path, content):
            created.append(str(path.relative_to(root)))
        else:
            preserved.append(str(path.relative_to(root)))

    validation = validate_product_os(root)
    return {
        "product_dir": str(product_root),
        "created": created,
        "preserved": preserved,
        "validation": validation,
    }


def validate_product_os(root: Path = Path(".")) -> dict[str, Any]:
    root = root.resolve()
    product_root = _product_root(root)
    errors: list[str] = []
    warnings: list[str] = []

    if not product_root.exists():
        return {
            "ok": False,
            "errors": [".product directory is missing"],
            "warnings": [],
        }

    for dirname in REQUIRED_DIRS:
        if not (product_root / dirname).is_dir():
            errors.append(f".product/{dirname} directory is missing")

    for filename in REQUIRED_FILES:
        if not (product_root / filename).is_file():
            errors.append(f".product/{filename} file is missing")

    product_os_path = product_root / "product-os.yaml"
    if product_os_path.exists():
        try:
            product_os = _load_yaml(product_os_path)
        except yaml.YAMLError as exc:
            errors.append(f".product/product-os.yaml is invalid YAML: {exc}")
        else:
            version = product_os.get("product_os", {}).get("version")
            if version != PRODUCT_OS_VERSION:
                warnings.append(f".product/product-os.yaml version is {version}; expected {PRODUCT_OS_VERSION}")
            backend = product_os.get("product_os", {}).get("execution_backend")
            if backend != "github_issues":
                warnings.append("execution_backend should be github_issues for loop-engineering v1")

    roadmap_path = product_root / "roadmap.yaml"
    if roadmap_path.exists():
        try:
            roadmap = _load_yaml(roadmap_path)
        except yaml.YAMLError as exc:
            errors.append(f".product/roadmap.yaml is invalid YAML: {exc}")
        else:
            sections = roadmap.get("roadmap")
            if not isinstance(sections, dict):
                errors.append(".product/roadmap.yaml must contain a roadmap mapping")
            else:
                for section in ("now", "next", "later", "icebox"):
                    if section not in sections:
                        warnings.append(f"roadmap.{section} is missing")
                    elif not isinstance(sections[section], list):
                        errors.append(f"roadmap.{section} must be a list")
                for section, items in sections.items():
                    if not isinstance(items, list):
                        continue
                    for item in items:
                        if not isinstance(item, dict):
                            errors.append(f"roadmap.{section} contains a non-mapping item")
                            continue
                        item_id = item.get("id", "<missing id>")
                        status = item.get("status")
                        if status and status not in FEATURE_STATUSES:
                            warnings.append(f"roadmap item {item_id} has unknown status {status}")

    for path in sorted((product_root / "feature-specs").glob("*.yaml")):
        try:
            spec = _load_yaml(path)
        except yaml.YAMLError as exc:
            errors.append(f"{path.relative_to(root)} is invalid YAML: {exc}")
            continue
        status = spec.get("status")
        if status and status not in FEATURE_STATUSES:
            warnings.append(f"{path.relative_to(root)} has unknown status {status}")
        for field in ("id", "title", "status", "problem", "scope", "acceptance_criteria"):
            if field not in spec:
                warnings.append(f"{path.relative_to(root)} is missing {field}")

    for path in sorted((product_root / "work-items").glob("*.yaml")):
        try:
            item = _load_yaml(path)
        except yaml.YAMLError as exc:
            errors.append(f"{path.relative_to(root)} is invalid YAML: {exc}")
            continue
        status = item.get("status")
        if status and status not in WORK_ITEM_STATUSES:
            warnings.append(f"{path.relative_to(root)} has unknown status {status}")
        for field in ("id", "feature_id", "title", "status", "definition_of_done", "validation"):
            if field not in item:
                warnings.append(f"{path.relative_to(root)} is missing {field}")

    return {
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
    }


def update_work_item(
    root: Path = Path("."),
    work_item_id: str = "",
    status: str | None = None,
    issue: int | None = None,
    pr: int | None = None,
) -> dict[str, Any]:
    """Write execution facts back into a work item so `.product/` stops drifting.

    Sets the work item status and appends issue / PR links without duplicates.
    Used by loop-close after an issue's PR merges.
    """
    root = root.resolve()
    path = _product_root(root) / "work-items" / f"{work_item_id}.yaml"
    if not path.exists():
        return {"ok": False, "error": f"work item not found: {path}"}
    if status is not None and status not in WORK_ITEM_STATUSES:
        return {"ok": False, "error": f"unknown work item status: {status}"}

    item = _load_yaml(path)
    if not isinstance(item, dict):
        return {"ok": False, "error": f"work item is not a mapping: {path}"}

    if status is not None:
        item["status"] = status

    links = item.get("links")
    if not isinstance(links, dict):
        links = {}
    issues = list(links.get("issues") or [])
    prs = list(links.get("prs") or [])
    if issue is not None and issue not in issues:
        issues.append(issue)
    if pr is not None and pr not in prs:
        prs.append(pr)
    links["issues"] = issues
    links["prs"] = prs
    item["links"] = links

    path.write_text(yaml.safe_dump(item, sort_keys=False, allow_unicode=True), encoding="utf-8")
    return {"ok": True, "work_item": str(path.relative_to(root)), "status": item.get("status"), "links": links}


def product_status(root: Path = Path(".")) -> dict[str, Any]:
    root = root.resolve()
    product_root = _product_root(root)
    validation = validate_product_os(root)
    feature_counts: Counter[str] = Counter()
    work_item_counts: Counter[str] = Counter()
    roadmap_counts: Counter[str] = Counter()

    roadmap_path = product_root / "roadmap.yaml"
    if roadmap_path.exists():
        try:
            roadmap = _load_yaml(roadmap_path)
        except yaml.YAMLError:
            roadmap = {}
        sections = roadmap.get("roadmap", {})
        if isinstance(sections, dict):
            for section, items in sections.items():
                if isinstance(items, list):
                    roadmap_counts[section] += len(items)

    feature_dir = product_root / "feature-specs"
    if feature_dir.exists():
        for path in feature_dir.glob("*.yaml"):
            try:
                feature = _load_yaml(path)
            except yaml.YAMLError:
                feature_counts["invalid"] += 1
                continue
            feature_counts[feature.get("status", "missing-status")] += 1

    work_item_dir = product_root / "work-items"
    if work_item_dir.exists():
        for path in work_item_dir.glob("*.yaml"):
            try:
                item = _load_yaml(path)
            except yaml.YAMLError:
                work_item_counts["invalid"] += 1
                continue
            work_item_counts[item.get("status", "missing-status")] += 1

    return {
        "validation": validation,
        "roadmap": dict(sorted(roadmap_counts.items())),
        "feature_specs": dict(sorted(feature_counts.items())),
        "work_items": dict(sorted(work_item_counts.items())),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init")
    init_parser.add_argument("--root", default=".")
    init_parser.add_argument("--owner")

    validate_parser = subparsers.add_parser("validate")
    validate_parser.add_argument("--root", default=".")
    validate_parser.add_argument("--json", action="store_true")

    status_parser = subparsers.add_parser("status")
    status_parser.add_argument("--root", default=".")
    status_parser.add_argument("--json", action="store_true")

    work_item_parser = subparsers.add_parser("work-item")
    work_item_parser.add_argument("--root", default=".")
    work_item_parser.add_argument("--id", required=True)
    work_item_parser.add_argument("--status")
    work_item_parser.add_argument("--issue", type=int)
    work_item_parser.add_argument("--pr", type=int)

    args = parser.parse_args()

    if args.command == "init":
        result = init_product_os(Path(args.root), owner=args.owner)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0 if result["validation"]["ok"] else 1

    if args.command == "validate":
        result = validate_product_os(Path(args.root))
        if args.json:
            print(json.dumps(result, indent=2, sort_keys=True))
        else:
            print("ok" if result["ok"] else "invalid")
            for error in result["errors"]:
                print(f"error: {error}")
            for warning in result["warnings"]:
                print(f"warning: {warning}")
        return 0 if result["ok"] else 1

    if args.command == "status":
        result = product_status(Path(args.root))
        if args.json:
            print(json.dumps(result, indent=2, sort_keys=True))
        else:
            print(json.dumps(result, indent=2, sort_keys=True))
        return 0 if result["validation"]["ok"] else 1

    if args.command == "work-item":
        result = update_work_item(
            Path(args.root),
            work_item_id=args.id,
            status=args.status,
            issue=args.issue,
            pr=args.pr,
        )
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0 if result["ok"] else 1

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
