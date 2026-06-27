from scripts.loop_comment import parse_run_comment, render_run_comment


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
