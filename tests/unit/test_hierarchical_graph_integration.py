from __future__ import annotations

from src.agents.graph import (
    _selecionar_rota_apos_handoff,
    _selecionar_saida_supervisor_equipe,
    criar_builder_inna,
)


def _edge_pairs(
    builder,
) -> set[tuple[str, str]]:
    pairs: set[tuple[str, str]] = set()

    for edge in builder.edges:
        if isinstance(
            edge,
            tuple,
        ):
            source = edge[0]
            target = edge[1]
        else:
            source = edge.source
            target = edge.target

        pairs.add(
            (
                str(source),
                str(target),
            )
        )

    return pairs


def _branch_ends(
    builder,
    source: str,
) -> set[str]:
    branches = builder.branches[
        source
    ]

    ends: set[str] = set()

    for branch in branches.values():
        mapping = getattr(
            branch,
            "ends",
            {},
        )

        if mapping:
            ends.update(
                str(key)
                for key in mapping
            )

    return ends


def test_hierarchical_nodes_are_registered():
    builder = criar_builder_inna()

    required = {
        "team_router",
        "financial_team_supervisor",
        "knowledge_team_supervisor",
        "support_team_supervisor",
    }

    assert required.issubset(
        builder.nodes
    )


def test_supervisor_routes_to_adaptive_gateway():
    builder = criar_builder_inna()
    edges = _edge_pairs(
        builder
    )

    assert (
        "supervisor",
        "adaptive_gateway",
    ) in edges

    assert (
        "supervisor",
        "team_router",
    ) not in edges

    assert (
        "supervisor",
        "execution_governance",
    ) not in edges

    assert _branch_ends(
        builder,
        "adaptive_gateway",
    ) == {
        "execution_governance",
        "team_router",
    }


def test_team_router_reaches_all_team_supervisors():
    builder = criar_builder_inna()

    assert _branch_ends(
        builder,
        "team_router",
    ) == {
        "financial_team_supervisor",
        "knowledge_team_supervisor",
        "support_team_supervisor",
    }


def test_team_supervisors_can_reach_governance():
    builder = criar_builder_inna()

    for supervisor in (
        "financial_team_supervisor",
        "knowledge_team_supervisor",
        "support_team_supervisor",
    ):
        ends = _branch_ends(
            builder,
            supervisor,
        )

        assert (
            "execution_governance"
            in ends
        )


def test_team_supervisors_can_escalate_to_root():
    builder = criar_builder_inna()

    for supervisor in (
        "financial_team_supervisor",
        "knowledge_team_supervisor",
        "support_team_supervisor",
    ):
        ends = _branch_ends(
            builder,
            supervisor,
        )

        assert "supervisor" in ends
        assert "fallback_agent" in ends


def test_handoff_requested_returns_to_hierarchy():
    result = (
        _selecionar_rota_apos_handoff({
            "handoff_current": {
                "status": "requested",
                "to_agent": "report_agent",
            }
        })
    )

    assert result == "team_router"


def test_handoff_terminal_goes_to_summary():
    result = (
        _selecionar_rota_apos_handoff({
            "handoff_current": {
                "status": "completed",
                "to_agent": "report_agent",
            }
        })
    )

    assert result == (
        "conversation_summary"
    )


def test_normal_team_decision_goes_to_governance():
    result = (
        _selecionar_saida_supervisor_equipe({
            "team_requires_root_supervisor": False,
        })
    )

    assert result == (
        "execution_governance"
    )


def test_cross_team_decision_returns_to_root():
    result = (
        _selecionar_saida_supervisor_equipe({
            "team_requires_root_supervisor": True,
            "root_supervisor_visits": 1,
            "max_root_supervisor_visits": 3,
        })
    )

    assert result == "supervisor"


def test_root_visit_limit_uses_fallback():
    result = (
        _selecionar_saida_supervisor_equipe({
            "team_requires_root_supervisor": True,
            "root_supervisor_visits": 3,
            "max_root_supervisor_visits": 3,
        })
    )

    assert result == (
        "fallback_agent"
    )


def test_agents_still_use_task_completion():
    builder = criar_builder_inna()
    edges = _edge_pairs(builder)

    for agent in (
        "financial_agent",
        "education_agent",
        "rag_agent",
        "report_agent",
        "fallback_agent",
    ):
        assert (
            agent,
            "task_completion",
        ) in edges


def test_summary_remains_the_only_static_end():
    edges = _edge_pairs(
        criar_builder_inna()
    )

    assert (
        "conversation_summary",
        "__end__",
    ) in edges
