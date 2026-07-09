import json

from scripts.loop_gh_milestone import (
    ensure_milestone,
    find_milestone,
    normalize_milestone,
    run_gh,
)


def test_normalize_milestone_computes_progress():
    raw = {
        "number": 4,
        "title": "feature-search",
        "state": "open",
        "open_issues": 3,
        "closed_issues": 1,
        "html_url": "https://github.com/example/repo/milestone/4",
    }

    normalized = normalize_milestone(raw)

    assert normalized["number"] == 4
    assert normalized["total_issues"] == 4
    assert normalized["closed_percent"] == 25
    assert normalized["complete"] is False
    assert normalized["url"] == "https://github.com/example/repo/milestone/4"


def test_normalize_milestone_complete_when_all_issues_closed():
    normalized = normalize_milestone({"open_issues": 0, "closed_issues": 5})

    assert normalized["closed_percent"] == 100
    assert normalized["complete"] is True


def test_normalize_milestone_empty_is_not_complete():
    normalized = normalize_milestone({"open_issues": 0, "closed_issues": 0})

    assert normalized["closed_percent"] == 0
    assert normalized["complete"] is False


def test_run_gh_returns_none_for_empty_output():
    assert run_gh(["api", "x"], runner=lambda command: "") is None


def test_find_milestone_matches_by_title():
    def fake_run(command):
        return json.dumps(
            [
                {"number": 1, "title": "feature-a", "open_issues": 0, "closed_issues": 2},
                {"number": 2, "title": "feature-b", "open_issues": 1, "closed_issues": 1},
            ]
        )

    milestone = find_milestone("feature-b", runner=fake_run)

    assert milestone is not None
    assert milestone["number"] == 2


def test_ensure_milestone_returns_existing_without_creating():
    calls = []

    def fake_run(command):
        calls.append(command)
        return json.dumps([{"number": 7, "title": "feature-a", "open_issues": 1, "closed_issues": 2}])

    result = ensure_milestone("feature-a", runner=fake_run)

    assert result["created"] is False
    assert result["milestone"]["number"] == 7
    assert all("POST" not in command for command in calls)


def test_ensure_milestone_creates_when_missing():
    def fake_run(command):
        if "POST" in command:
            assert "title=feature-b" in command
            assert "description=New feature" in command
            return json.dumps(
                {"number": 9, "title": "feature-b", "open_issues": 0, "closed_issues": 0}
            )
        return json.dumps([])

    result = ensure_milestone("feature-b", description="New feature", runner=fake_run)

    assert result["created"] is True
    assert result["milestone"]["number"] == 9
