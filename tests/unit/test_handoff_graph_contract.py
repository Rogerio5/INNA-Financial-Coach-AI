from __future__ import annotations

from langgraph.graph import END

from src.agents.graph import (
    ALLOWED_AGENT_ROUTES,
    _selecionar_rota_apos_handoff,
    criar_builder_inna,
)


def _edge_pairs(builder) -> set[tuple[str, str]]:
    pairs: set[tuple[str, str]] = set()

    for edge in builder.edges:
        if (
            isinstance(edge, tuple)
            and len(edge) >= 2
        ):
            source = edge[0]
            target = edge[1]
        else:
            source = getattr(
                edge,
                "source",
                None,
            )
            target = getattr(
                edge,
                "target",
                None,
            )

        if source is not None and target is not None:
            pairs.add(
                (
                    str(source),
                    str(target),
                )
            )

    return pairs


def test_handoff_coordinator_is_registered():
    builder = criar_builder_inna()

    assert (
        "handoff_coordinator"
        in builder.nodes
    )


def test_agents_still_route_to_task_completion():
    builder = criar_builder_inna()
    edges = _edge_pairs(builder)

    for agent in ALLOWED_AGENT_ROUTES:
        assert (
            agent,
            "task_completion",
        ) in edges


def test_task_completion_routes_to_handoff_coordinator():
    builder = criar_builder_inna()
    edges = _edge_pairs(builder)

    assert (
        "task_completion",
        "handoff_coordinator",
    ) in edges


def test_task_completion_no_longer_skips_coordinator():
    builder = criar_builder_inna()
    edges = _edge_pairs(builder)

    assert (
        "task_completion",
        "conversation_summary",
    ) not in edges

    assert (
        "task_completion",
        END,
    ) not in edges


def test_no_handoff_routes_to_summary():
    assert _selecionar_rota_apos_handoff(
        {}
    ) == "conversation_summary"


def test_requested_handoff_routes_to_target():
    result = _selecionar_rota_apos_handoff({
        "handoff_current": {
            "status": "requested",
            "to_agent": "report_agent",
        }
    })

    assert result == "report_agent"


def test_terminal_handoff_routes_to_summary():
    for status in (
        "completed",
        "failed",
        "rejected",
        "cancelled",
    ):
        result = _selecionar_rota_apos_handoff({
            "handoff_current": {
                "status": status,
                "to_agent": "report_agent",
            }
        })

        assert result == "conversation_summary"


def test_invalid_target_routes_to_summary():
    result = _selecionar_rota_apos_handoff({
        "handoff_current": {
            "status": "requested",
            "to_agent": "unknown_agent",
        }
    })

    assert result == "conversation_summary"
