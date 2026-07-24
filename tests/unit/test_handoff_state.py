from __future__ import annotations

from typing import get_type_hints

from src.agents.state import (
    InnaAgentState,
    merge_handoff_history,
)


def _handoff(
    handoff_id: str,
    status: str,
) -> dict:
    return {
        "handoff_id": handoff_id,
        "from_agent": "financial_agent",
        "to_agent": "report_agent",
        "reason": "Preparar relatório.",
        "payload": {},
        "status": status,
    }


def test_handoff_fields_exist_in_agent_state():
    hints = get_type_hints(
        InnaAgentState,
        include_extras=True,
    )

    expected_fields = {
        "handoff_current",
        "handoff_history",
        "handoff_count",
        "handoff_required",
        "handoff_target",
        "handoff_reason",
    }

    assert expected_fields.issubset(
        hints
    )


def test_empty_handoff_history_merge():
    assert merge_handoff_history(
        None,
        None,
    ) == []

    assert merge_handoff_history(
        [],
        [],
    ) == []


def test_new_handoff_is_appended():
    requested = _handoff(
        "handoff-001",
        "requested",
    )

    result = merge_handoff_history(
        [],
        [requested],
    )

    assert result == [requested]


def test_multiple_handoffs_preserve_order():
    first = _handoff(
        "handoff-001",
        "completed",
    )

    second = _handoff(
        "handoff-002",
        "requested",
    )

    result = merge_handoff_history(
        [first],
        [second],
    )

    assert [
        item["handoff_id"]
        for item in result
    ] == [
        "handoff-001",
        "handoff-002",
    ]


def test_existing_handoff_is_updated_in_place():
    requested = _handoff(
        "handoff-001",
        "requested",
    )

    accepted = _handoff(
        "handoff-001",
        "accepted",
    )

    result = merge_handoff_history(
        [requested],
        [accepted],
    )

    assert len(result) == 1
    assert result[0]["status"] == "accepted"


def test_update_does_not_change_original_position():
    first = _handoff(
        "handoff-001",
        "requested",
    )

    second = _handoff(
        "handoff-002",
        "requested",
    )

    first_completed = _handoff(
        "handoff-001",
        "completed",
    )

    result = merge_handoff_history(
        [
            first,
            second,
        ],
        [
            first_completed,
        ],
    )

    assert [
        item["handoff_id"]
        for item in result
    ] == [
        "handoff-001",
        "handoff-002",
    ]

    assert result[0]["status"] == (
        "completed"
    )


def test_complete_history_return_is_not_duplicated():
    first = _handoff(
        "handoff-001",
        "completed",
    )

    second = _handoff(
        "handoff-002",
        "accepted",
    )

    current = [first]
    complete_update = [
        first,
        second,
    ]

    result = merge_handoff_history(
        current,
        complete_update,
    )

    assert result == complete_update


def test_invalid_records_are_ignored():
    valid = _handoff(
        "handoff-001",
        "requested",
    )

    result = merge_handoff_history(
        [],
        [
            {},
            {
                "status": "requested",
            },
            valid,
        ],
    )

    assert result == [valid]


def test_reducer_does_not_mutate_original_records():
    original = _handoff(
        "handoff-001",
        "requested",
    )

    result = merge_handoff_history(
        [],
        [original],
    )

    result[0]["status"] = "completed"

    assert original["status"] == (
        "requested"
    )


def test_same_update_is_idempotent():
    requested = _handoff(
        "handoff-001",
        "requested",
    )

    first_result = merge_handoff_history(
        [],
        [requested],
    )

    second_result = merge_handoff_history(
        first_result,
        [requested],
    )

    assert second_result == [
        requested
    ]


def test_invalid_current_records_are_ignored():
    valid = _handoff(
        "handoff-001",
        "requested",
    )

    result = merge_handoff_history(
        [
            {},
            {
                "status": "accepted",
            },
            valid,
        ],
        [],
    )

    assert result == [valid]


def test_blank_handoff_id_is_ignored():
    valid = _handoff(
        "handoff-001",
        "requested",
    )

    result = merge_handoff_history(
        [],
        [
            {
                "handoff_id": "   ",
                "status": "requested",
            },
            valid,
        ],
    )

    assert result == [valid]


def test_handoff_id_is_normalized():
    record = _handoff(
        " handoff-001 ",
        "requested",
    )

    result = merge_handoff_history(
        [],
        [record],
    )

    assert result[0]["handoff_id"] == (
        "handoff-001"
    )

