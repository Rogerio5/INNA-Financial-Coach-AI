from __future__ import annotations

import copy

import pytest

from src.agents.team_router import (
    resolve_team_router_decision,
    select_team_supervisor_route,
    team_router_node,
)


@pytest.mark.parametrize(
    (
        "agent",
        "expected_team",
        "expected_supervisor",
    ),
    [
        (
            "financial_agent",
            "financial_team",
            "financial_team_supervisor",
        ),
        (
            "report_agent",
            "financial_team",
            "financial_team_supervisor",
        ),
        (
            "education_agent",
            "knowledge_team",
            "knowledge_team_supervisor",
        ),
        (
            "rag_agent",
            "knowledge_team",
            "knowledge_team_supervisor",
        ),
        (
            "fallback_agent",
            "support_team",
            "support_team_supervisor",
        ),
    ],
)
def test_maps_agent_to_team_supervisor(
    agent: str,
    expected_team: str,
    expected_supervisor: str,
):
    decision = resolve_team_router_decision(
        {
            "next_node": agent,
        }
    )

    assert decision.requested_agent == agent
    assert decision.selected_team == expected_team

    assert decision.team_supervisor_node == expected_supervisor

    assert decision.recovered_to_fallback is False


def test_explicit_team_request_has_priority():
    decision = resolve_team_router_decision(
        {
            "next_node": "financial_agent",
            "team_requested_agent": ("report_agent"),
        }
    )

    assert decision.requested_agent == ("report_agent")

    assert decision.route_source == ("explicit_team_request")


@pytest.mark.parametrize(
    "invalid_agent",
    [
        "",
        "unknown_agent",
        "supervisor",
        "financial_team_supervisor",
    ],
)
def test_invalid_agent_recovers_to_support_team(
    invalid_agent: str,
):
    decision = resolve_team_router_decision(
        {
            "next_node": invalid_agent,
        }
    )

    assert decision.requested_agent == ("fallback_agent")

    assert decision.selected_team == ("support_team")

    assert decision.team_supervisor_node == ("support_team_supervisor")

    assert decision.recovered_to_fallback is True

    assert decision.route_source == ("fallback_recovery")


def test_router_node_populates_hierarchical_state():
    result = team_router_node(
        {
            "next_node": "financial_agent",
            "structured_response": {},
            "trace": [],
        }
    )

    assert result["current_team"] == ("financial_team")

    assert result["team_supervisor"] == ("financial_team_supervisor")

    assert result["team_requested_agent"] == ("financial_agent")

    assert result["team_route"] == ("financial_team_supervisor")

    assert result["team_requires_root_supervisor"] is False


def test_router_decision_is_auditable():
    result = team_router_node(
        {
            "next_node": "rag_agent",
            "structured_response": {},
            "trace": [],
        }
    )

    decision = result["structured_response"]["team_router_decision"]

    assert decision["requested_agent"] == ("rag_agent")

    assert decision["selected_team"] == ("knowledge_team")

    assert decision["team_supervisor_node"] == "knowledge_team_supervisor"


def test_router_adds_trace_event():
    result = team_router_node(
        {
            "next_node": "report_agent",
            "structured_response": {},
            "trace": [
                "supervisor:rule:relatorio",
            ],
        }
    )

    assert result["trace"][-1] == (
        "team_router:financial_team:financial_team_supervisor:report_agent"
    )


def test_router_preserves_existing_trace():
    result = team_router_node(
        {
            "next_node": "fallback_agent",
            "structured_response": {},
            "trace": [
                "trace:existing",
            ],
        }
    )

    assert result["trace"][0] == ("trace:existing")


def test_router_preserves_structured_response():
    result = team_router_node(
        {
            "next_node": "education_agent",
            "structured_response": {
                "existing": {
                    "value": True,
                }
            },
            "trace": [],
        }
    )

    assert result["structured_response"]["existing"]["value"] is True


def test_router_does_not_mutate_input():
    state = {
        "next_node": "financial_agent",
        "structured_response": {},
        "trace": [],
    }

    original = copy.deepcopy(state)

    team_router_node(state)

    assert state == original


@pytest.mark.parametrize(
    (
        "route",
        "expected",
    ),
    [
        (
            "financial_team_supervisor",
            "financial_team_supervisor",
        ),
        (
            "knowledge_team_supervisor",
            "knowledge_team_supervisor",
        ),
        (
            "support_team_supervisor",
            "support_team_supervisor",
        ),
        (
            "",
            "support_team_supervisor",
        ),
        (
            "unknown",
            "support_team_supervisor",
        ),
    ],
)
def test_select_team_supervisor_route(
    route: str,
    expected: str,
):
    assert (
        select_team_supervisor_route(
            {
                "team_supervisor": route,
            }
        )
        == expected
    )


def test_selector_can_use_team_route_fallback():
    result = select_team_supervisor_route(
        {
            "team_supervisor": "",
            "team_route": ("knowledge_team_supervisor"),
        }
    )

    assert result == ("knowledge_team_supervisor")


def test_decision_model_dump_returns_dict():
    decision = resolve_team_router_decision(
        {
            "next_node": "financial_agent",
        }
    )

    payload = decision.model_dump()

    assert isinstance(payload, dict)

    assert payload["selected_team"] == ("financial_team")


def test_requested_handoff_has_priority_over_next_node():
    decision = resolve_team_router_decision(
        {
            "next_node": "financial_agent",
            "handoff_current": {
                "status": "requested",
                "to_agent": "report_agent",
            },
        }
    )

    assert decision.requested_agent == ("report_agent")

    assert decision.selected_team == ("financial_team")


def test_terminal_handoff_does_not_override_next_node():
    decision = resolve_team_router_decision(
        {
            "next_node": "education_agent",
            "handoff_current": {
                "status": "completed",
                "to_agent": "report_agent",
            },
        }
    )

    assert decision.requested_agent == ("education_agent")

    assert decision.selected_team == ("knowledge_team")
