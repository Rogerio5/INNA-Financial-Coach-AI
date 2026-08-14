from __future__ import annotations

from src.agents.supervisor_mesh_node import (
    infer_supervisor_mesh_teams,
    supervisor_mesh_node,
)


def test_database_and_rag_activate_financial_knowledge_mesh():
    state = {
        "adaptive_multi_domain": True,
        "adaptive_target_agent": "financial_agent",
        "adaptive_budget": {
            "max_supervisors": 3,
        },
        "use_database": True,
        "use_rag": True,
        "trace": [],
    }

    result = supervisor_mesh_node(
        state
    )

    assert (
        result["supervisor_mesh_active"]
        is True
    )

    assert result[
        "supervisor_mesh_requested_teams"
    ] == [
        "financial_team",
        "knowledge_team",
    ]

    assert result[
        "supervisor_mesh_supervisors"
    ] == [
        "financial_team_supervisor",
        "knowledge_team_supervisor",
    ]


def test_single_domain_keeps_mesh_inactive():
    result = supervisor_mesh_node(
        {
            "adaptive_multi_domain": False,
            "adaptive_target_agent": (
                "financial_agent"
            ),
            "adaptive_budget": {
                "max_supervisors": 1,
            },
            "use_database": True,
            "trace": [],
        }
    )

    assert (
        result["supervisor_mesh_active"]
        is False
    )
    assert (
        result["supervisor_mesh_status"]
        == "inactive"
    )


def test_multi_domain_without_second_team_fails_closed():
    result = supervisor_mesh_node(
        {
            "adaptive_multi_domain": True,
            "adaptive_target_agent": (
                "financial_agent"
            ),
            "adaptive_budget": {
                "max_supervisors": 3,
            },
            "trace": [],
        }
    )

    assert (
        result["supervisor_mesh_active"]
        is False
    )
    assert (
        result["supervisor_mesh_status"]
        == "blocked"
    )
    assert (
        result["supervisor_mesh_plan"][
            "reason"
        ]
        == "supervisor_mesh_participants_unresolved"
    )


def test_mesh_respects_adaptive_supervisor_budget():
    result = supervisor_mesh_node(
        {
            "adaptive_multi_domain": True,
            "adaptive_target_agent": (
                "financial_agent"
            ),
            "adaptive_budget": {
                "max_supervisors": 1,
            },
            "use_database": True,
            "use_rag": True,
            "trace": [],
        }
    )

    assert (
        result["supervisor_mesh_active"]
        is False
    )
    assert (
        result["supervisor_mesh_status"]
        == "blocked"
    )


def test_requested_handoff_adds_target_team():
    teams = infer_supervisor_mesh_teams(
        {
            "current_team": (
                "financial_team"
            ),
            "handoff_current": {
                "status": "requested",
                "to_agent": "rag_agent",
            },
        }
    )

    assert teams == (
        "financial_team",
        "knowledge_team",
    )


def test_mesh_history_contains_only_governance_metadata():
    result = supervisor_mesh_node(
        {
            "adaptive_multi_domain": True,
            "adaptive_target_agent": (
                "financial_agent"
            ),
            "adaptive_budget": {
                "max_supervisors": 3,
            },
            "use_database": True,
            "use_rag": True,
            "supervisor_mesh_history": [],
            "trace": [],
            "user_message": (
                "conteudo privado que nao deve "
                "entrar no historico do mesh"
            ),
        }
    )

    history = result[
        "supervisor_mesh_history"
    ]

    assert len(history) == 1

    serialized = str(
        history
    )

    assert (
        "conteudo privado"
        not in serialized
    )


def test_mesh_trace_is_deterministic():
    result = supervisor_mesh_node(
        {
            "adaptive_multi_domain": True,
            "adaptive_target_agent": (
                "financial_agent"
            ),
            "adaptive_budget": {
                "max_supervisors": 3,
            },
            "use_database": True,
            "use_rag": True,
            "trace": [
                "before",
            ],
        }
    )

    assert result["trace"][0] == "before"
    assert result["trace"][-1] == (
        "supervisor_mesh:"
        "planned:"
        "financial_team:"
        "2"
    )
