from scripts.loop_labels import clean_transient_labels, next_status_labels


def test_next_status_labels_replaces_state_label():
    labels = ["loop:ready", "kind:bug", "priority:p1"]

    result = next_status_labels(labels, "loop:in-progress")

    assert result == ["kind:bug", "priority:p1", "loop:in-progress"]


def test_clean_transient_labels_keeps_done_and_kind():
    labels = ["loop:claimed", "loop:pr-open", "run:stale", "kind:feature", "agent:codex"]

    result = clean_transient_labels(labels)

    assert result == ["kind:feature", "agent:codex", "loop:done"]
