from __future__ import annotations

import copy

import pytest

from src.agents.team_hierarchy import (
    TeamHierarchyError,
)
from src.agents.team_supervisor import (
    TEAM_SUPERVISOR_NODES,
    financial_team_supervisor_node,
    knowledge_team_supervisor_node,
    resolve_team_supervisor_decision,
    support_team_supervisor_node,
)


def _base_state() -> dict:
    return {
        "intent": "diagnostico_financeiro",
        "next_node": "financial_agent",
        "team_requested_agent": "",
        "structured_response": {},
        "team_route_history": [],
        "trace": [],
    }


def test_financial_team_preserves_requested_financial_agent():
    result = financial_team_supervisor_node(
        _base_state()
    )

    assert result["next_node"] == (
        "financial_agent"
    )

    assert result["current_team"] == (
        "financial_team"
    )

    assert result[
        "team_route_source"
    ] == "requested_agent"


def test_financial_team_selects_report_agent():
    state = _base_state()
    state["next_node"] = "report_agent"
    state["intent"] = "relatorio"

    result = financial_team_supervisor_node(
        state
    )

    assert result["next_node"] == (
        "report_agent"
    )


def test_composite_diagnosis_stays_with_financial_agent():
    state = _base_state()
    state["generate_report"] = True
    state["next_node"] = "financial_agent"

    result = financial_team_supervisor_node(
        state
    )

    assert result["next_node"] == (
        "financial_agent"
    )


def test_financial_team_infers_agent_from_diagnosis_intent():
    state = _base_state()
    state["next_node"] = ""
    state["intent"] = (
        "diagnostico_financeiro"
    )

    result = financial_team_supervisor_node(
        state
    )

    assert result["next_node"] == (
        "financial_agent"
    )

    assert result[
        "team_route_source"
    ] == "intent_rule"


def test_financial_team_infers_agent_from_history_intent():
    state = _base_state()
    state["next_node"] = ""
    state["intent"] = (
        "historico_financeiro"
    )

    result = financial_team_supervisor_node(
        state
    )

    assert result["next_node"] == (
        "financial_agent"
    )


def test_financial_team_infers_report_agent():
    state = _base_state()
    state["next_node"] = ""
    state["intent"] = "relatorio"

    result = financial_team_supervisor_node(
        state
    )

    assert result["next_node"] == (
        "report_agent"
    )


def test_knowledge_team_selects_education_agent():
    state = _base_state()
    state["next_node"] = "education_agent"
    state["intent"] = (
        "educacao_financeira"
    )

    result = knowledge_team_supervisor_node(
        state
    )

    assert result["next_node"] == (
        "education_agent"
    )

    assert result["current_team"] == (
        "knowledge_team"
    )


def test_knowledge_team_selects_rag_agent():
    state = _base_state()
    state["next_node"] = "rag_agent"
    state["intent"] = "consulta_rag"

    result = knowledge_team_supervisor_node(
        state
    )

    assert result["next_node"] == (
        "rag_agent"
    )


def test_knowledge_team_infers_rag_agent():
    state = _base_state()
    state["next_node"] = ""
    state["intent"] = "consulta_rag"

    result = knowledge_team_supervisor_node(
        state
    )

    assert result["next_node"] == (
        "rag_agent"
    )


def test_knowledge_team_defaults_to_education():
    state = _base_state()
    state["next_node"] = ""
    state["intent"] = ""

    result = knowledge_team_supervisor_node(
        state
    )

    assert result["next_node"] == (
        "education_agent"
    )

    assert result[
        "team_route_source"
    ] == "team_default"


def test_support_team_selects_fallback():
    state = _base_state()
    state["next_node"] = "fallback_agent"
    state["intent"] = "desconhecido"

    result = support_team_supervisor_node(
        state
    )

    assert result["next_node"] == (
        "fallback_agent"
    )

    assert result["current_team"] == (
        "support_team"
    )


def test_support_team_defaults_to_fallback():
    state = _base_state()
    state["next_node"] = ""
    state["intent"] = ""

    result = support_team_supervisor_node(
        state
    )

    assert result["next_node"] == (
        "fallback_agent"
    )


def test_cross_team_request_is_escalated():
    state = _base_state()
    state["next_node"] = "rag_agent"

    result = financial_team_supervisor_node(
        state
    )

    assert result["next_node"] == (
        "supervisor"
    )

    assert result[
        "team_requires_root_supervisor"
    ] is True

    assert result[
        "team_route_source"
    ] == "root_escalation"


def test_unknown_agent_is_escalated():
    state = _base_state()
    state["next_node"] = "unknown_agent"

    result = financial_team_supervisor_node(
        state
    )

    assert result["next_node"] == (
        "supervisor"
    )

    assert result[
        "team_requires_root_supervisor"
    ] is True


def test_team_requested_agent_has_priority():
    state = _base_state()

    state["next_node"] = "financial_agent"
    state["team_requested_agent"] = (
        "report_agent"
    )

    result = financial_team_supervisor_node(
        state
    )

    assert result["next_node"] == (
        "report_agent"
    )


def test_decision_is_recorded_in_history():
    state = _base_state()

    result = financial_team_supervisor_node(
        state
    )

    history = result[
        "team_route_history"
    ]

    assert len(history) == 1

    assert history[0][
        "team_name"
    ] == "financial_team"

    assert history[0][
        "selected_agent"
    ] == "financial_agent"


def test_existing_history_is_preserved():
    state = _base_state()

    state["team_route_history"] = [
        {
            "team_name": "previous_team",
            "next_node": "previous_agent",
        }
    ]

    result = financial_team_supervisor_node(
        state
    )

    assert len(
        result["team_route_history"]
    ) == 2


def test_decision_is_recorded_in_structured_response():
    result = financial_team_supervisor_node(
        _base_state()
    )

    decisions = result[
        "structured_response"
    ]["team_supervisor_decisions"]

    assert "financial_team" in decisions

    assert decisions[
        "financial_team"
    ]["next_node"] == "financial_agent"


def test_trace_contains_team_supervisor_event():
    result = financial_team_supervisor_node(
        _base_state()
    )

    assert result["trace"][-1] == (
        "team_supervisor:"
        "financial_team:"
        "selected:"
        "financial_agent"
    )


def test_supervisor_does_not_mutate_input_state():
    state = _base_state()
    original = copy.deepcopy(
        state
    )

    financial_team_supervisor_node(
        state
    )

    assert state == original


def test_invalid_team_raises_error():
    with pytest.raises(
        TeamHierarchyError,
        match="Equipe não registrada",
    ):
        resolve_team_supervisor_decision(
            team_name=(
                "unknown_team"
            ),  # type: ignore[arg-type]
            state=_base_state(),
        )


def test_decision_model_dump_is_serializable():
    decision = (
        resolve_team_supervisor_decision(
            team_name="financial_team",
            state=_base_state(),
        )
    )

    payload = decision.model_dump()

    assert isinstance(payload, dict)
    assert payload["status"] == "selected"
    assert payload["reason"]


def test_team_supervisor_mapping_is_complete():
    assert set(
        TEAM_SUPERVISOR_NODES
    ) == {
        "financial_team_supervisor",
        "knowledge_team_supervisor",
        "support_team_supervisor",
    }


def test_all_team_supervisor_mapping_values_are_callable():
    assert all(
        callable(node)
        for node
        in TEAM_SUPERVISOR_NODES.values()
    )
