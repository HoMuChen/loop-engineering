from scripts.loop_gh_issue_state import normalize_issue, run_gh


def test_normalize_issue_flattens_labels():
    raw = {
        "number": 123,
        "title": "Fix login redirect",
        "state": "OPEN",
        "url": "https://github.com/example/repo/issues/123",
        "labels": [{"name": "loop:ready"}, {"name": "kind:bug"}],
    }

    normalized = normalize_issue(raw)

    assert normalized["number"] == 123
    assert normalized["labels"] == ["loop:ready", "kind:bug"]


def test_run_gh_returns_json():
    def fake_run(command):
        assert command == ["gh", "issue", "view", "123", "--json", "number,title"]
        return '{"number": 123, "title": "Example"}'

    result = run_gh(["issue", "view", "123", "--json", "number,title"], runner=fake_run)

    assert result == {"number": 123, "title": "Example"}
