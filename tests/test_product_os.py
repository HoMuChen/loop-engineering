from pathlib import Path

import yaml

from scripts.loop_product_os import (
    init_product_os,
    product_status,
    update_work_item,
    validate_product_os,
)


def _write_work_item(tmp_path: Path, work_item_id: str, **fields) -> Path:
    init_product_os(tmp_path)
    path = tmp_path / ".product" / "work-items" / f"{work_item_id}.yaml"
    base = {"id": work_item_id, "feature_id": "feature-x", "title": "Task", "status": "in-progress"}
    base.update(fields)
    path.write_text(yaml.safe_dump(base, sort_keys=False), encoding="utf-8")
    return path


def test_update_work_item_sets_status_and_appends_links(tmp_path: Path):
    path = _write_work_item(tmp_path, "wi-feature-x-001")

    result = update_work_item(tmp_path, "wi-feature-x-001", status="done", issue=12, pr=34)

    assert result["ok"] is True
    written = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert written["status"] == "done"
    assert written["links"]["issues"] == [12]
    assert written["links"]["prs"] == [34]


def test_update_work_item_does_not_duplicate_links(tmp_path: Path):
    _write_work_item(tmp_path, "wi-feature-x-002", links={"issues": [7], "prs": []})

    result = update_work_item(tmp_path, "wi-feature-x-002", issue=7, pr=9)

    assert result["work_item"].endswith("wi-feature-x-002.yaml")
    written = yaml.safe_load((tmp_path / ".product" / "work-items" / "wi-feature-x-002.yaml").read_text(encoding="utf-8"))
    assert written["links"]["issues"] == [7]
    assert written["links"]["prs"] == [9]


def test_update_work_item_rejects_unknown_status(tmp_path: Path):
    _write_work_item(tmp_path, "wi-feature-x-003")

    result = update_work_item(tmp_path, "wi-feature-x-003", status="shipped")

    assert result["ok"] is False
    assert "unknown work item status" in result["error"]


def test_update_work_item_rejects_derived_status(tmp_path: Path):
    _write_work_item(tmp_path, "wi-feature-x-004", status="ready-for-build")

    result = update_work_item(tmp_path, "wi-feature-x-004", status="in-progress")

    assert result["ok"] is False
    assert "derived" in result["error"]


def test_validate_product_os_warns_on_stored_derived_status(tmp_path: Path):
    _write_work_item(
        tmp_path,
        "wi-feature-x-005",
        status="in-progress",
        definition_of_done=["x"],
        validation=["x"],
    )

    result = validate_product_os(tmp_path)

    assert result["ok"] is True
    assert any("derived" in warning for warning in result["warnings"])


def test_update_work_item_reports_missing_file(tmp_path: Path):
    init_product_os(tmp_path)

    result = update_work_item(tmp_path, "wi-does-not-exist", status="done")

    assert result["ok"] is False
    assert "work item not found" in result["error"]


def test_init_product_os_creates_required_structure(tmp_path: Path):
    result = init_product_os(tmp_path, owner="HoMu")

    assert result["validation"]["ok"] is True
    assert (tmp_path / ".product" / "product-os.yaml").is_file()
    assert (tmp_path / ".product" / "product-brief.md").is_file()
    assert (tmp_path / ".product" / "roadmap.yaml").is_file()
    assert (tmp_path / ".product" / "feature-specs").is_dir()
    assert (tmp_path / ".product" / "work-items").is_dir()

    product_os = yaml.safe_load((tmp_path / ".product" / "product-os.yaml").read_text(encoding="utf-8"))
    assert product_os["product_os"]["owner"] == "HoMu"
    assert product_os["product_os"]["execution_backend"] == "github_issues"


def test_init_product_os_preserves_existing_files(tmp_path: Path):
    product_dir = tmp_path / ".product"
    product_dir.mkdir()
    brief = product_dir / "product-brief.md"
    brief.write_text("# Existing Brief\n", encoding="utf-8")

    init_product_os(tmp_path)

    assert brief.read_text(encoding="utf-8") == "# Existing Brief\n"
    assert (product_dir / "roadmap.yaml").is_file()


def test_validate_product_os_reports_missing_directory(tmp_path: Path):
    result = validate_product_os(tmp_path)

    assert result["ok"] is False
    assert ".product directory is missing" in result["errors"]


def test_product_status_counts_roadmap_and_work_items(tmp_path: Path):
    init_product_os(tmp_path)
    (tmp_path / ".product" / "roadmap.yaml").write_text(
        """
roadmap:
  now:
    - id: inbox-v1
      title: Inbox
      status: ready-for-build
  next: []
  later: []
  icebox: []
""",
        encoding="utf-8",
    )
    (tmp_path / ".product" / "work-items" / "wi-inbox-001.yaml").write_text(
        """
id: wi-inbox-001
feature_id: inbox-v1
title: Build inbox list
status: ready-for-build
definition_of_done:
  - Inbox list renders
validation:
  - npm test
""",
        encoding="utf-8",
    )

    status = product_status(tmp_path)

    assert status["validation"]["ok"] is True
    assert status["roadmap"]["now"] == 1
    assert status["work_items"]["ready-for-build"] == 1
