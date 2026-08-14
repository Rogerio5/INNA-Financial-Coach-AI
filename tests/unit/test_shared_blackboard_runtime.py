from __future__ import annotations

from src.agents.shared_blackboard_runtime import (
    load_shared_blackboard,
    publish_shared_blackboard,
    read_shared_blackboard,
)


def _state():
    return {
        "shared_blackboard_entries": [],
        "shared_blackboard_count": 0,
        "max_shared_blackboard_entries": 64,
        "shared_blackboard_audit": [],
        "shared_blackboard_last_decision": {},
        "trace": [],
    }


def test_financial_agent_publishes_workflow_result():
    state = _state()

    update = publish_shared_blackboard(
        state,
        principal="financial_agent",
        kind="result",
        visibility="workflow",
        payload={
            "task_status": "completed",
            "score": 0.95,
        },
    )

    assert (
        update["shared_blackboard_count"]
        == 1
    )

    assert (
        update[
            "shared_blackboard_last_decision"
        ]["allowed"]
        is True
    )


def test_runtime_state_is_json_serializable_shape():
    state = _state()

    update = publish_shared_blackboard(
        state,
        principal="financial_agent",
        kind="result",
        visibility="workflow",
        payload={
            "status": "completed",
        },
    )

    entry = update[
        "shared_blackboard_entries"
    ][0]

    assert isinstance(
        entry,
        dict,
    )
    assert isinstance(
        entry["payload"],
        dict,
    )


def test_duplicate_publication_does_not_grow_state():
    state = _state()

    first = publish_shared_blackboard(
        state,
        principal="financial_agent",
        kind="result",
        visibility="workflow",
        payload={
            "status": "completed",
        },
    )

    state.update(
        first
    )

    second = publish_shared_blackboard(
        state,
        principal="financial_agent",
        kind="result",
        visibility="workflow",
        payload={
            "status": "completed",
        },
    )

    assert (
        second["shared_blackboard_count"]
        == 1
    )

    assert (
        second[
            "shared_blackboard_last_decision"
        ]["reason"]
        == "blackboard_entry_deduplicated"
    )


def test_acl_denial_does_not_create_entry():
    state = _state()

    update = publish_shared_blackboard(
        state,
        principal="communication_agent",
        kind="result",
        visibility="workflow",
        payload={
            "status": "completed",
        },
    )

    assert (
        "shared_blackboard_entries"
        not in update
    )

    assert (
        update[
            "shared_blackboard_last_decision"
        ]["allowed"]
        is False
    )


def test_blocked_raw_field_is_not_published():
    update = publish_shared_blackboard(
        _state(),
        principal="financial_agent",
        kind="result",
        visibility="workflow",
        payload={
            "user_message": "private",
        },
    )

    assert (
        "shared_blackboard_entries"
        not in update
    )

    assert (
        update[
            "shared_blackboard_last_decision"
        ]["allowed"]
        is False
    )


def test_audit_does_not_copy_payload():
    secret_marker = (
        "private-payload-marker"
    )

    update = publish_shared_blackboard(
        _state(),
        principal="financial_agent",
        kind="result",
        visibility="workflow",
        payload={
            "summary": secret_marker,
        },
    )

    assert (
        secret_marker
        not in str(
            update[
                "shared_blackboard_audit"
            ]
        )
    )


def test_financial_team_entry_hidden_from_knowledge_agent():
    state = _state()

    update = publish_shared_blackboard(
        state,
        principal="financial_agent",
        kind="result",
        visibility="team",
        team="financial_team",
        payload={
            "status": "completed",
        },
    )

    state.update(
        update
    )

    result = read_shared_blackboard(
        state,
        principal="rag_agent",
    )

    assert result.entries == ()


def test_financial_team_entry_visible_to_report_agent():
    state = _state()

    state.update(
        publish_shared_blackboard(
            state,
            principal="financial_agent",
            kind="result",
            visibility="team",
            team="financial_team",
            payload={
                "status": "completed",
            },
        )
    )

    result = read_shared_blackboard(
        state,
        principal="report_agent",
    )

    assert len(
        result.entries
    ) == 1


def test_workflow_entry_visible_cross_team():
    state = _state()

    state.update(
        publish_shared_blackboard(
            state,
            principal="financial_agent",
            kind="result",
            visibility="workflow",
            payload={
                "status": "completed",
            },
        )
    )

    result = read_shared_blackboard(
        state,
        principal="rag_agent",
    )

    assert len(
        result.entries
    ) == 1


def test_communication_identity_reads_nothing():
    state = _state()

    state.update(
        publish_shared_blackboard(
            state,
            principal="financial_agent",
            kind="result",
            visibility="workflow",
            payload={
                "status": "completed",
            },
        )
    )

    result = read_shared_blackboard(
        state,
        principal="communication_agent",
    )

    assert result.entries == ()


def test_corrupted_entry_blocks_new_publication():
    state = _state()

    state[
        "shared_blackboard_entries"
    ] = [
        {
            "schema_version": "1.0.0",
            "entry_id": "bb_tampered",
            "kind": "result",
            "producer": "financial_agent",
            "visibility": "workflow",
            "team": None,
            "payload": {
                "status": "completed",
            },
        }
    ]

    update = publish_shared_blackboard(
        state,
        principal="financial_agent",
        kind="result",
        visibility="workflow",
        payload={
            "next": "value",
        },
    )

    assert (
        update[
            "shared_blackboard_last_decision"
        ]["reason"]
        == "blackboard_existing_state_invalid"
    )

    assert (
        "shared_blackboard_entries"
        not in update
    )


def test_corrupted_entry_is_not_read():
    state = _state()

    state[
        "shared_blackboard_entries"
    ] = [
        {
            "invalid": True,
        }
    ]

    result = read_shared_blackboard(
        state,
        principal="financial_agent",
    )

    assert result.entries == ()
    assert (
        result.rejected_entries
        == 1
    )


def test_loader_accepts_canonical_runtime_entry():
    state = _state()

    state.update(
        publish_shared_blackboard(
            state,
            principal="financial_agent",
            kind="evidence",
            visibility="workflow",
            payload={
                "source": "diagnosis",
                "available": True,
            },
        )
    )

    entries, rejected = (
        load_shared_blackboard(
            state
        )
    )

    assert rejected == 0
    assert len(entries) == 1


def test_entry_budget_is_enforced_from_state():
    state = _state()

    state[
        "max_shared_blackboard_entries"
    ] = 1

    state.update(
        publish_shared_blackboard(
            state,
            principal="financial_agent",
            kind="result",
            visibility="workflow",
            payload={
                "value": 1,
            },
        )
    )

    second = publish_shared_blackboard(
        state,
        principal="financial_agent",
        kind="evidence",
        visibility="workflow",
        payload={
            "value": 2,
        },
    )

    assert (
        second[
            "shared_blackboard_last_decision"
        ]["reason"]
        == "blackboard_entry_budget_exceeded"
    )


def test_audit_is_bounded():
    state = _state()

    state[
        "shared_blackboard_audit"
    ] = [
        {
            "event": number,
        }
        for number in range(
            200
        )
    ]

    update = publish_shared_blackboard(
        state,
        principal="financial_agent",
        kind="result",
        visibility="workflow",
        payload={
            "status": "completed",
        },
    )

    assert len(
        update[
            "shared_blackboard_audit"
        ]
    ) == 128
