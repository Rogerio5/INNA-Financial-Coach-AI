from __future__ import annotations

import pytest

from src.agents.team_hierarchy import (
    DEFAULT_TEAM_REGISTRY,
    FINANCIAL_TEAM,
    KNOWLEDGE_TEAM,
    SUPPORT_TEAM,
    TeamDefinition,
    TeamHierarchyError,
    TeamRegistry,
)


def test_default_registry_contains_three_teams():
    assert DEFAULT_TEAM_REGISTRY.team_names == (
        "financial_team",
        "knowledge_team",
        "support_team",
    )


def test_default_registry_contains_all_agents():
    assert set(
        DEFAULT_TEAM_REGISTRY.agents
    ) == {
        "financial_agent",
        "report_agent",
        "education_agent",
        "rag_agent",
        "fallback_agent",
    }


def test_financial_team_members():
    assert FINANCIAL_TEAM.members == (
        "financial_agent",
        "report_agent",
    )


def test_knowledge_team_members():
    assert KNOWLEDGE_TEAM.members == (
        "education_agent",
        "rag_agent",
    )


def test_support_team_members():
    assert SUPPORT_TEAM.members == (
        "fallback_agent",
    )


def test_resolves_team_for_financial_agent():
    team = (
        DEFAULT_TEAM_REGISTRY
        .team_for_agent(
            "financial_agent"
        )
    )

    assert team.name == "financial_team"


def test_resolves_team_for_report_agent():
    team = (
        DEFAULT_TEAM_REGISTRY
        .team_for_agent(
            "report_agent"
        )
    )

    assert team.name == "financial_team"


def test_resolves_team_for_rag_agent():
    team = (
        DEFAULT_TEAM_REGISTRY
        .team_for_agent(
            "rag_agent"
        )
    )

    assert team.name == "knowledge_team"


def test_resolves_team_supervisor():
    supervisor = (
        DEFAULT_TEAM_REGISTRY
        .supervisor_for_agent(
            "education_agent"
        )
    )

    assert supervisor == (
        "knowledge_team_supervisor"
    )


def test_membership_check():
    assert (
        DEFAULT_TEAM_REGISTRY.is_member(
            agent="report_agent",
            team_name="financial_team",
        )
        is True
    )

    assert (
        DEFAULT_TEAM_REGISTRY.is_member(
            agent="rag_agent",
            team_name="financial_team",
        )
        is False
    )


def test_internal_financial_transfer_is_allowed():
    decision = (
        DEFAULT_TEAM_REGISTRY
        .evaluate_transfer(
            from_agent="financial_agent",
            to_agent="report_agent",
        )
    )

    assert decision.allowed is True
    assert decision.same_team is True

    assert (
        decision.requires_root_supervisor
        is False
    )

    assert decision.source_team == (
        "financial_team"
    )

    assert decision.target_team == (
        "financial_team"
    )


def test_internal_knowledge_transfer_is_allowed():
    decision = (
        DEFAULT_TEAM_REGISTRY
        .evaluate_transfer(
            from_agent="education_agent",
            to_agent="rag_agent",
        )
    )

    assert decision.allowed is True
    assert decision.same_team is True


def test_cross_team_transfer_requires_root_supervisor():
    decision = (
        DEFAULT_TEAM_REGISTRY
        .evaluate_transfer(
            from_agent="financial_agent",
            to_agent="rag_agent",
        )
    )

    assert decision.allowed is False
    assert decision.same_team is False

    assert (
        decision.requires_root_supervisor
        is True
    )

    assert decision.source_team == (
        "financial_team"
    )

    assert decision.target_team == (
        "knowledge_team"
    )


def test_unknown_team_raises_error():
    with pytest.raises(
        TeamHierarchyError,
        match="Equipe não registrada",
    ):
        DEFAULT_TEAM_REGISTRY.get_team(
            "unknown_team"  # type: ignore[arg-type]
        )


def test_unknown_agent_raises_error():
    with pytest.raises(
        TeamHierarchyError,
        match="Agente não associado",
    ):
        DEFAULT_TEAM_REGISTRY.team_for_agent(
            "unknown_agent"  # type: ignore[arg-type]
        )


def test_team_requires_members():
    with pytest.raises(
        TeamHierarchyError,
        match="ao menos um membro",
    ):
        TeamDefinition(
            name="financial_team",
            supervisor_node=(
                "financial_team_supervisor"
            ),
            members=(),
            description="Equipe inválida.",
        )


def test_team_rejects_duplicate_members():
    with pytest.raises(
        TeamHierarchyError,
        match="membros duplicados",
    ):
        TeamDefinition(
            name="financial_team",
            supervisor_node=(
                "financial_team_supervisor"
            ),
            members=(
                "financial_agent",
                "financial_agent",
            ),
            description="Equipe inválida.",
        )


def test_team_requires_description():
    with pytest.raises(
        TeamHierarchyError,
        match="descrição",
    ):
        TeamDefinition(
            name="financial_team",
            supervisor_node=(
                "financial_team_supervisor"
            ),
            members=(
                "financial_agent",
            ),
            description="   ",
        )


def test_internal_handoff_limit_must_be_positive():
    with pytest.raises(
        TeamHierarchyError,
        match="maior ou igual a 1",
    ):
        TeamDefinition(
            name="support_team",
            supervisor_node=(
                "support_team_supervisor"
            ),
            members=(
                "fallback_agent",
            ),
            description="Equipe de suporte.",
            max_internal_handoffs=0,
        )


def test_registry_rejects_duplicate_team_names():
    with pytest.raises(
        TeamHierarchyError,
        match="equipes duplicados",
    ):
        TeamRegistry(
            (
                FINANCIAL_TEAM,
                FINANCIAL_TEAM,
            )
        )


def test_registry_rejects_duplicate_supervisors():
    duplicate_supervisor_team = (
        TeamDefinition(
            name="knowledge_team",
            supervisor_node=(
                "financial_team_supervisor"
            ),
            members=(
                "education_agent",
            ),
            description="Equipe inválida.",
        )
    )

    with pytest.raises(
        TeamHierarchyError,
        match="supervisores",
    ):
        TeamRegistry(
            (
                FINANCIAL_TEAM,
                duplicate_supervisor_team,
            )
        )


def test_agent_cannot_belong_to_multiple_teams():
    overlapping_team = TeamDefinition(
        name="knowledge_team",
        supervisor_node=(
            "knowledge_team_supervisor"
        ),
        members=(
            "financial_agent",
            "rag_agent",
        ),
        description="Equipe sobreposta.",
    )

    with pytest.raises(
        TeamHierarchyError,
        match="mais de uma equipe",
    ):
        TeamRegistry(
            (
                FINANCIAL_TEAM,
                overlapping_team,
            )
        )


def test_registry_requires_at_least_one_team():
    with pytest.raises(
        TeamHierarchyError,
        match="possuir equipes",
    ):
        TeamRegistry(())
