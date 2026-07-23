from __future__ import annotations

from langgraph.graph import END

from src.agents.graph import (
    ALLOWED_AGENT_ROUTES,
    criar_builder_inna,
)


def _edge_pairs(
    builder,
) -> set[tuple[str, str]]:
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

        if (
            source is None
            or target is None
        ):
            continue

        pairs.add(
            (
                str(source),
                str(target),
            )
        )

    return pairs


def test_task_completion_node_is_registered():
    builder = criar_builder_inna()

    assert (
        "task_completion"
        in builder.nodes
    )


def test_all_agents_route_to_task_completion():
    builder = criar_builder_inna()
    edges = _edge_pairs(builder)

    for agent in ALLOWED_AGENT_ROUTES:
        assert (
            agent,
            "task_completion",
        ) in edges


def test_agents_do_not_skip_task_completion():
    builder = criar_builder_inna()
    edges = _edge_pairs(builder)

    for agent in ALLOWED_AGENT_ROUTES:
        assert (
            agent,
            "conversation_summary",
        ) not in edges

        assert (
            agent,
            END,
        ) not in edges


def test_task_completion_routes_to_human_review_policy():
    builder = criar_builder_inna()
    edges = _edge_pairs(builder)

    assert (
        "task_completion",
        "human_review_policy",
    ) in edges


def test_task_completion_does_not_bypass_review_policy():
    builder = criar_builder_inna()
    edges = _edge_pairs(builder)

    assert (
        "task_completion",
        "handoff_coordinator",
    ) not in edges

    assert (
        "task_completion",
        "conversation_summary",
    ) not in edges


def test_task_completion_does_not_finish_directly():
    builder = criar_builder_inna()
    edges = _edge_pairs(builder)

    assert (
        "task_completion",
        END,
    ) not in edges


def test_summary_remains_final_node():
    builder = criar_builder_inna()
    edges = _edge_pairs(builder)

    assert (
        "conversation_summary",
        END,
    ) in edges
