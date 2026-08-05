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
        if isinstance(edge, tuple):
            assert len(edge) >= 2, f"Aresta inválida: {edge!r}"

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


def test_langgraph_has_expected_linear_entry_flow():
    builder = criar_builder_inna()

    edges = _edge_pairs(builder)

    assert (
        "__start__",
        "context_builder",
    ) in edges

    assert (
        "context_builder",
        "supervisor",
    ) in edges


def test_all_specialized_agents_finish_through_finalization_pipeline():
    builder = criar_builder_inna()

    edges = _edge_pairs(builder)

    for agent in ALLOWED_AGENT_ROUTES:
        assert (
            agent,
            "task_completion",
        ) in edges

        assert (
            agent,
            "conversation_summary",
        ) not in edges

    assert (
        "task_completion",
        "human_review_policy",
    ) in edges

    assert (
        "task_completion",
        "handoff_coordinator",
    ) not in edges

    assert (
        "conversation_summary",
        "__end__",
    ) in edges


def test_agents_do_not_return_to_supervisor():
    builder = criar_builder_inna()

    edges = _edge_pairs(builder)

    for agent in ALLOWED_AGENT_ROUTES:
        assert (
            agent,
            "supervisor",
        ) not in edges


def test_agents_do_not_transition_between_each_other():
    builder = criar_builder_inna()

    edges = _edge_pairs(builder)

    for source in ALLOWED_AGENT_ROUTES:
        for target in ALLOWED_AGENT_ROUTES:
            assert (
                source,
                target,
            ) not in edges


def test_current_graph_topology_is_acyclic_by_design():
    builder = criar_builder_inna()

    edges = _edge_pairs(builder)

    adjacency: dict[str, set[str]] = {}

    for source, target in edges:
        adjacency.setdefault(
            source,
            set(),
        ).add(target)

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str) -> None:
        if node in visiting:
            raise AssertionError(f"Ciclo detectado em {node}")

        if node in visited:
            return

        visiting.add(node)

        for target in adjacency.get(
            node,
            set(),
        ):
            visit(target)

        visiting.remove(node)
        visited.add(node)

    for node in adjacency:
        visit(node)
