from scripts.loop_labels import (
    LABEL_CATALOG,
    STATE_LABELS,
    clean_transient_labels,
    ensure_labels,
    next_status_labels,
)


def test_next_status_labels_replaces_state_label():
    labels = ["loop:ready", "kind:bug", "priority:p1"]

    result = next_status_labels(labels, "loop:in-progress")

    assert result == ["kind:bug", "priority:p1", "loop:in-progress"]


def test_clean_transient_labels_keeps_done_and_kind():
    labels = ["loop:claimed", "loop:pr-open", "run:stale", "kind:feature", "agent:codex"]

    result = clean_transient_labels(labels)

    assert result == ["kind:feature", "agent:codex", "loop:done"]


def test_label_catalog_covers_every_state_label():
    catalog_names = {label["name"] for label in LABEL_CATALOG}

    assert STATE_LABELS <= catalog_names


def test_ensure_labels_upserts_each_catalog_entry():
    calls = []

    def fake_run(command):
        calls.append(command)

    ensured = ensure_labels(runner=fake_run)

    assert ensured == [label["name"] for label in LABEL_CATALOG]
    assert len(calls) == len(LABEL_CATALOG)
    # Every command must use --force so re-running is an idempotent upsert.
    assert all("--force" in command for command in calls)
    first = calls[0]
    assert first[:3] == ["gh", "label", "create"]
