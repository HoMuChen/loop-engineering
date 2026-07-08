from pathlib import Path

import yaml

from scripts.loop_product_os import init_product_os, product_status, validate_product_os


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
