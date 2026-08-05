from __future__ import annotations

from typing import get_type_hints

from src.agents.graph import (
    _criar_estado_inicial,
)
from src.agents.state import (
    InnaAgentState,
)


def _create_state(
    *,
    thread_id: str = "thread-team-state",
) -> InnaAgentState:
    return _criar_estado_inicial(
        "Teste da hierarquia de equipes.",
        thread_id=thread_id,
        usuario_id="user-team-state",
        idioma="pt-BR",
        moeda="BRL",
    )


def test_initial_state_enables_hierarchical_routing():
    state = _create_state(
        thread_id="thread-team-001",
    )

    assert state["hierarchical_routing_enabled"] is True


def test_initial_state_contains_empty_team_identity():
    state = _create_state(
        thread_id="thread-team-002",
    )

    assert state["current_team"] == ""
    assert state["team_supervisor"] == ""
    assert state["team_route"] == ""
    assert state["team_requested_agent"] == ""


def test_initial_state_contains_empty_team_routing_metadata():
    state = _create_state(
        thread_id="thread-team-003",
    )

    assert state["team_route_source"] == ""
    assert state["team_routing_reason"] == ""

    assert state["team_requires_root_supervisor"] is False


def test_initial_state_contains_empty_team_route_history():
    state = _create_state(
        thread_id="thread-team-004",
    )

    assert state["team_route_history"] == []


def test_initial_state_has_root_supervisor_guard():
    state = _create_state(
        thread_id="thread-team-005",
    )

    assert state["root_supervisor_visits"] == 0

    assert state["max_root_supervisor_visits"] == 3


def test_root_supervisor_limit_is_positive():
    state = _create_state(
        thread_id="thread-team-006",
    )

    assert state["max_root_supervisor_visits"] > 0


def test_root_supervisor_counter_starts_below_limit():
    state = _create_state(
        thread_id="thread-team-007",
    )

    assert state["root_supervisor_visits"] < state["max_root_supervisor_visits"]


def test_initial_state_keeps_handoff_configuration():
    state = _create_state(
        thread_id="thread-team-008",
    )

    assert state["handoff_current"] is None
    assert state["handoff_history"] == []
    assert state["handoff_count"] == 0
    assert state["max_handoffs"] == 3

    assert state["handoff_limit_exceeded"] is False


def test_initial_state_keeps_handoff_request_empty():
    state = _create_state(
        thread_id="thread-team-009",
    )

    assert state["handoff_required"] is False
    assert state["handoff_target"] == ""
    assert state["handoff_reason"] == ""


def test_initial_state_preserves_conversation_identity():
    state = _create_state(
        thread_id="thread-team-010",
    )

    assert state["thread_id"] == ("thread-team-010")

    assert state["user_id"] == ("user-team-state")

    assert state["language"] == "pt-BR"
    assert state["currency"] == "BRL"


def test_initial_state_creates_independent_team_histories():
    first = _create_state(
        thread_id="thread-team-011",
    )

    second = _create_state(
        thread_id="thread-team-012",
    )

    first["team_route_history"].append(
        {
            "team_name": "financial_team",
        }
    )

    assert second["team_route_history"] == []


def test_initial_state_creates_independent_traces():
    first = _create_state(
        thread_id="thread-team-013",
    )

    second = _create_state(
        thread_id="thread-team-014",
    )

    first["trace"].append("team:test")

    assert second["trace"] == []


def test_state_type_exposes_team_annotations():
    annotations = InnaAgentState.__annotations__

    required_fields = {
        "hierarchical_routing_enabled",
        "current_team",
        "team_supervisor",
        "team_route",
        "team_requested_agent",
        "team_route_source",
        "team_routing_reason",
        "team_requires_root_supervisor",
        "team_route_history",
        "root_supervisor_visits",
        "max_root_supervisor_visits",
    }

    assert required_fields.issubset(annotations)


def test_state_type_hints_can_be_resolved():
    type_hints = get_type_hints(InnaAgentState)

    assert type_hints["hierarchical_routing_enabled"] is bool

    assert type_hints["current_team"] is str

    assert type_hints["team_supervisor"] is str

    assert type_hints["team_route"] is str

    assert type_hints["team_requested_agent"] is str


def test_team_route_history_annotation_is_present():
    type_hints = get_type_hints(InnaAgentState)

    assert "team_route_history" in type_hints


def test_root_supervisor_annotations_are_integers():
    type_hints = get_type_hints(InnaAgentState)

    assert type_hints["root_supervisor_visits"] is int

    assert type_hints["max_root_supervisor_visits"] is int


def test_team_requires_root_supervisor_annotation_is_boolean():
    type_hints = get_type_hints(InnaAgentState)

    assert type_hints["team_requires_root_supervisor"] is bool
