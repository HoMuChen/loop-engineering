from scripts.loop_gh_pr_state import GET_PR_JSON_FIELDS, ci_summary, normalize_pr


def test_normalize_pr_extracts_review_and_merge_state():
    raw = {
        "number": 55,
        "title": "Fix login redirect",
        "state": "OPEN",
        "url": "https://github.com/example/repo/pull/55",
        "headRefOid": "a1b2c3d4",
        "mergeStateStatus": "CLEAN",
        "reviewDecision": "APPROVED",
        "statusCheckRollup": [],
    }

    normalized = normalize_pr(raw)

    assert normalized["number"] == 55
    assert normalized["review_decision"] == "APPROVED"
    assert normalized["merge_state"] == "CLEAN"


def test_normalize_pr_exposes_head_sha():
    """`loop-review-pr` keys review idempotence on this field: it records the reviewed
    commit and skips re-reviewing when the head has not moved. Drop it and the reviewer
    silently loses its memory, re-reviews unchanged diffs, and can reverse its own
    earlier approval by chance."""
    normalized = normalize_pr({"number": 1, "headRefOid": "deadbeef"})

    assert normalized["head_sha"] == "deadbeef"


def test_get_pr_requests_head_sha_from_gh():
    """normalize_pr can only surface what `gh pr view --json` was asked for."""
    assert "headRefOid" in GET_PR_JSON_FIELDS


def test_ci_summary_detects_failure():
    checks = [
        {"name": "typecheck", "conclusion": "SUCCESS"},
        {"name": "test", "conclusion": "FAILURE"},
    ]

    summary = ci_summary(checks)

    assert summary["state"] == "failed"
    assert summary["failed"] == ["test"]
