from __future__ import annotations

from src.agents.agent_registry import (
    AgentDefinition,
    AgentRegistry,
)
from src.agents.blackboard_permissions import (
    evaluate_blackboard_publish,
    evaluate_blackboard_read,
)
from src.agents.shared_blackboard import (
    BlackboardEntry,
)


def _entry(
    *,
    visibility="workflow",
    team=None,
):
    return BlackboardEntry(
        schema_version="1.0.0",
        entry_id="bb_test",
        kind="result",
        producer="financial_agent",
        visibility=visibility,
        team=team,
        payload={
            "status": "completed",
        },
    )


def test_financial_agent_can_publish_result_workflow():
    decision = evaluate_blackboard_publish(
        principal="financial_agent",
        kind="result",
        visibility="workflow",
        team=None,
    )

    assert decision.allowed is True


def test_financial_agent_can_publish_to_own_team():
    decision = evaluate_blackboard_publish(
        principal="financial_agent",
        kind="evidence",
        visibility="team",
        team="financial_team",
    )

    assert decision.allowed is True


def test_financial_agent_cannot_publish_to_other_team():
    decision = evaluate_blackboard_publish(
        principal="financial_agent",
        kind="result",
        visibility="team",
        team="knowledge_team",
    )

    assert decision.allowed is False
    assert (
        decision.reason
        == "blackboard_cross_team_publish_denied"
    )


def test_agent_cannot_publish_supervisor_decision():
    decision = evaluate_blackboard_publish(
        principal="financial_agent",
        kind="decision",
        visibility="workflow",
        team=None,
    )

    assert decision.allowed is False


def test_report_agent_has_restricted_kinds():
    decision = evaluate_blackboard_publish(
        principal="report_agent",
        kind="fact",
        visibility="workflow",
        team=None,
    )

    assert decision.allowed is False


def test_rag_agent_can_publish_evidence():
    decision = evaluate_blackboard_publish(
        principal="rag_agent",
        kind="evidence",
        visibility="workflow",
        team=None,
    )

    assert decision.allowed is True


def test_research_agent_can_publish_workflow_result():
    decision = evaluate_blackboard_publish(
        principal="research_agent",
        kind="result",
        visibility="workflow",
        team=None,
    )

    assert decision.allowed is True


def test_research_agent_cannot_publish_team_entry():
    decision = evaluate_blackboard_publish(
        principal="research_agent",
        kind="result",
        visibility="team",
        team="knowledge_team",
    )

    assert decision.allowed is False


def test_fallback_can_publish_support_team_result():
    decision = evaluate_blackboard_publish(
        principal="fallback_agent",
        kind="result",
        visibility="team",
        team="support_team",
    )

    assert decision.allowed is True


def test_fallback_cannot_publish_workflow():
    decision = evaluate_blackboard_publish(
        principal="fallback_agent",
        kind="result",
        visibility="workflow",
        team=None,
    )

    assert decision.allowed is False


def test_team_supervisor_can_publish_decision():
    decision = evaluate_blackboard_publish(
        principal="financial_team_supervisor",
        kind="decision",
        visibility="workflow",
        team=None,
    )

    assert decision.allowed is True
    assert (
        decision.principal_type
        == "team_supervisor"
    )


def test_supervisor_cannot_publish_agent_result():
    decision = evaluate_blackboard_publish(
        principal="financial_team_supervisor",
        kind="result",
        visibility="workflow",
        team=None,
    )

    assert decision.allowed is False


def test_supervisor_team_publish_is_scoped():
    decision = evaluate_blackboard_publish(
        principal="financial_team_supervisor",
        kind="decision",
        visibility="team",
        team="knowledge_team",
    )

    assert decision.allowed is False


def test_communication_service_identity_is_denied_publish():
    decision = evaluate_blackboard_publish(
        principal="communication_agent",
        kind="result",
        visibility="workflow",
        team=None,
    )

    assert decision.allowed is False
    assert (
        decision.reason
        == "blackboard_service_identity_denied"
    )


def test_communication_service_identity_is_denied_read():
    decision = evaluate_blackboard_read(
        principal="communication_agent",
        entry=_entry(),
    )

    assert decision.allowed is False


def test_financial_agent_reads_workflow_entry():
    decision = evaluate_blackboard_read(
        principal="financial_agent",
        entry=_entry(),
    )

    assert decision.allowed is True


def test_financial_agent_reads_own_team_entry():
    decision = evaluate_blackboard_read(
        principal="financial_agent",
        entry=_entry(
            visibility="team",
            team="financial_team",
        ),
    )

    assert decision.allowed is True


def test_financial_agent_cannot_read_knowledge_team_entry():
    decision = evaluate_blackboard_read(
        principal="financial_agent",
        entry=_entry(
            visibility="team",
            team="knowledge_team",
        ),
    )

    assert decision.allowed is False


def test_knowledge_supervisor_reads_workflow_entry():
    decision = evaluate_blackboard_read(
        principal="knowledge_team_supervisor",
        entry=_entry(),
    )

    assert decision.allowed is True


def test_knowledge_supervisor_reads_own_team_entry():
    decision = evaluate_blackboard_read(
        principal="knowledge_team_supervisor",
        entry=_entry(
            visibility="team",
            team="knowledge_team",
        ),
    )

    assert decision.allowed is True


def test_research_agent_reads_workflow_only():
    workflow = evaluate_blackboard_read(
        principal="research_agent",
        entry=_entry(),
    )

    team = evaluate_blackboard_read(
        principal="research_agent",
        entry=_entry(
            visibility="team",
            team="knowledge_team",
        ),
    )

    assert workflow.allowed is True
    assert team.allowed is False


def test_fallback_has_minimum_read_scope():
    own_team = evaluate_blackboard_read(
        principal="fallback_agent",
        entry=_entry(
            visibility="team",
            team="support_team",
        ),
    )

    workflow = evaluate_blackboard_read(
        principal="fallback_agent",
        entry=_entry(),
    )

    assert own_team.allowed is True
    assert workflow.allowed is False


def test_unknown_principal_is_denied():
    decision = evaluate_blackboard_read(
        principal="unknown_agent",
        entry=_entry(),
    )

    assert decision.allowed is False
    assert (
        decision.reason
        == "blackboard_unknown_principal"
    )


def test_inactive_registered_agent_is_denied():
    registry = AgentRegistry()

    registry.register(
        AgentDefinition(
            agent_id="inactive_agent",
            description="Inactive test principal.",
            status="inactive",
        )
    )

    decision = evaluate_blackboard_publish(
        principal="inactive_agent",
        kind="result",
        visibility="workflow",
        team=None,
        registry=registry,
    )

    assert decision.allowed is False
    assert (
        decision.reason
        == "blackboard_inactive_principal"
    )
