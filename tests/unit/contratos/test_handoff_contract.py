from __future__ import annotations

import pytest

from src.agents.handoff import (
    accept_handoff,
    cancel_handoff,
    complete_handoff,
    create_handoff,
    fail_handoff,
    reject_handoff,
    transition_handoff,
)


CREATED_AT = "2026-07-22T10:00:00+00:00"
ACCEPTED_AT = "2026-07-22T10:01:00+00:00"
COMPLETED_AT = "2026-07-22T10:02:00+00:00"


def _handoff():
    return create_handoff(
        from_agent="financial_agent",
        to_agent="report_agent",
        reason=(
            "O diagnóstico foi concluído e "
            "precisa ser transformado em relatório."
        ),
        payload={
            "diagnosis_id": "diag-001",
        },
        metadata={
            "thread_id": "thread-001",
        },
        handoff_id="handoff-001",
        timestamp=CREATED_AT,
    )


def test_create_handoff():
    handoff = _handoff()

    assert handoff["handoff_id"] == (
        "handoff-001"
    )

    assert handoff["from_agent"] == (
        "financial_agent"
    )

    assert handoff["to_agent"] == (
        "report_agent"
    )

    assert handoff["status"] == (
        "requested"
    )

    assert handoff["payload"] == {
        "diagnosis_id": "diag-001",
    }

    assert handoff["accepted_at"] is None
    assert handoff["completed_at"] is None


def test_handoff_can_be_accepted():
    accepted = accept_handoff(
        _handoff(),
        timestamp=ACCEPTED_AT,
    )

    assert accepted["status"] == (
        "accepted"
    )

    assert accepted["accepted_at"] == (
        ACCEPTED_AT
    )

    assert accepted["updated_at"] == (
        ACCEPTED_AT
    )


def test_accepted_handoff_can_be_completed():
    accepted = accept_handoff(
        _handoff(),
        timestamp=ACCEPTED_AT,
    )

    completed = complete_handoff(
        accepted,
        result={
            "report_id": "report-001",
        },
        timestamp=COMPLETED_AT,
    )

    assert completed["status"] == (
        "completed"
    )

    assert completed["completed_at"] == (
        COMPLETED_AT
    )

    assert completed["result"] == {
        "report_id": "report-001",
    }


def test_requested_handoff_can_be_rejected():
    rejected = reject_handoff(
        _handoff(),
        reason=(
            "O payload não contém dados suficientes."
        ),
        timestamp=ACCEPTED_AT,
    )

    assert rejected["status"] == (
        "rejected"
    )

    assert (
        "payload"
        in rejected["error"].lower()
    )


def test_accepted_handoff_can_fail():
    accepted = accept_handoff(
        _handoff(),
        timestamp=ACCEPTED_AT,
    )

    failed = fail_handoff(
        accepted,
        error="Falha ao gerar relatório.",
        timestamp=COMPLETED_AT,
    )

    assert failed["status"] == "failed"
    assert failed["error"]


def test_requested_handoff_can_be_cancelled():
    cancelled = cancel_handoff(
        _handoff(),
        reason="Solicitação cancelada.",
        timestamp=ACCEPTED_AT,
    )

    assert cancelled["status"] == (
        "cancelled"
    )


def test_agent_cannot_handoff_to_itself():
    with pytest.raises(
        ValueError,
        match="ele mesmo",
    ):
        create_handoff(
            from_agent="financial_agent",
            to_agent="financial_agent",
            reason="Transferência inválida.",
        )


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("from_agent", ""),
        ("to_agent", "   "),
        ("reason", ""),
    ],
)
def test_required_fields_are_validated(
    field: str,
    value: str,
):
    arguments = {
        "from_agent": "financial_agent",
        "to_agent": "report_agent",
        "reason": "Criar relatório.",
    }

    arguments[field] = value

    with pytest.raises(
        ValueError,
    ):
        create_handoff(
            **arguments,
        )


def test_completed_handoff_cannot_transition_again():
    accepted = accept_handoff(
        _handoff(),
        timestamp=ACCEPTED_AT,
    )

    completed = complete_handoff(
        accepted,
        timestamp=COMPLETED_AT,
    )

    with pytest.raises(
        ValueError,
        match="completed -> accepted",
    ):
        transition_handoff(
            completed,
            status="accepted",
        )


def test_handoff_cannot_complete_before_acceptance():
    with pytest.raises(
        ValueError,
        match="requested -> completed",
    ):
        complete_handoff(
            _handoff(),
            timestamp=COMPLETED_AT,
        )


def test_original_handoff_is_not_mutated():
    requested = _handoff()

    accepted = accept_handoff(
        requested,
        timestamp=ACCEPTED_AT,
    )

    assert requested["status"] == (
        "requested"
    )

    assert requested["accepted_at"] is None

    assert accepted["status"] == (
        "accepted"
    )


def test_payload_and_metadata_are_copied():
    payload = {
        "diagnosis": {
            "score": 80,
        }
    }

    metadata = {
        "thread_id": "thread-001",
    }

    handoff = create_handoff(
        from_agent="financial_agent",
        to_agent="report_agent",
        reason="Preparar relatório.",
        payload=payload,
        metadata=metadata,
    )

    payload["new_key"] = "external"
    metadata["channel"] = "external"

    assert "new_key" not in handoff["payload"]
    assert "channel" not in handoff["metadata"]
