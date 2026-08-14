from __future__ import annotations

from src.agents.graph import (
    _selecionar_saida_adaptive_gateway,
)
from src.agents.supervisor_mesh_node import (
    select_supervisor_mesh_route,
    supervisor_mesh_node,
)


def test_simple_route_preserves_fast_path():
    state = {
        "adaptive_route_type": "simple",
        "next_node": "financial_agent",
    }

    assert (
        _selecionar_saida_adaptive_gateway(
            state  # type: ignore[arg-type]
        )
        == "execution_governance"
    )


def test_complex_route_enters_supervisor_mesh():
    state = {
        "adaptive_route_type": "complex",
        "next_node": "financial_agent",
    }

    assert (
        _selecionar_saida_adaptive_gateway(
            state  # type: ignore[arg-type]
        )
        == "supervisor_mesh"
    )


def test_database_and_rag_infer_multi_domain_without_flag():
    result = supervisor_mesh_node(
        {
            "adaptive_multi_domain": False,
            "adaptive_target_agent": (
                "financial_agent"
            ),
            "adaptive_budget": {
                "max_supervisors": 3,
            },
            "use_database": True,
            "use_rag": True,
            "trace": [],
        }
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


def test_planned_mesh_continues_to_team_router():
    assert (
        select_supervisor_mesh_route(
            {
                "supervisor_mesh_status": (
                    "planned"
                )
            }
        )
        == "team_router"
    )


def test_inactive_mesh_continues_to_team_router():
    assert (
        select_supervisor_mesh_route(
            {
                "supervisor_mesh_status": (
                    "inactive"
                )
            }
        )
        == "team_router"
    )


def test_blocked_mesh_fails_closed_to_governance():
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
        result["supervisor_mesh_status"]
        == "blocked"
    )

    assert (
        result["next_node"]
        == "fallback_agent"
    )

    assert (
        select_supervisor_mesh_route(
            result
        )
        == "execution_governance"
    )
