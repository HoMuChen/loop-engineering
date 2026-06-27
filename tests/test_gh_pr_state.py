from scripts.loop_gh_pr_state import ci_summary, normalize_pr


def test_normalize_pr_extracts_review_and_merge_state():
    raw = {
        "number": 55,
        "title": "Fix login redirect",
        "state": "OPEN",
        "url": "https://github.com/example/repo/pull/55",
        "mergeStateStatus": "CLEAN",
        "reviewDecision": "APPROVED",
        "statusCheckRollup": [],
    }

    normalized = normalize_pr(raw)

    assert normalized["number"] == 55
    assert normalized["review_decision"] == "APPROVED"
    assert normalized["merge_state"] == "CLEAN"


def test_ci_summary_detects_failure():
    checks = [
        {"name": "typecheck", "conclusion": "SUCCESS"},
        {"name": "test", "conclusion": "FAILURE"},
    ]

    summary = ci_summary(checks)

    assert summary["state"] == "failed"
    assert summary["failed"] == ["test"]
