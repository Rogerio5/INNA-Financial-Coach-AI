"""Testes do contrato A2A governado da INNA."""

from __future__ import annotations

import pytest

from src.agents.a2a_contract import (
    A2A_MESSAGE_SCHEMA_VERSION,
    create_a2a_message,
    create_handoff_from_a2a,
    evaluate_a2a_message,
)
from src.agents.agent_catalog import (
    criar_registro_agentes_inna,
)


def _registry():
    return criar_registro_agentes_inna()


def _message(
    *,
    target_agent: str = "report_agent",
    capability: str = "report_preparation",
):
    return create_a2a_message(
        source_agent="financial_agent",
        target_agent=target_agent,
        capability=capability,
        payload={
            "request": "prepare_report",
        },
        trace_id="trace-a2a-001",
    )


def test_a2a_message_has_formal_envelope():
    message = _message()

    assert message[
        "schema_version"
    ] == A2A_MESSAGE_SCHEMA_VERSION

    assert message[
        "kind"
    ] == "task_request"

    assert message[
        "source_agent"
    ] == "financial_agent"

    assert message[
        "target_agent"
    ] == "report_agent"

    assert message[
        "trace_id"
    ] == "trace-a2a-001"

    assert message["message_id"]


def test_a2a_self_target_is_rejected():
    with pytest.raises(
        ValueError,
        match="agentes distintos",
    ):
        create_a2a_message(
            source_agent="financial_agent",
            target_agent="financial_agent",
            capability="financial_diagnosis",
        )


def test_a2a_authorizes_registered_capable_target():
    decision = evaluate_a2a_message(
        _message(),
        agent_registry=_registry(),
        a2a_message_count=0,
        max_a2a_messages=6,
        handoff_count=0,
        max_handoffs=3,
    )

    assert decision.allowed is True
    assert (
        decision.reason
        == "a2a_route_allowed"
    )

    assert (
        decision.next_message_count
        == 1
    )

    assert (
        decision.requires_handoff
        is True
    )

    assert decision.target_team
    assert decision.target_supervisor


def test_a2a_zero_budget_denies_message():
    decision = evaluate_a2a_message(
        _message(),
        agent_registry=_registry(),
        a2a_message_count=0,
        max_a2a_messages=0,
        handoff_count=0,
        max_handoffs=1,
    )

    assert decision.allowed is False

    assert decision.reason == (
        "a2a_message_budget_exceeded"
    )


def test_a2a_message_limit_is_enforced():
    decision = evaluate_a2a_message(
        _message(),
        agent_registry=_registry(),
        a2a_message_count=6,
        max_a2a_messages=6,
        handoff_count=0,
        max_handoffs=3,
    )

    assert decision.allowed is False

    assert decision.reason == (
        "a2a_message_budget_exceeded"
    )


def test_a2a_handoff_limit_is_enforced():
    decision = evaluate_a2a_message(
        _message(),
        agent_registry=_registry(),
        a2a_message_count=1,
        max_a2a_messages=6,
        handoff_count=3,
        max_handoffs=3,
    )

    assert decision.allowed is False

    assert decision.reason == (
        "a2a_handoff_budget_exceeded"
    )


def test_a2a_target_requires_capability():
    decision = evaluate_a2a_message(
        _message(
            capability="knowledge_retrieval"
        ),
        agent_registry=_registry(),
        a2a_message_count=0,
        max_a2a_messages=6,
        handoff_count=0,
        max_handoffs=3,
    )

    assert decision.allowed is False

    assert decision.reason == (
        "a2a_target_capability_denied"
    )


def test_a2a_service_identity_cannot_be_target():
    decision = evaluate_a2a_message(
        _message(
            target_agent="communication_agent",
            capability="email_preparation",
        ),
        agent_registry=_registry(),
        a2a_message_count=0,
        max_a2a_messages=6,
        handoff_count=0,
        max_handoffs=3,
    )

    assert decision.allowed is False

    assert decision.reason == (
        "a2a_agent_kind_denied"
    )


def test_a2a_non_hierarchical_agent_is_not_handoff_target():
    decision = evaluate_a2a_message(
        _message(
            target_agent="research_agent",
            capability="agentic_research",
        ),
        agent_registry=_registry(),
        a2a_message_count=0,
        max_a2a_messages=6,
        handoff_count=0,
        max_handoffs=3,
    )

    assert decision.allowed is False

    assert decision.reason == (
        "a2a_target_not_handoff_routable"
    )


def test_a2a_unknown_agent_fails_closed():
    decision = evaluate_a2a_message(
        _message(
            target_agent="unknown_agent",
        ),
        agent_registry=_registry(),
        a2a_message_count=0,
        max_a2a_messages=6,
        handoff_count=0,
        max_handoffs=3,
    )

    assert decision.allowed is False

    assert decision.reason == (
        "a2a_agent_not_registered"
    )


def test_a2a_can_be_adapted_to_existing_handoff():
    message = _message()

    handoff = create_handoff_from_a2a(
        message
    )

    assert handoff[
        "status"
    ] == "requested"

    assert handoff[
        "from_agent"
    ] == "financial_agent"

    assert handoff[
        "to_agent"
    ] == "report_agent"

    assert handoff[
        "reason"
    ] == "a2a:report_preparation"

    assert handoff[
        "payload"
    ] == message["payload"]

    assert handoff[
        "metadata"
    ][
        "a2a_message_id"
    ] == message["message_id"]

    assert handoff[
        "metadata"
    ][
        "a2a_trace_id"
    ] == message["trace_id"]
