from datetime import UTC, datetime

from scripts.loop_comment import assess_heartbeat, parse_run_comment, render_run_comment

NOW = datetime(2026, 7, 11, 10, 0, 0, tzinfo=UTC)


def test_assess_heartbeat_fresh_within_window():
    result = assess_heartbeat("2026-07-11T09:30:00Z", stale_after_minutes=120, now=NOW)

    assert result["state"] == "fresh"
    assert result["stale"] is False


def test_assess_heartbeat_stale_past_window():
    result = assess_heartbeat("2026-07-11T07:00:00Z", stale_after_minutes=120, now=NOW)

    assert result["state"] == "stale"
    assert result["stale"] is True


def test_assess_heartbeat_future_beyond_skew_is_invalid_and_stale():
    # A Taipei-local time mislabeled as Z lands ~8 hours in the future; it must
    # not keep the run "fresh" until the mislabeled clock catches up.
    result = assess_heartbeat("2026-07-11T17:38:00Z", stale_after_minutes=120, now=NOW)

    assert result["state"] == "invalid-future"
    assert result["stale"] is True


def test_assess_heartbeat_small_future_skew_is_fresh():
    result = assess_heartbeat("2026-07-11T10:02:00Z", stale_after_minutes=120, now=NOW)

    assert result["state"] == "fresh"
    assert result["stale"] is False


def test_assess_heartbeat_unparsable_is_invalid_and_stale():
    result = assess_heartbeat("yesterday-ish", stale_after_minutes=120, now=NOW)

    assert result["state"] == "invalid-format"
    assert result["stale"] is True


def test_parse_run_comment_extracts_fields():
    body = """before
<!-- loop-engineering:run v1 -->
Run: run-123
Agent: codex
Status: in-progress
Branch: loop/123-title
PR: none
Started: 2026-06-27T10:20:00Z
Updated: 2026-06-27T10:35:00Z

Plan:
- Edit files

Verification:
- pending

Blockers:
- none
<!-- /loop-engineering:run -->
after"""

    parsed = parse_run_comment(body)

    assert parsed["run_id"] == "run-123"
    assert parsed["agent"] == "codex"
    assert parsed["status"] == "in-progress"
    assert parsed["branch"] == "loop/123-title"
    assert parsed["pr"] == "none"
    assert parsed["plan"] == ["Edit files"]
    assert parsed["verification"] == ["pending"]
    assert parsed["blockers"] == ["none"]


def test_render_run_comment_round_trips():
    rendered = render_run_comment(
        {
            "run_id": "run-456",
            "agent": "claude",
            "status": "claimed",
            "branch": "loop/456-example",
            "pr": "none",
            "started": "2026-06-27T11:00:00Z",
            "updated": "2026-06-27T11:00:00Z",
            "plan": ["Inspect issue", "Write tests"],
            "verification": ["pending"],
            "blockers": ["none"],
        }
    )

    parsed = parse_run_comment(rendered)

    assert parsed["run_id"] == "run-456"
    assert parsed["agent"] == "claude"
    assert parsed["plan"] == ["Inspect issue", "Write tests"]
