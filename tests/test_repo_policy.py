from pathlib import Path

from scripts.loop_repo_policy import load_policy


def test_load_policy_uses_safe_defaults_when_file_missing(tmp_path: Path):
    policy = load_policy(tmp_path / ".loop-engineering.yml")

    assert policy["branch_prefix"] == "loop/"
    assert policy["merge_method"] == "squash"
    assert policy["auto_merge"] is False
    assert policy["auto_close"] is True
    assert policy["local_repair_limit"] == 3
    assert "security" in policy["protected_labels"]


def test_load_policy_merges_config(tmp_path: Path):
    config = tmp_path / ".loop-engineering.yml"
    config.write_text(
        """
loop_engineering:
  default_agent: claude
  auto_merge: true
  required_verification:
    - pnpm typecheck
    - pnpm test
""",
        encoding="utf-8",
    )

    policy = load_policy(config)

    assert policy["default_agent"] == "claude"
    assert policy["auto_merge"] is True
    assert policy["required_verification"] == ["pnpm typecheck", "pnpm test"]
