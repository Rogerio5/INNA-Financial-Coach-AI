from __future__ import annotations

from src.agents.shared_blackboard import (
    BLACKBOARD_SCHEMA_VERSION,
    DEFAULT_MAX_BLACKBOARD_PAYLOAD_BYTES,
    can_read_blackboard_entry,
    publish_blackboard_entry,
    read_blackboard_entries,
)


def _publish(
    *,
    payload=None,
    visibility="workflow",
    team=None,
    current_entries=(),
    max_entries=64,
):
    return publish_blackboard_entry(
        current_entries=current_entries,
        kind="result",
        producer="financial_agent",
        visibility=visibility,
        team=team,
        payload=(
            payload
            or {
                "status": "completed",
                "score": 0.95,
            }
        ),
        max_entries=max_entries,
    )


def test_workflow_entry_is_published():
    result = _publish()

    assert result.accepted is True
    assert (
        result.reason
        == "blackboard_entry_published"
    )
    assert result.entry is not None
    assert (
        result.entry.schema_version
        == BLACKBOARD_SCHEMA_VERSION
        == "1.0.0"
    )
    assert (
        result.entry.entry_id
        .startswith("bb_")
    )
    assert len(result.entries) == 1


def test_entry_id_is_content_deterministic():
    first = _publish()
    second = _publish()

    assert first.entry is not None
    assert second.entry is not None

    assert (
        first.entry.entry_id
        == second.entry.entry_id
    )


def test_duplicate_entry_does_not_grow_blackboard():
    first = _publish()

    assert first.entry is not None

    second = _publish(
        current_entries=first.entries,
    )

    assert second.accepted is True
    assert (
        second.reason
        == "blackboard_entry_deduplicated"
    )
    assert len(second.entries) == 1


def test_team_visibility_requires_team():
    result = _publish(
        visibility="team",
    )

    assert result.accepted is False
    assert (
        result.reason
        == "blackboard_team_required"
    )


def test_team_entry_is_visible_to_same_team():
    result = _publish(
        visibility="team",
        team="financial_team",
    )

    assert result.entry is not None

    assert can_read_blackboard_entry(
        result.entry,
        consumer_team="financial_team",
    )


def test_team_entry_is_hidden_from_other_team():
    result = _publish(
        visibility="team",
        team="financial_team",
    )

    assert result.entry is not None

    assert not can_read_blackboard_entry(
        result.entry,
        consumer_team="knowledge_team",
    )


def test_workflow_entry_is_visible_cross_team():
    result = _publish()

    assert result.entry is not None

    assert can_read_blackboard_entry(
        result.entry,
        consumer_team="knowledge_team",
    )


def test_read_can_filter_by_kind():
    result = _publish()

    assert result.entry is not None

    visible = read_blackboard_entries(
        result.entries,
        consumer_team="knowledge_team",
        kinds=[
            "decision",
        ],
    )

    assert visible == ()


def test_raw_user_message_field_is_blocked():
    result = _publish(
        payload={
            "user_message": (
                "mensagem privada"
            ),
        },
    )

    assert result.accepted is False
    assert (
        result.reason
        == "blackboard_payload_contains_blocked_field"
    )


def test_nested_conversation_history_is_blocked():
    result = _publish(
        payload={
            "metadata": {
                "conversation_history": [
                    "mensagem privada",
                ]
            }
        },
    )

    assert result.accepted is False


def test_nested_token_field_is_blocked():
    result = _publish(
        payload={
            "metadata": {
                "token": "secret-value",
            }
        },
    )

    assert result.accepted is False


def test_response_generated_metadata_is_allowed():
    result = _publish(
        payload={
            "task_status": "completed",
            "response_generated": True,
        },
    )

    assert result.accepted is True


def test_full_response_field_is_blocked():
    result = _publish(
        payload={
            "response": (
                "resposta integral do usuario"
            ),
        },
    )

    assert result.accepted is False


def test_non_json_payload_is_rejected():
    result = _publish(
        payload={
            "value": object(),
        },
    )

    assert result.accepted is False
    assert (
        result.reason
        == "blackboard_payload_not_json_serializable"
    )


def test_nan_is_rejected():
    result = _publish(
        payload={
            "score": float("nan"),
        },
    )

    assert result.accepted is False


def test_entry_budget_fails_closed():
    first = _publish(
        max_entries=1,
    )

    second = publish_blackboard_entry(
        current_entries=first.entries,
        kind="decision",
        producer="financial_agent",
        visibility="workflow",
        payload={
            "decision": "continue",
        },
        max_entries=1,
    )

    assert second.accepted is False
    assert (
        second.reason
        == "blackboard_entry_budget_exceeded"
    )


def test_invalid_zero_budget_is_rejected():
    result = _publish(
        max_entries=0,
    )

    assert result.accepted is False
    assert (
        result.reason
        == "blackboard_invalid_entry_budget"
    )


def test_payload_size_limit_is_enforced():
    result = _publish(
        payload={
            "summary": (
                "x"
                * (
                    DEFAULT_MAX_BLACKBOARD_PAYLOAD_BYTES
                    + 100
                )
            )
        },
    )

    assert result.accepted is False
    assert (
        result.reason
        == "blackboard_payload_too_large"
    )


def test_producer_is_required():
    result = publish_blackboard_entry(
        current_entries=(),
        kind="fact",
        producer="",
        visibility="workflow",
        payload={
            "name": "risk",
            "value": "low",
        },
    )

    assert result.accepted is False
    assert (
        result.reason
        == "blackboard_producer_required"
    )



def test_invalid_entry_kind_fails_closed():
    result = publish_blackboard_entry(
        current_entries=(),
        kind="unknown",  # type: ignore[arg-type]
        producer="financial_agent",
        visibility="workflow",
        payload={
            "status": "completed",
        },
    )

    assert result.accepted is False
    assert (
        result.reason
        == "blackboard_invalid_entry_kind"
    )


def test_invalid_visibility_fails_closed():
    result = publish_blackboard_entry(
        current_entries=(),
        kind="result",
        producer="financial_agent",
        visibility="public",  # type: ignore[arg-type]
        payload={
            "status": "completed",
        },
    )

    assert result.accepted is False
    assert (
        result.reason
        == "blackboard_invalid_visibility"
    )
